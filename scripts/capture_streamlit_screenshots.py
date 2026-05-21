"""Capture fresh review screenshots for the Streamlit app."""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, TimeoutError, expect, sync_playwright


BASE_URL = "http://127.0.0.1:8507"
OUTPUT_DIR = Path("docs") / "screenshots"

SCREENSHOT_ROWS = [
    ("01_home_dashboard.png", "Home dashboard", "Overall product framing, workflow, and metric cards.", "GitHub README, recruiter demo"),
    ("02_how_to_use_and_app_overview.png", "How-to-use and app overview", "Beginner workflow, what the platform does, and scientific grounding.", "GitHub README, student onboarding"),
    ("03_molecule_library_screening.png", "Molecule library screening", "Search/filter controls and aspirin example library workflow.", "Recruiter demo, GitHub README"),
    ("04_selected_molecule_profile.png", "Selected molecule profile", "Aspirin SVG rendering, canonical SMILES, teaching note, and key properties.", "PI review, recruiter demo"),
    ("05_descriptor_summary.png", "Descriptor summary", "Descriptor table and medicinal chemistry interpretation.", "PK/ADME reviewer"),
    ("06_permeability_prediction.png", "Permeability prediction", "Prediction card, probability, model source, and decision-support interpretation.", "AI-health recruiter, PI review"),
    ("07_confidence_applicability.png", "Confidence and applicability", "Confidence, entropy, Tanimoto similarity, and domain-shift explanation.", "Model-risk review, academic reviewer"),
    ("08_explainable_ai.png", "Explainable AI", "Descriptor driver table, SHAP-style interpretation, and chemical caveats.", "Explainability portfolio"),
    ("09_focused_molecule_comparison.png", "Focused molecule comparison", "Aspirin, caffeine, ibuprofen, metformin, and propranolol ADME comparison.", "LinkedIn, recruiter demo"),
    ("10_multi_drug_pk_curve_comparison.png", "Multi-drug PK curve comparison", "Five-drug oral PK overlay, scenario-F assumptions, and literature teaching notes.", "PI review, PK teaching"),
    ("11_absorption_sensitivity_simulator.png", "Absorption sensitivity simulator", "Aspirin F/ka assumption controls, exposure ratios, and sensitivity interpretation.", "PK/ADME reviewer"),
    ("12_literature_f_vs_scenario_f.png", "Literature F vs scenario F", "Aspirin literature teaching F, default scenario F, and presystemic-loss warning.", "Scientific review"),
    ("13_equations_iv_oral_ivive.png", "Equations, IV/oral, IVIVE", "Expanded PK equations, IV/oral route explanation, and IVIVE boundary panels.", "Academic review"),
    ("14_report_download_section.png", "Report download section", "Report-contents preview and download buttons.", "GitHub README, reviewer handoff"),
    ("15_scientific_limitations_and_model_credibility.png", "Scientific limitations and model credibility", "Model trust, validation, limitations, and FDA/EMA-style boundaries.", "PI review, scientific rigor"),
    ("16_reviewer_summary.png", "Reviewer summary", "AI/ML recruiter, computational pharmacology, and PI reviewer summaries.", "Recruiter demo, PI review"),
]

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
    "Select at least two molecules to compare.",
    "Select at least 2 molecules",
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
    try:
        page.get_by_role("radio", name=re.compile(f"^{re.escape(label)}$")).click(timeout=8000)
    except Exception:
        page.get_by_text(label, exact=True).first.click(timeout=15000)
    page.wait_for_timeout(3000)


def expand_if_collapsed(page: Page, label: str) -> None:
    try:
        page.get_by_role("button", name=re.compile(re.escape(label))).first.click(timeout=5000)
        page.wait_for_timeout(700)
    except TimeoutError:
        return


def scroll_to_text(page: Page, text: str) -> None:
    page.get_by_text(text, exact=False).first.scroll_into_view_if_needed(timeout=15000)
    page.wait_for_timeout(900)


def delete_old_pngs() -> None:
    for path in OUTPUT_DIR.glob("*.png"):
        path.unlink()


def write_readme() -> None:
    lines = [
        "# Screenshot Index",
        "",
        "Fresh screenshots generated from the current Streamlit app after molecule-rendering and F-assumption language fixes.",
        "",
        "| Screenshot | App section shown | What reviewer should look at | Recommended use |",
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
    for filename, *_ in SCREENSHOT_ROWS:
        if not (OUTPUT_DIR / filename).exists():
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
    ]
    for issue in issues:
        lines.extend(
            [
                f"## {issue}",
                "- Suspected cause: the captured page contained a blocked phrase, missing section, or screenshot file was not produced.",
                "- Suggested fix: open the affected app section, correct the visible UI/content state, then rerun `scripts/capture_streamlit_screenshots.py`.",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    delete_old_pngs()
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

            navigate(page, "ADME Workbench")
            scroll_to_text(page, "Therapeutic category")
            capture(page, "03_molecule_library_screening.png", issues, full_page=False)

            scroll_to_text(page, "Aspirin")
            capture(page, "04_selected_molecule_profile.png", issues, full_page=False)

            click_tab(page, "Descriptors")
            capture(page, "05_descriptor_summary.png", issues)

            click_tab(page, "Permeability")
            capture(page, "06_permeability_prediction.png", issues)

            click_tab(page, "Confidence")
            capture(page, "07_confidence_applicability.png", issues)

            click_tab(page, "Explainable AI")
            capture(page, "08_explainable_ai.png", issues)

            navigate(page, "Molecule Comparison")
            capture(page, "09_focused_molecule_comparison.png", issues)

            navigate(page, "Multi-Drug PK")
            expect(page.get_by_text("Multi-Drug PK Impact Comparison").first).to_be_visible(timeout=20000)
            capture(page, "10_multi_drug_pk_curve_comparison.png", issues)

            navigate(page, "ADME Workbench")
            click_tab(page, "Absorption Sensitivity")
            scroll_to_text(page, "Absorption Sensitivity Simulator")
            capture(page, "11_absorption_sensitivity_simulator.png", issues, full_page=False)

            scroll_to_text(page, "Literature teaching F")
            capture(page, "12_literature_f_vs_scenario_f.png", issues, full_page=False)

            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            for panel in ["PK equations used", "IV bolus vs oral dosing", "What IVIVE would require"]:
                expand_if_collapsed(page, panel)
            scroll_to_text(page, "PK equations used in this educational simulator")
            capture(page, "13_equations_iv_oral_ivive.png", issues)

            navigate(page, "ADME Workbench")
            scroll_to_text(page, "Report Download")
            capture(page, "14_report_download_section.png", issues, full_page=False)

            navigate(page, "Evidence & Limits")
            expand_if_collapsed(page, "Why this project matters")
            expand_if_collapsed(page, "Model Trust and Engineering")
            capture(page, "15_scientific_limitations_and_model_credibility.png", issues)

            expand_if_collapsed(page, "Reviewer Summary")
            scroll_to_text(page, "Reviewer Summary")
            capture(page, "16_reviewer_summary.png", issues, full_page=False)
        finally:
            browser.close()

    write_readme()
    write_qc(issues)


if __name__ == "__main__":
    main()
