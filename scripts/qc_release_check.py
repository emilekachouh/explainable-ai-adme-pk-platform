"""Release quality-control checker for the Caco-2 Permeability Screening + PK Education Platform.

Run:
    python scripts/qc_release_check.py

Saves a markdown report to reports/release_qc_report.md.
Exits with code 1 if any check fails.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "release_qc_report.md"

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check(label: str, result: bool, note: str = "") -> tuple[str, str, str]:
    status = PASS if result else FAIL
    return (status, label, note)


def _warn(label: str, note: str = "") -> tuple[str, str, str]:
    return (WARN, label, note)


# ---------------------------------------------------------------------------
# 1. Required files
# ---------------------------------------------------------------------------

def check_required_files() -> list[tuple[str, str, str]]:
    required = [
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "CITATION.cff",
        "SECURITY.md",
        "CHANGELOG.md",
        "requirements.txt",
        "app/streamlit_app.py",
        "docs/model_card.md",
        "docs/data_card.md",
        "docs/methods.md",
        "docs/screenshots/README.md",
        "src/adme_predictor/__init__.py",
        "tests/conftest.py",
        "pytest.ini",
    ]
    results = []
    for f in required:
        path = ROOT / f
        results.append(_check(f"File exists: {f}", path.exists()))
    return results


# ---------------------------------------------------------------------------
# 2. Unsafe phrase scan (string literals in .py; text in .md)
# ---------------------------------------------------------------------------

BANNED_PHRASES_PY: list[tuple[str, str]] = [
    # (phrase, description)
    ("predicted F", "implies ML model predicts bioavailability F"),
    ("predicted bioavailability", "implies model predicts human bioavailability"),
    ("predicts human PK", "overclaims validated human PK prediction"),
    ("human PK predictor", "overclaims validated human PK prediction"),
    ("validated PK prediction", "implies regulated/clinical validation"),
    ("clinical prediction", "implies clinical use"),
    ("dose recommendation", "clinical claim"),
    ("safety prediction", "clinical claim"),
    ("efficacy prediction", "clinical claim"),
    ("regulatory decision", "regulatory claim"),
]

SAFE_CONTEXTS_PY = [
    "does not predict",
    "does NOT predict",
    "not predict",
    "NOT predict",
    "illustrative",
    "not measured",
    "educational",
    "scenario",
    "assumption",
]

SHAP_LIVE_CLAIMS: list[str] = [
    "SHAP values computed",
    "computing SHAP",
    "live SHAP",
    "SHAP is running",
]

BANNED_MD: list[tuple[str, str]] = [
    ("predicted F", "overclaims"),
    ("predicted bioavailability", "overclaims"),
    ("validated human PK prediction", "overclaims"),
    ("clinical dose prediction", "overclaims"),
]

NEGATION_WORDS = [
    "does not", "not predict", "not a prediction", "illustrative", "NOT",
    "educational scenario", "would require", "requires", "not for",
    "cannot", "do not", "does not support", "not support",
    "not replace", "not make", "not claim",
    "does_not_support", "rather than", "prioritization rather",
    "early prioritization", "support rather",
]

# Markdown files excluded from the phrase scan (audit/documentation files intentionally
# discuss banned phrases in order to document that they are banned)
_MD_SCAN_EXCLUDED = {
    "reports/language_claims_audit.md",
    "reports/interview_pitch.md",
    "reports/release_qc_report.md",
    "reports/screenshot_qc_report.md",
    "docs/methods.md",
    "docs/open_source_release_checklist.md",
    "docs/screenshots/README.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
}


def _scan_py_literals(source: str, banned: list[tuple[str, str]]) -> list[str]:
    violations = []
    lines = source.splitlines()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["SyntaxError: could not parse file"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lower = node.value.lower()
            for phrase, desc in banned:
                if phrase.lower() in lower:
                    context = node.value[:100]
                    # Check negation in the string value itself
                    if any(neg.lower() in lower for neg in NEGATION_WORDS):
                        continue
                    # Check negation in surrounding source lines (±8 lines)
                    line_no = getattr(node, "lineno", 1) - 1
                    surrounding = "\n".join(lines[max(0, line_no - 8): line_no + 5]).lower()
                    if any(neg.lower() in surrounding for neg in NEGATION_WORDS):
                        continue
                    violations.append(f"  Phrase '{phrase}' in: {context!r}")
    return violations


def check_unsafe_phrases() -> list[tuple[str, str, str]]:
    results = []

    # Scan Python files
    py_files = list((ROOT / "app").rglob("*.py")) + list((ROOT / "src").rglob("*.py"))
    for py_path in py_files:
        source = py_path.read_text(encoding="utf-8", errors="replace")
        violations = _scan_py_literals(source, BANNED_PHRASES_PY)
        rel = py_path.relative_to(ROOT)
        results.append(_check(
            f"Unsafe phrase scan: {rel}",
            len(violations) == 0,
            "; ".join(violations[:3]) if violations else "",
        ))
        # Check for live SHAP claims
        shap_violations = [p for p in SHAP_LIVE_CLAIMS if p in source]
        if shap_violations:
            results.append(_warn(
                f"Live SHAP claim: {rel}",
                f"Found: {shap_violations}. Verify SHAP is not claimed as runtime inference.",
            ))

    # Scan Markdown files (looser scan on full text)
    md_files = list(ROOT.rglob("*.md"))
    excluded = {ROOT / f for f in _MD_SCAN_EXCLUDED}
    md_files = [f for f in md_files if ".venv" not in str(f) and ".git" not in str(f)
                and f not in excluded]
    all_violations: list[str] = []
    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase, desc in BANNED_MD:
            if phrase.lower() in text:
                # Check for negation context
                idx = text.find(phrase.lower())
                context = text[max(0, idx - 80): idx + 80]
                if not any(neg.lower() in context for neg in NEGATION_WORDS):
                    all_violations.append(f"{md_path.relative_to(ROOT)}: '{phrase}'")
    results.append(_check(
        "Unsafe phrases in Markdown docs",
        len(all_violations) == 0,
        "; ".join(all_violations[:5]),
    ))

    return results


# ---------------------------------------------------------------------------
# 3. Screenshots
# ---------------------------------------------------------------------------

REQUIRED_SCREENSHOTS = [
    "01_home_dashboard.png",
    "02_single_molecule_profile.png",
    "03_descriptor_based_interpretation.png",
    "04_batch_upload.png",
    "05_batch_results.png",
    "06_molecule_comparison.png",
    "07_multi_drug_pk_overlay.png",
    "08_absorption_sensitivity_simulator.png",
    "09_report_download.png",
    "10_model_credibility_limits.png",
]


def check_screenshots() -> list[tuple[str, str, str]]:
    results = []
    ss_dir = ROOT / "docs" / "screenshots"
    for fname in REQUIRED_SCREENSHOTS:
        p = ss_dir / fname
        results.append(_check(
            f"Screenshot exists: {fname}",
            p.exists(),
            f"Expected at {p.relative_to(ROOT)}" if not p.exists() else "",
        ))
    # Check README
    results.append(_check(
        "docs/screenshots/README.md exists",
        (ss_dir / "README.md").exists(),
    ))
    # Check sizes — any screenshot < 50 KB is suspicious (blank or broken)
    for fname in REQUIRED_SCREENSHOTS:
        p = ss_dir / fname
        if p.exists():
            size_kb = p.stat().st_size / 1024
            results.append(_check(
                f"Screenshot not blank: {fname}",
                size_kb >= 50,
                f"Size {size_kb:.0f} KB — may be blank or broken" if size_kb < 50 else "",
            ))
    return results


# ---------------------------------------------------------------------------
# 4. requirements.txt
# ---------------------------------------------------------------------------

def check_requirements() -> list[tuple[str, str, str]]:
    req = ROOT / "requirements.txt"
    if not req.exists():
        return [_check("requirements.txt exists", False)]
    lines = [l.strip().lower() for l in req.read_text().splitlines() if l.strip() and not l.startswith("#")]
    required_packages = ["streamlit", "pandas", "numpy", "rdkit", "scikit-learn", "xgboost", "joblib"]
    results = []
    for pkg in required_packages:
        found = any(pkg in line for line in lines)
        results.append(_check(f"requirements.txt contains: {pkg}", found))
    return results


# ---------------------------------------------------------------------------
# 5. Tests directory
# ---------------------------------------------------------------------------

def check_tests() -> list[tuple[str, str, str]]:
    tests_dir = ROOT / "tests"
    test_files = list(tests_dir.glob("test_*.py"))
    return [
        _check("tests/ directory exists", tests_dir.exists()),
        _check("At least 15 test files present", len(test_files) >= 15,
               f"Found {len(test_files)} test files"),
    ]


# ---------------------------------------------------------------------------
# 6. App import check
# ---------------------------------------------------------------------------

def check_app_syntax() -> list[tuple[str, str, str]]:
    app = ROOT / "app" / "streamlit_app.py"
    if not app.exists():
        return [_check("app/streamlit_app.py syntax", False, "File missing")]
    source = app.read_text(encoding="utf-8", errors="replace")
    try:
        ast.parse(source)
        return [_check("app/streamlit_app.py parses (no syntax error)", True)]
    except SyntaxError as exc:
        return [_check("app/streamlit_app.py parses (no syntax error)", False, str(exc))]


# ---------------------------------------------------------------------------
# 7. Molecule library count
# ---------------------------------------------------------------------------

def check_molecule_count() -> list[tuple[str, str, str]]:
    ex = ROOT / "src" / "adme_predictor" / "example_molecules.py"
    if not ex.exists():
        return [_check("example_molecules.py exists", False)]
    text = ex.read_text(encoding="utf-8", errors="replace")
    # Count "smiles" occurrences as a proxy for molecule definitions
    count = text.lower().count('"smiles"')
    return [_check(
        f"Molecule library count >= 200 ({count} found)",
        count >= 200,
        f"Found approximately {count} molecules; expected >= 200",
    )]


# ---------------------------------------------------------------------------
# 8. README title check
# ---------------------------------------------------------------------------

def check_readme_title() -> list[tuple[str, str, str]]:
    readme = ROOT / "README.md"
    if not readme.exists():
        return [_check("README.md title", False, "README missing")]
    text = readme.read_text(encoding="utf-8", errors="replace")
    results = []
    results.append(_check(
        "README title contains 'Caco-2'",
        "Caco-2" in text[:200],
        "Title may still use overclaiming name",
    ))
    results.append(_check(
        "README does not use 'AI-PBPK' title",
        "AI-PBPK" not in text[:200],
        "Found 'AI-PBPK' in README header area",
    ))
    results.append(_check(
        "README has LICENSE section",
        "MIT" in text or "License" in text,
    ))
    results.append(_check(
        "README has live app placeholder or URL",
        "streamlit" in text.lower() and ("demo" in text.lower() or "live" in text.lower()),
    ))
    return results


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_all() -> tuple[list[tuple[str, str, str]], int, int, int]:
    checks: list[tuple[str, str, str]] = []
    checks += check_required_files()
    checks += check_unsafe_phrases()
    checks += check_screenshots()
    checks += check_requirements()
    checks += check_tests()
    checks += check_app_syntax()
    checks += check_molecule_count()
    checks += check_readme_title()
    passed = sum(1 for s, _, _ in checks if s == PASS)
    failed = sum(1 for s, _, _ in checks if s == FAIL)
    warned = sum(1 for s, _, _ in checks if s == WARN)
    return checks, passed, failed, warned


def write_report(checks: list[tuple[str, str, str]], passed: int, failed: int, warned: int) -> None:
    lines = [
        "# Release QC Report",
        "",
        f"Generated: by `scripts/qc_release_check.py`",
        "",
        f"**Result: {'PASS' if failed == 0 else 'FAIL'}**  ",
        f"Passed: {passed} | Failed: {failed} | Warnings: {warned} | Total: {len(checks)}",
        "",
        "## Check Results",
        "",
        "| Status | Check | Notes |",
        "|---|---|---|",
    ]
    for status, label, note in checks:
        icon = "[OK]" if status == PASS else ("[WN]" if status == WARN else "[!!]")
        lines.append(f"| {icon} {status} | {label} | {note} |")
    lines.extend(["", "---", "Run `python scripts/qc_release_check.py` to regenerate.", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    checks, passed, failed, warned = run_all()
    write_report(checks, passed, failed, warned)

    for status, label, note in checks:
        icon = "[OK]" if status == PASS else ("[WN]" if status == WARN else "[!!]")
        suffix = f" — {note}" if note else ""
        print(f"{icon} {label}{suffix}")

    print(f"\nResult: {'PASS' if failed == 0 else 'FAIL'} ({passed} passed, {failed} failed, {warned} warnings)")
    print(f"Full report saved to: {REPORT_PATH.relative_to(ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
