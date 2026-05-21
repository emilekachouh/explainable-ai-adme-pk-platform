"""Capture recruiter-review screenshots for the Streamlit app."""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, TimeoutError, expect, sync_playwright


BASE_URL = "http://127.0.0.1:8507"
OUTPUT_DIR = Path("docs") / "screenshots"


SCREENSHOTS = [
    ("01_home_dashboard.png", "Home / landing dashboard"),
    ("02_molecule_input_aspirin.png", "Molecule input section using Aspirin"),
    ("03_descriptor_summary.png", "Descriptor Summary tab"),
    ("04_permeability_prediction.png", "Permeability Prediction tab"),
    ("05_confidence.png", "Confidence tab"),
    ("06_applicability_domain.png", "Applicability Domain tab"),
    ("07_explainable_ai.png", "Explainable AI tab"),
    ("08_scientific_limitations.png", "Scientific Limitations tab"),
    ("09_pk_nca_simulator.png", "PK/NCA Simulator overview"),
    ("10_pk_nca_results.png", "PK/NCA concentration-time graph and NCA table"),
    ("11_molecule_comparison.png", "Molecule comparison mode"),
    ("12_example_molecule_library.png", "Example molecule library / search-filter view"),
]


def wait_for_app(page: Page) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    expect(page.get_by_text("Explainable AI ADME-PK Platform").first).to_be_visible(timeout=45000)
    page.wait_for_timeout(2500)


def screenshot(page: Page, filename: str) -> None:
    page.screenshot(path=str(OUTPUT_DIR / filename), full_page=True)


def click_tab(page: Page, name: str) -> None:
    page.get_by_role("tab", name=re.compile(f"^{re.escape(name)}$")).click(timeout=15000)
    page.wait_for_timeout(1200)


def navigate(page: Page, label: str) -> None:
    page.get_by_text(label, exact=True).click(timeout=15000)
    page.wait_for_timeout(2500)


def set_pk_oral_demo(page: Page) -> None:
    page.get_by_text("PK/NCA Simulator", exact=True).click(timeout=15000)
    page.wait_for_timeout(2000)
    expect(page.get_by_text("Oral fast absorption").first).to_be_visible(timeout=15000)
    page.wait_for_timeout(1200)


def write_index(missing: list[str]) -> None:
    rows = [
        "# Screenshot Index",
        "",
        "These screenshots were generated from the local Streamlit app for GitHub, LinkedIn, recruiter, and academic review materials.",
        "",
        "| File | Shows | Recommended use | Notes |",
        "|---|---|---|---|",
    ]
    uses = {
        "01_home_dashboard.png": "GitHub README, recruiter demo, LinkedIn hero",
        "02_molecule_input_aspirin.png": "GitHub README, PI review",
        "03_descriptor_summary.png": "PK/ADME reviewer detail",
        "04_permeability_prediction.png": "Recruiter demo, AI-health review",
        "05_confidence.png": "AI-health review, model-risk discussion",
        "06_applicability_domain.png": "Academic review, model reliability",
        "07_explainable_ai.png": "Explainability portfolio evidence",
        "08_scientific_limitations.png": "Scientific rigor and responsible-use review",
        "09_pk_nca_simulator.png": "PK education demo",
        "10_pk_nca_results.png": "PK/NCA result review",
        "11_molecule_comparison.png": "Recruiter demo, LinkedIn carousel",
        "12_example_molecule_library.png": "GitHub README, demo setup",
    }
    for filename, description in SCREENSHOTS:
        note = "Captured" if filename not in missing else "Missing; see MISSING_FEATURES.md"
        rows.append(f"| `{filename}` | {description} | {uses[filename]} | {note} |")
    rows.extend(
        [
            "",
            "Scientific boundary: screenshots show Caco-2 permeability risk prediction and educational PK/NCA simulation only. They do not show validated clinical PK, PBPK, safety, efficacy, dose, or regulatory prediction.",
            "",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(rows), encoding="utf-8")


def write_missing(missing: list[str], errors: list[str]) -> None:
    path = OUTPUT_DIR / "MISSING_FEATURES.md"
    if not missing:
        if path.exists():
            path.unlink()
        return
    lines = [
        "# Missing Screenshot Features",
        "",
        "The following screenshots could not be captured automatically.",
        "",
    ]
    for item in missing:
        lines.append(f"- `{item}`")
    if errors:
        lines.extend(["", "## Automation Notes", ""])
        lines.extend(f"- {error}" for error in errors)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []
    errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=1)
        try:
            wait_for_app(page)
            screenshot(page, "01_home_dashboard.png")
            screenshot(page, "02_molecule_input_aspirin.png")

            for tab, filename in [
                ("Descriptors", "03_descriptor_summary.png"),
                ("Permeability", "04_permeability_prediction.png"),
                ("Confidence", "05_confidence.png"),
                ("Applicability Domain", "06_applicability_domain.png"),
                ("Explainable AI", "07_explainable_ai.png"),
                ("Limits", "08_scientific_limitations.png"),
            ]:
                try:
                    click_tab(page, tab)
                    screenshot(page, filename)
                except TimeoutError as error:
                    missing.append(filename)
                    errors.append(f"{filename}: {error}")

            try:
                set_pk_oral_demo(page)
                screenshot(page, "09_pk_nca_simulator.png")
                click_tab(page, "Tables")
                screenshot(page, "10_pk_nca_results.png")
            except TimeoutError as error:
                missing.extend(["09_pk_nca_simulator.png", "10_pk_nca_results.png"])
                errors.append(f"PK/NCA screenshots: {error}")

            try:
                navigate(page, "Molecule Comparison")
                screenshot(page, "11_molecule_comparison.png")
            except TimeoutError as error:
                missing.append("11_molecule_comparison.png")
                errors.append(f"11_molecule_comparison.png: {error}")

            try:
                navigate(page, "ADME Workbench")
                screenshot(page, "12_example_molecule_library.png")
            except TimeoutError as error:
                missing.append("12_example_molecule_library.png")
                errors.append(f"12_example_molecule_library.png: {error}")
        finally:
            browser.close()

    write_index(missing)
    write_missing(missing, errors)


if __name__ == "__main__":
    main()
