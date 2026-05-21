"""Capture fresh review screenshots for the Streamlit app."""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, TimeoutError, expect, sync_playwright


BASE_URL = "http://127.0.0.1:8507"
OUTPUT_DIR = Path("docs") / "screenshots"

SCREENSHOT_ROWS = [
    ("01_home_dashboard.png", "Home dashboard", "Overall product framing, hero cards, workflow, and metric cards.", "GitHub README, recruiter demo"),
    ("02_how_to_use_and_app_overview.png", "How-to-use and app overview", "Beginner workflow, what the platform does, and scientific grounding.", "GitHub README, student onboarding"),
    ("03_molecule_input_aspirin.png", "Aspirin molecule input/profile", "SVG rendering, canonical SMILES, teaching note, and key properties.", "PI review, recruiter demo"),
    ("04_descriptor_summary.png", "Descriptor summary", "Descriptor table and medicinal chemistry interpretation.", "PK/ADME reviewer"),
    ("05_permeability_prediction.png", "Permeability prediction", "Prediction card, probability, model source, and decision-support interpretation.", "AI-health recruiter, PI review"),
    ("06_confidence_and_uncertainty.png", "Confidence and uncertainty", "Confidence score, entropy, and reliability explanation.", "Model-risk review"),
    ("07_applicability_domain.png", "Applicability domain", "Tanimoto similarity, nearest neighbor, and domain-shift explanation.", "Academic reviewer"),
    ("08_explainable_ai.png", "Explainable AI", "Descriptor driver table, SHAP-style interpretation, and chemical caveats.", "Explainability portfolio"),
    ("09_molecule_comparison.png", "Molecule comparison", "Aspirin, caffeine, ibuprofen, metformin, and propranolol comparison dashboard.", "LinkedIn, recruiter demo"),
    ("10_pk_nca_simulator.png", "PK/NCA simulator", "Oral preset, parameters, metric cards, and concentration-time plot.", "PI review, PK teaching"),
    ("11_permeability_to_pk_impact.png", "Permeability-to-PK impact", "F/ka assumption mapping, AUC/Cmax/Tmax/CL-F ratios, and interpretations.", "PK/ADME reviewer"),
    ("12_pk_impact_comparison_curves.png", "PK impact comparison curves", "Reference vs permeability-adjusted oral concentration-time curves.", "PK teaching, PI review"),
    ("13_equations_iv_oral_ivive.png", "Equations, IV/oral, IVIVE", "PK equations, route explanation, and IVIVE boundary.", "Academic review"),
    ("14_report_download_section.png", "Report download section", "Markdown report and CSV download buttons.", "GitHub README, reviewer handoff"),
    ("15_scientific_limitations_and_reviewer_summary.png", "Scientific limits and reviewer summary", "Reviewer summary and external validation roadmap.", "PI review, scientific rigor"),
]

BAD_TEXT = [
    "model artifact missing",
    "Baseline model artifact not found",
    "Molecule image could not be rendered",
    "then\nthen",
    "Select at least two molecules to compare.",
    "SHAP figure files are not present",
]


def wait_for_app(page: Page) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    expect(page.get_by_text("Explainable AI ADME-PK Platform").first).to_be_visible(timeout=45000)
    page.wait_for_timeout(2500)


def capture(page: Page, filename: str, issues: list[str], full_page: bool = True) -> None:
    text = page.locator("body").inner_text(timeout=15000)
    for bad in BAD_TEXT:
        if bad in text:
            issues.append(f"`{filename}` contains problematic text: `{bad}`")
    page.screenshot(path=str(OUTPUT_DIR / filename), full_page=full_page)


def click_tab(page: Page, name: str) -> None:
    page.get_by_role("tab", name=re.compile(f"^{re.escape(name)}$")).click(timeout=15000)
    page.wait_for_timeout(1400)


def navigate(page: Page, label: str) -> None:
    # Try radio button first, then fall back to plain text click
    try:
        page.get_by_role("radio", name=re.compile(f"^{re.escape(label)}$")).click(timeout=6000)
    except Exception:
        page.get_by_text(label, exact=True).first.click(timeout=15000)
    page.wait_for_timeout(3500)


