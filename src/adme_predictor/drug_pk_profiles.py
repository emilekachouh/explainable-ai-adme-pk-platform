"""Educational drug PK profiles from published literature teaching values.

These are curated approximate values for educational purposes only.
Label as 'literature teaching preset' and do NOT present as model predictions.
Verify all values against primary literature before any scientific use.
"""
from __future__ import annotations

DRUG_PK_PROFILES: dict[str, dict] = {
    "aspirin": {
        "name": "Aspirin",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "route": "oral",
        "teaching_dose_mg": 325.0,
        "approximate_half_life_h": 0.25,
        "approximate_f": 0.68,
        "approximate_vd_l_kg": 0.14,
        "approximate_ka_per_h": 1.2,
        "approximate_kel_per_h": 2.8,
        "source_note": (
            "Approximate teaching values. Aspirin undergoes rapid hydrolysis to salicylate. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Rapid pre-systemic hydrolysis to salicylate; PK is complex and dose-dependent.",
            "Simple one-compartment model is an educational approximation only.",
            "Saturable (Michaelis-Menten) elimination at higher doses.",
        ],
    },
    "ibuprofen": {
        "name": "Ibuprofen",
        "smiles": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "route": "oral",
        "teaching_dose_mg": 400.0,
        "approximate_half_life_h": 2.0,
        "approximate_f": 0.80,
        "approximate_vd_l_kg": 0.14,
        "approximate_ka_per_h": 1.5,
        "approximate_kel_per_h": 0.35,
        "source_note": (
            "Approximate teaching values. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "High plasma protein binding (>99%); total vs free drug distinction is important.",
            "Racemate; chiral inversion from R to S form occurs in vivo.",
            "Verify Vd on a body-weight basis; values vary across references.",
        ],
    },
    "caffeine": {
        "name": "Caffeine",
        "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        "route": "oral",
        "teaching_dose_mg": 200.0,
        "approximate_half_life_h": 5.0,
        "approximate_f": 1.00,
        "approximate_vd_l_kg": 0.60,
        "approximate_ka_per_h": 1.2,
        "approximate_kel_per_h": 0.14,
        "source_note": (
            "Approximate teaching values. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Near-complete oral absorption; useful as a high-F teaching example.",
            "Metabolized primarily by CYP1A2; enzyme induction and inhibition are relevant.",
            "Half-life is longer in neonates and during pregnancy; shorter in smokers.",
        ],
    },
    "metformin": {
        "name": "Metformin",
        "smiles": "CN(C)C(=N)NC(=N)N",
        "route": "oral",
        "teaching_dose_mg": 500.0,
        "approximate_half_life_h": 5.0,
        "approximate_f": 0.50,
        "approximate_vd_l_kg": 6.5,
        "approximate_ka_per_h": 0.30,
        "approximate_kel_per_h": 0.14,
        "source_note": (
            "Approximate teaching values. Metformin absorption is incomplete and "
            "transporter-mediated. Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Absorption is transporter-mediated (OCT1, OCT2); passive permeability is low.",
            "Not metabolized; excreted renally unchanged. Large apparent Vd reflects tissue distribution.",
            "Key teaching example: transporter-dependent absorption can decouple permeability from F.",
        ],
    },
    "propranolol": {
        "name": "Propranolol",
        "smiles": "CC(C)NCC(O)COc1cccc2ccccc12",
        "route": "oral",
        "teaching_dose_mg": 80.0,
        "approximate_half_life_h": 4.0,
        "approximate_f": 0.26,
        "approximate_vd_l_kg": 4.0,
        "approximate_ka_per_h": 1.5,
        "approximate_kel_per_h": 0.17,
        "source_note": (
            "Approximate teaching values. High first-pass extraction; F is variable. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "High hepatic first-pass extraction; F is highly variable between individuals.",
            "High lipophilicity; compare to atenolol for lipophilicity-ADME contrast teaching.",
            "Stereoselective metabolism; racemate with different R/S pharmacology.",
        ],
    },
    "atenolol": {
        "name": "Atenolol",
        "smiles": "CC(C)NCC(O)COc1ccc(CC(N)=O)cc1",
        "route": "oral",
        "teaching_dose_mg": 50.0,
        "approximate_half_life_h": 7.0,
        "approximate_f": 0.50,
        "approximate_vd_l_kg": 1.1,
        "approximate_ka_per_h": 0.50,
        "approximate_kel_per_h": 0.10,
        "source_note": (
            "Approximate teaching values. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Hydrophilic beta-blocker; low lipophilicity contrast to propranolol.",
            "Low protein binding; excreted renally largely unchanged.",
            "Useful teaching contrast: similar pharmacological class, very different ADME.",
        ],
    },
    "warfarin": {
        "name": "Warfarin",
        "smiles": "OC(=O)C(CC(=O)c1ccccc1)c1ccc2ccccc2o1",
        "route": "oral",
        "teaching_dose_mg": 5.0,
        "approximate_half_life_h": 40.0,
        "approximate_f": 0.93,
        "approximate_vd_l_kg": 0.14,
        "approximate_ka_per_h": 0.80,
        "approximate_kel_per_h": 0.017,
        "source_note": (
            "Approximate teaching values. Warfarin is a racemate with complex PK/PD. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Very high protein binding (>99%); narrow therapeutic index requires monitoring.",
            "Racemate; S-warfarin (more pharmacologically active) metabolized mainly by CYP2C9.",
            "Long half-life and narrow TI make it a key teaching example for DDI relevance.",
        ],
    },
    "diazepam": {
        "name": "Diazepam",
        "smiles": "CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21",
        "route": "oral",
        "teaching_dose_mg": 10.0,
        "approximate_half_life_h": 48.0,
        "approximate_f": 1.00,
        "approximate_vd_l_kg": 1.1,
        "approximate_ka_per_h": 0.80,
        "approximate_kel_per_h": 0.014,
        "source_note": (
            "Approximate teaching values. Diazepam has active metabolite desmethyldiazepam. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Active metabolite (desmethyldiazepam) contributes substantially to pharmacological effect.",
            "Very long half-life; accumulation with repeated dosing is a key teaching point.",
            "High lipophilicity and large Vd; not a low-lipophilicity ADME representative.",
        ],
    },
    "midazolam": {
        "name": "Midazolam",
        "smiles": "Cc1ncc2n1-c1ccc(Cl)cc1C(=N2)c1ccccc1F",
        "route": "oral",
        "teaching_dose_mg": 7.5,
        "approximate_half_life_h": 2.5,
        "approximate_f": 0.44,
        "approximate_vd_l_kg": 1.1,
        "approximate_ka_per_h": 1.5,
        "approximate_kel_per_h": 0.28,
        "source_note": (
            "Approximate teaching values. Midazolam is a classic CYP3A4 probe substrate. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Classic CYP3A4 probe substrate; widely used in drug-drug interaction studies.",
            "High hepatic first-pass extraction; F is sensitive to CYP3A4 modulation.",
            "Shorter half-life than diazepam despite same pharmacological class; contrast is instructive.",
        ],
    },
    "omeprazole": {
        "name": "Omeprazole",
        "smiles": "COc1ccc2c(c1)nc(CS(=O)c1ncccc1C)n2C",
        "route": "oral",
        "teaching_dose_mg": 20.0,
        "approximate_half_life_h": 1.0,
        "approximate_f": 0.50,
        "approximate_vd_l_kg": 0.35,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.69,
        "source_note": (
            "Approximate teaching values. Omeprazole is an enteric-coated prodrug. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Enteric coating delays release; absorption profiles differ between formulations.",
            "Prodrug activated in acidic environment; pharmacological duration exceeds PK half-life.",
            "CYP2C19 polymorphism substantially affects clearance; poor vs extensive metabolizers differ.",
        ],
    },
}

DRUG_PROFILE_NAMES = list(DRUG_PK_PROFILES.keys())
