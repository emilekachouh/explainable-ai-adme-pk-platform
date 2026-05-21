"""Capture fresh review screenshots for the Streamlit app.

Navigation structure (post batch-screening + explainability-labeling fixes):
  Sidebar pages: Single Molecule | Batch Screening | Molecule Comparison |
                 Multi-Drug PK | PK/NCA Simulator | Evidence & Limits
  Single Molecule tabs: Descriptors | Permeability | Confidence |
                        Applicability Domain | Descriptor Interpretation |
                        Absorption Sensitivity | Limits
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import Page, TimeoutError, sync_playwright


BASE_URL = "http://127.0.0.1:8507"
OUTPUT_DIR = Path("docs") / "screenshots"

SCREENSHOT_ROWS = [
    (
        "01_home_dashboard.png",
        "Home dashboard",
        "App title, workflow strip, metric cards, and scientific boundary notice.",
        "GitHub README, recruiter demo",
    ),
    (
        "02_single_molecule_profile.png",
        "Single molecule profile",
        "Aspirin SVG structure, canonical SMILES, key physicochemical properties, descriptor status pills.",
        "PI review, recruiter demo",
    ),
    (
        "03_descriptor_based_interpretation.png",
        "Descriptor-based interpretation",
        "Rule-based descriptor threshold profile (not labeled SHAP), driver analysis, chemical caveats.",
        "Explainability portfolio, AI-health recruiter",
    ),
    (
        "04_batch_upload.png",
        "Batch screening — upload",
        "CSV file uploader and paste-SMILES input panels with format hint card.",
        "Pharma usability, recruiter demo",
    ),
    (
        "05_batch_results.png",
        "Batch screening — results",
        "Summary metrics, results table, top-ranked lists, and download buttons for a 5-compound run.",
        "Pharma usability, GitHub README",
    ),
    (
        "06_molecule_comparison.png",
        "Molecule comparison",
        "Physicochemical, model & trust, and PK assumptions tabs across 5 compounds.",
        "LinkedIn, recruiter demo",
    ),
    (
        "07_multi_drug_pk_overlay.png",
        "Multi-drug PK overlay",
        "Five-drug scenario-adjusted oral PK curves visible simultaneously with distinct traces.",
        "PI review, PK teaching",
    ),
    (
        "08_absorption_sensitivity_simulator.png",
        "Absorption sensitivity simulator",
        "F/ka sliders, reference vs adjusted C-t overlay, exposure ratios, and educational disclaimer.",
        "PK/ADME reviewer",
    ),
    (
        "09_report_download.png",
        "Report download section",
        "Report preview and markdown/CSV download buttons. No 'predicted F' language.",
        "GitHub README, reviewer handoff",
    ),
    (
        "10_model_credibility_limits.png",
        "Model credibility and limits",
        "Model trust panel, validation mode comparison, scientific boundaries, and responsible-use notice.",
        "PI review, scientific rigor",
    ),
]

# Text that must NOT appear in any screenshot
BAD_TEXT = [
    "model artifact missing",
    "Baseline model artifact not found",
    "Molecule image could not be rendered",
    "Renderer unavailable here",
    "predicted F",
    "predicted bioavailability",
    "model predicts human F",
    "app error traceback",
    "Traceback (most recent call last)",
    "Select at least 2 molecules",
    "SHAP figure files are not present",
    # old navigation label — must be gone
    "ADME Workbench",
    # old explainability label — must be gone
    "Explainable AI\nDescriptor",
]


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

def wait_for_app(page: Page) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    # Wait for the hero h1 which is always rendered
    page.get_by_text("Caco-2 Permeability Screening", exact=False).first.wait_for(timeout=45000)
    page.wait_for_timeout(2500)


def capture(page: Page, filename: str, issues: list[str], full_page: bool = True) -> None:
    page.wait_for_timeout(800)
    try:
        text = page.locator("body").inner_text(timeout=15000)
    except Exception:
        text = ""
    for bad in BAD_TEXT:
        if bad in text:
            issues.append(f"`{filename}` contains problematic text: `{bad}`")
    page.screenshot(path=str(OUTPUT_DIR / filename), full_page=full_page)


def navigate(page: Page, label: str) -> None:
    """Click a sidebar radio button by exact label."""
    try:
        page.get_by_role("radio", name=re.compile(f"^{re.escape(label)}$")).click(timeout=8000)
    except Exception:
        page.get_by_text(label, exact=True).first.click(timeout=15000)
    page.wait_for_timeout(3000)


def click_tab(page: Page, name: str) -> None:
    page.get_by_role("tab", name=re.compile(f"^{re.escape(name)}$")).click(timeout=15000)
    page.wait_for_timeout(1400)


def expand_if_collapsed(page: Page, label: str) -> None:
    try:
        btn = page.get_by_role("button", name=re.compile(re.escape(label))).first
        btn.click(timeout=5000)
        page.wait_for_timeout(700)
    except TimeoutError:
        return


def scroll_to_text(page: Page, text: str) -> None:
    try:
        page.get_by_text(text, exact=False).first.scroll_into_view_if_needed(timeout=10000)
        page.wait_for_timeout(900)
    except Exception:
        pass


def scroll_to_bottom(page: Page) -> None:
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)


def scroll_to_top(page: Page) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)


# ---------------------------------------------------------------------------
# README / QC writers
# ---------------------------------------------------------------------------

def write_readme() -> None:
    lines = [
        "# Screenshot Index",
        "",
        "Fresh screenshots captured after batch-screening addition and "
        "descriptor-based explainability label fixes (post SHAP-overclaiming cleanup).",
        "",
        "| Screenshot | App section shown | What reviewer should look at | Recommended use |",
        "|---|---|---|---|",
    ]
    for filename, section, reviewer_note, use in SCREENSHOT_ROWS:
        lines.append(f"| `{filename}` | {section} | {reviewer_note} | {use} |")
    lines.extend(
        [
            "",
            "**Scientific boundary:** screenshots show Caco-2 permeability classification and "
            "educational PK/NCA simulation only. No validated human PK, clinical, regulatory, "
            "safety, efficacy, or dose prediction is shown.",
            "",
            "**Explainability label:** the interpretation panel is labeled "
            "'Descriptor-Based Model Interpretation' — not SHAP. "
            "SHAP figures are offline-only artifacts stored under `reports/figures/shap/`.",
            "",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_qc(issues: list[str]) -> None:
    path = OUTPUT_DIR / "SCREENSHOT_QC_ISSUES.md"
    for filename, *_ in SCREENSHOT_ROWS:
        if not (OUTPUT_DIR / filename).exists():
            issues.append(f"`{filename}` was not created.")

    if not issues:
        if path.exists():
            path.unlink()
        print("QC PASS — no issues found.")
        return

    lines = [
        "# Screenshot QC Issues",
        "",
        "The following screenshot problems were detected automatically.",
        "",
    ]
    for issue in issues:
        lines.extend(
            [
                f"## {issue}",
                "- Suspected cause: captured page contained a blocked phrase, "
                "missing UI section, or file was not produced.",
                "- Fix: open the affected app section, correct the visible state, "
                "then rerun `scripts/capture_streamlit_screenshots.py`.",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"QC ISSUES ({len(issues)}):")
    for i in issues:
        print(f"  • {i}")


# ---------------------------------------------------------------------------
# Main capture sequence
# ---------------------------------------------------------------------------

def delete_old_pngs() -> None:
    removed = 0
    for p in OUTPUT_DIR.glob("*.png"):
        p.unlink()
        removed += 1
    print(f"Deleted {removed} old PNG(s) from {OUTPUT_DIR}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    delete_old_pngs()
    issues: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1500, "height": 1250},
            device_scale_factor=1,
        )
        try:
            # ── 01: home dashboard ──────────────────────────────────────────
            wait_for_app(page)
            scroll_to_top(page)
            capture(page, "01_home_dashboard.png", issues)
            print("01 home_dashboard captured")

            # ── 02: single molecule profile ────────────────────────────────
            navigate(page, "Single Molecule")
            scroll_to_top(page)
            # Aspirin should be default; wait for structure render
            page.wait_for_timeout(2000)
            capture(page, "02_single_molecule_profile.png", issues, full_page=False)
            print("02 single_molecule_profile captured")

            # ── 03: descriptor-based interpretation tab ────────────────────
            click_tab(page, "Descriptor Interpretation")
            scroll_to_top(page)
            capture(page, "03_descriptor_based_interpretation.png", issues)
            print("03 descriptor_based_interpretation captured")

            # ── 04: batch upload (empty state) ─────────────────────────────
            navigate(page, "Batch Screening")
            scroll_to_top(page)
            capture(page, "04_batch_upload.png", issues, full_page=False)
            print("04 batch_upload captured")

            # ── 05: batch results — paste 5 SMILES then capture ───────────
            navigate(page, "Batch Screening")
            paste_tab_btn = page.get_by_role("tab", name="Paste SMILES")
            paste_tab_btn.click(timeout=10000)
            page.wait_for_timeout(600)
            textarea = page.get_by_role("textbox").filter(
                has_text=""
            ).first
            # Use a more reliable locator for the paste textarea
            try:
                textarea = page.locator("textarea[aria-label*='SMILES']").first
                if not textarea.is_visible(timeout=3000):
                    raise Exception("not found")
            except Exception:
                textarea = page.locator("textarea").nth(0)
            smiles_input = (
                "Aspirin,CC(=O)Oc1ccccc1C(=O)O\n"
                "Caffeine,Cn1cnc2c1c(=O)n(C)c(=O)n2C\n"
                "Metformin,CN(C)C(=N)N=C(N)N\n"
                "Ibuprofen,CC(C)Cc1ccc(C(C)C(=O)O)cc1\n"
                "Warfarin,CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O"
            )
            textarea.fill(smiles_input)
            page.wait_for_timeout(4000)
            scroll_to_top(page)
            capture(page, "05_batch_results.png", issues)
            print("05 batch_results captured")

            # ── 06: molecule comparison ────────────────────────────────────
            navigate(page, "Molecule Comparison")
            page.wait_for_timeout(2000)
            scroll_to_top(page)
            capture(page, "06_molecule_comparison.png", issues)
            print("06 molecule_comparison captured")

            # ── 07: multi-drug PK overlay ──────────────────────────────────
            navigate(page, "Multi-Drug PK")
            page.wait_for_timeout(3000)
            scroll_to_top(page)
            # Scroll to show the overlay charts
            try:
                scroll_to_text(page, "Overlay concentration-time curves")
            except Exception:
                pass
            capture(page, "07_multi_drug_pk_overlay.png", issues)
            print("07 multi_drug_pk_overlay captured")

            # ── 08: absorption sensitivity simulator ───────────────────────
            navigate(page, "Single Molecule")
            page.wait_for_timeout(1500)
            click_tab(page, "Absorption Sensitivity")
            page.wait_for_timeout(1500)
            scroll_to_top(page)
            capture(page, "08_absorption_sensitivity_simulator.png", issues)
            print("08 absorption_sensitivity_simulator captured")

            # ── 09: report download ────────────────────────────────────────
            click_tab(page, "Limits")
            page.wait_for_timeout(1000)
            scroll_to_text(page, "Report Download")
            capture(page, "09_report_download.png", issues, full_page=False)
            print("09 report_download captured")

            # ── 10: model credibility / limits ─────────────────────────────
            navigate(page, "Evidence & Limits")
            page.wait_for_timeout(2000)
            expand_if_collapsed(page, "Why this project matters")
            expand_if_collapsed(page, "Model Trust and Engineering")
            scroll_to_top(page)
            capture(page, "10_model_credibility_limits.png", issues)
            print("10 model_credibility_limits captured")

        except Exception as exc:
            issues.append(f"Script crashed: {exc}")
            print(f"ERROR: {exc}", file=sys.stderr)
        finally:
            browser.close()

    write_readme()
    write_qc(issues)
    print(f"\nDone — {len(SCREENSHOT_ROWS)} screenshots targeted, "
          f"{sum(1 for f, *_ in SCREENSHOT_ROWS if (OUTPUT_DIR / f).exists())} produced.")


if __name__ == "__main__":
    main()