def expand_if_collapsed(page: Page, label: str) -> None:
    try:
        button = page.get_by_role("button", name=re.compile(re.escape(label))).first
        button.click(timeout=5000)
        page.wait_for_timeout(700)
    except TimeoutError:
        return


def scroll_to_text(page: Page, text: str) -> None:
    page.get_by_text(text, exact=False).first.scroll_into_view_if_needed(timeout=15000)
    page.wait_for_timeout(800)


def write_readme() -> None:
    lines = [
        "# Screenshot Index",
        "",
        "Fresh screenshots generated from the local Streamlit app after the educational PK/ADME explanation and report-download upgrades.",
        "",
        "| Screenshot | App section shown | What a reviewer should look at | Recommended use |",
        "|---|---|---|---|",
    ]
    for filename, section, reviewer_note, use in SCREENSHOT_ROWS:
        lines.append(f"| `{filename}` | {section} | {reviewer_note} | {use} |")
    lines.extend(
        [
            "",
            "Scientific boundary: screenshots show Caco-2 permeability prediction and educational PK/NCA/permeability-to-PK impact simulation only. They do not show validated human PK, clinical, regulatory, safety, efficacy, or dose prediction.",
            "",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_qc(issues: list[str]) -> None:
    path = OUTPUT_DIR / "SCREENSHOT_QC_ISSUES.md"
    missing = [filename for filename, *_ in SCREENSHOT_ROWS if not (OUTPUT_DIR / filename).exists()]
    for filename in missing:
        issues.append(f"`{filename}` was not created.")

    if not issues:
        if path.exists():
            path.unlink()
        return

    lines = [
        "# Screenshot QC Issues",
        "",
        "The following screenshot problems were detected automatically.",
        "",
        *[f"- {issue}" for issue in issues],
        "",
        "Proposed fix: open the affected app section locally, correct the broken UI/content state, and rerun `scripts/capture_streamlit_screenshots.py`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    issues: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 1250}, device_scale_factor=1)
        try:
            wait_for_app(page)
            capture(page, "01_home_dashboard.png", issues)

            expand_if_collapsed(page, "How to use this app")
            expand_if_collapsed(page, "Scientific guide")
            capture(page, "02_how_to_use_and_app_overview.png", issues)

            capture(page, "03_molecule_input_aspirin.png", issues)

            for tab, filename in [
                ("Descriptors", "04_descriptor_summary.png"),
                ("Permeability", "05_permeability_prediction.png"),
                ("Confidence", "06_confidence_and_uncertainty.png"),
                ("Applicability Domain", "07_applicability_domain.png"),
                ("Explainable AI", "08_explainable_ai.png"),
            ]:
                click_tab(page, tab)
                capture(page, filename, issues)

            navigate(page, "Molecule Comparison")
            capture(page, "09_molecule_comparison.png", issues)

            navigate(page, "PK/NCA Simulator")
            expect(page.get_by_text("Oral fast absorption").first).to_be_visible(timeout=15000)
            capture(page, "10_pk_nca_simulator.png", issues)

            navigate(page, "ADME Workbench")
            click_tab(page, "PK Impact")
            page.wait_for_timeout(1200)
            capture(page, "11_permeability_to_pk_impact.png", issues)
            # Click the "Linear C-t curve" tab to show the concentration-time curves
            try:
                page.get_by_role("tab", name=re.compile("Linear C-t curve")).click(timeout=8000)
                page.wait_for_timeout(1000)
            except Exception:
                pass
            scroll_to_text(page, "Editable scenario parameters")
            page.wait_for_timeout(600)
            capture(page, "12_pk_impact_comparison_curves.png", issues, full_page=False)

            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(1800)
            expand_if_collapsed(page, "PK equations used")
            expand_if_collapsed(page, "IV bolus vs oral dosing")
            expand_if_collapsed(page, "What IVIVE would require")
            capture(page, "13_equations_iv_oral_ivive.png", issues)

            click_tab(page, "PK Impact")
            scroll_to_text(page, "Download markdown report")
            capture(page, "14_report_download_section.png", issues, full_page=False)

            navigate(page, "Evidence & Limits")
            capture(page, "15_scientific_limitations_and_reviewer_summary.png", issues)
        finally:
            browser.close()

    write_readme()
    write_qc(issues)


if __name__ == "__main__":
    main()
