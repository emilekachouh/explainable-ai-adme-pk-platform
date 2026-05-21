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
    "acetaminophen": {
        "name": "Acetaminophen",
        "smiles": "CC(=O)Nc1ccc(O)cc1",
        "route": "oral",
        "teaching_dose_mg": 500.0,
        "approximate_half_life_h": 2.0,
        "approximate_f": 0.88,
        "approximate_vd_l_kg": 0.9,
        "approximate_ka_per_h": 1.5,
        "approximate_kel_per_h": 0.35,
        "source_note": (
            "Approximate teaching values. Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Hepatotoxicity risk at supratherapeutic doses via CYP2E1 reactive metabolite (NAPQI).",
            "Glucuronidation and sulfation are primary metabolic routes under therapeutic doses.",
            "Near-complete absorption makes it a useful high-F oral teaching example.",
        ],
    },
    "naproxen": {
        "name": "Naproxen",
        "smiles": "COc1ccc2cc(C(C)C(=O)O)ccc2c1",
        "route": "oral",
        "teaching_dose_mg": 250.0,
        "approximate_half_life_h": 13.0,
        "approximate_f": 0.95,
        "approximate_vd_l_kg": 0.16,
        "approximate_ka_per_h": 0.8,
        "approximate_kel_per_h": 0.053,
        "source_note": (
            "Approximate teaching values. Naproxen has a longer half-life than ibuprofen. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "High plasma protein binding (>99%); long half-life supports twice-daily dosing.",
            "NSAID with GI/cardiovascular risk considerations; educational PK focus only.",
            "Compare half-life to ibuprofen (~13 h vs ~2 h) as a teaching contrast.",
        ],
    },
    "diclofenac": {
        "name": "Diclofenac",
        "smiles": "O=C(O)Cc1ccccc1Nc1c(Cl)cccc1Cl",
        "route": "oral",
        "teaching_dose_mg": 50.0,
        "approximate_half_life_h": 1.5,
        "approximate_f": 0.54,
        "approximate_vd_l_kg": 1.3,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.46,
        "source_note": (
            "Approximate teaching values. Diclofenac has significant first-pass metabolism. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Substantial first-pass extraction reduces F to approximately 50%.",
            "Short half-life requires multiple daily doses; modified-release formulations exist.",
            "Hepatic metabolism (CYP2C9) and glucuronidation; drug-drug interaction potential.",
        ],
    },
    "metoprolol": {
        "name": "Metoprolol",
        "smiles": "COCCc1ccc(OCC(O)CNC(C)C)cc1",
        "route": "oral",
        "teaching_dose_mg": 100.0,
        "approximate_half_life_h": 3.5,
        "approximate_f": 0.40,
        "approximate_vd_l_kg": 5.6,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.20,
        "source_note": (
            "Approximate teaching values. Metoprolol undergoes first-pass hepatic metabolism. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "First-pass extraction gives variable F (~40%); CYP2D6 polymorphism affects clearance.",
            "Cardioselective beta-1 blocker; contrast with propranolol (non-selective, higher first-pass).",
            "Extensive-metabolizer vs poor-metabolizer contrast is a key clinical pharmacology teaching point.",
        ],
    },
    "amlodipine": {
        "name": "Amlodipine",
        "smiles": "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OC)C1c1ccccc1Cl",
        "route": "oral",
        "teaching_dose_mg": 10.0,
        "approximate_half_life_h": 40.0,
        "approximate_f": 0.64,
        "approximate_vd_l_kg": 21.0,
        "approximate_ka_per_h": 0.1,
        "approximate_kel_per_h": 0.017,
        "source_note": (
            "Approximate teaching values. Amlodipine has a very long half-life. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Very long half-life (~35-50 h) supports once-daily dosing; contrast with short-acting CCBs.",
            "Large Vd (~21 L/kg) reflects extensive tissue distribution and lipophilicity.",
            "Slow onset and long duration make it useful for teaching accumulation/steady-state concepts.",
        ],
    },
    "furosemide": {
        "name": "Furosemide",
        "smiles": "NS(=O)(=O)c1cc(C(=O)O)c(NCc2ccco2)cc1Cl",
        "route": "oral",
        "teaching_dose_mg": 40.0,
        "approximate_half_life_h": 0.5,
        "approximate_f": 0.65,
        "approximate_vd_l_kg": 0.15,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 1.39,
        "source_note": (
            "Approximate teaching values. Furosemide bioavailability is variable (10-100%). "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Highly variable oral bioavailability (10-100%) due to formulation and GI status.",
            "Loop diuretic with site of action at renal tubule; PK does not predict diuretic response alone.",
            "Compare oral vs IV route: IV has faster onset and more predictable response.",
        ],
    },
    "digoxin": {
        "name": "Digoxin",
        "smiles": "CC1OC(OC2C(O)CC(OC3C(O)CC(OC4CCC5(C)C(CCC6C5CC(O)C5(C)C(C7=CC(=O)OC7)CCC65O)C4)OC3C)OC2C)CC(O)C1O",
        "route": "oral",
        "teaching_dose_mg": 0.125,
        "approximate_half_life_h": 36.0,
        "approximate_f": 0.70,
        "approximate_vd_l_kg": 7.0,
        "approximate_ka_per_h": 0.5,
        "approximate_kel_per_h": 0.019,
        "source_note": (
            "Approximate teaching values. Digoxin has a narrow therapeutic index. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Narrow therapeutic index; therapeutic drug monitoring is essential in clinical use.",
            "Large Vd (~7 L/kg); very long half-life (~36 h); accumulation risk with renal impairment.",
            "P-gp substrate: drug interactions can significantly alter digoxin levels.",
        ],
    },
    "theophylline": {
        "name": "Theophylline",
        "smiles": "Cn1c(=O)c2[nH]cnc2n(C)c1=O",
        "route": "oral",
        "teaching_dose_mg": 200.0,
        "approximate_half_life_h": 8.0,
        "approximate_f": 0.96,
        "approximate_vd_l_kg": 0.5,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.087,
        "source_note": (
            "Approximate teaching values. Theophylline has a narrow therapeutic index. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Narrow therapeutic index; plasma monitoring required in clinical use.",
            "CYP1A2 substrate: enzyme inducers (smoking) and inhibitors (ciprofloxacin) alter clearance.",
            "Near-complete absorption; useful high-F oral teaching example with half-life ~8 h.",
        ],
    },
    "morphine": {
        "name": "Morphine",
        "smiles": "CN1CCC23c4c5ccc(O)c4OC2C(O)C=CC3C1C5",
        "route": "oral",
        "teaching_dose_mg": 30.0,
        "approximate_half_life_h": 2.0,
        "approximate_f": 0.24,
        "approximate_vd_l_kg": 3.2,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.35,
        "source_note": (
            "Approximate teaching values. Morphine has extensive first-pass glucuronidation. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Extensive first-pass glucuronidation; oral F ~24% vs IV; active metabolite M6G.",
            "Opioid; this is an educational PK teaching example, not a dosing recommendation.",
            "Renal impairment can cause M6G accumulation with prolonged opioid effect.",
        ],
    },
    "atorvastatin": {
        "name": "Atorvastatin",
        "smiles": "CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O",
        "route": "oral",
        "teaching_dose_mg": 10.0,
        "approximate_half_life_h": 14.0,
        "approximate_f": 0.12,
        "approximate_vd_l_kg": 5.4,
        "approximate_ka_per_h": 0.5,
        "approximate_kel_per_h": 0.050,
        "source_note": (
            "Approximate teaching values. Atorvastatin has very low bioavailability due to first-pass. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Very low oral F (~12%) due to extensive first-pass hepatic metabolism (CYP3A4).",
            "OATP1B1 substrate: transporter polymorphisms and drug interactions alter systemic exposure.",
            "Pharmacological effect (HMG-CoA inhibition) occurs in liver, where concentrations are high.",
        ],
    },
    "simvastatin": {
        "name": "Simvastatin",
        "smiles": "CCC(C)(C)C(=O)OC1CC(C)C=C2C=CC(C)C(CCC3CC(O)CC(=O)O3)C21",
        "route": "oral",
        "teaching_dose_mg": 20.0,
        "approximate_half_life_h": 2.0,
        "approximate_f": 0.05,
        "approximate_vd_l_kg": 3.5,
        "approximate_ka_per_h": 0.5,
        "approximate_kel_per_h": 0.35,
        "source_note": (
            "Approximate teaching values for the lactone prodrug. Simvastatin is a prodrug. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Prodrug hydrolyzed to active acid form in vivo; systemic F is very low (~5%).",
            "CYP3A4 substrate; concurrent use with strong inhibitors increases myopathy risk.",
            "Compare to atorvastatin for statin-class PK diversity teaching.",
        ],
    },
    "losartan": {
        "name": "Losartan",
        "smiles": "CCCCc1nc(Cl)c(CO)n1Cc1ccc(-c2ccccc2-c2nn[nH]n2)cc1",
        "route": "oral",
        "teaching_dose_mg": 50.0,
        "approximate_half_life_h": 2.0,
        "approximate_f": 0.33,
        "approximate_vd_l_kg": 0.49,
        "approximate_ka_per_h": 0.8,
        "approximate_kel_per_h": 0.35,
        "source_note": (
            "Approximate teaching values. Losartan is a prodrug converted to active metabolite E-3174. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Prodrug: converted to active metabolite E-3174 (carboxylic acid) by CYP2C9/3A4.",
            "E-3174 has a longer half-life (~6-9 h) and contributes most pharmacological activity.",
            "CYP2C9 polymorphism affects active metabolite formation.",
        ],
    },
    "ciprofloxacin": {
        "name": "Ciprofloxacin",
        "smiles": "O=C(O)c1cn(C2CC2)c2cc(N3CCNCC3)c(F)cc2c1=O",
        "route": "oral",
        "teaching_dose_mg": 500.0,
        "approximate_half_life_h": 4.0,
        "approximate_f": 0.69,
        "approximate_vd_l_kg": 2.5,
        "approximate_ka_per_h": 0.8,
        "approximate_kel_per_h": 0.17,
        "source_note": (
            "Approximate teaching values. Ciprofloxacin has adequate oral bioavailability for a fluoroquinolone. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Divalent cation chelation (calcium, magnesium, zinc) reduces absorption; separate from antacids.",
            "CYP1A2 inhibitor; theophylline and caffeine interactions are clinically relevant.",
            "Wide tissue distribution (Vd ~2.5 L/kg); higher tissue concentrations vs plasma.",
        ],
    },
    "azithromycin": {
        "name": "Azithromycin",
        "smiles": "CCC1OC(=O)C(C)C(OC2CC(C)(OC)C(O)C(C)O2)C(C)C(OC2OC(C)CC(N(C)C)C2O)C(C)(O)CC(C)CN(C)C(C)C(O)C1(C)O",
        "route": "oral",
        "teaching_dose_mg": 500.0,
        "approximate_half_life_h": 68.0,
        "approximate_f": 0.37,
        "approximate_vd_l_kg": 31.0,
        "approximate_ka_per_h": 0.5,
        "approximate_kel_per_h": 0.010,
        "source_note": (
            "Approximate teaching values. Azithromycin has extreme tissue distribution. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Very large Vd (~31 L/kg) due to extensive tissue binding; plasma T½ (~68 h) reflects slow redistribution.",
            "Tissue concentration may far exceed plasma; short clinical courses despite long T½.",
            "QT-prolongation risk; use as teaching example for Vd influence on half-life.",
        ],
    },
    "prednisone": {
        "name": "Prednisone",
        "smiles": "CC12C=CC(=O)C=C1CCC1C2C(=O)CC2(C)C1CCC2(O)C(=O)CO",
        "route": "oral",
        "teaching_dose_mg": 10.0,
        "approximate_half_life_h": 1.0,
        "approximate_f": 0.80,
        "approximate_vd_l_kg": 0.5,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.69,
        "source_note": (
            "Approximate teaching values for the prodrug prednisone. Converted to prednisolone in vivo. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "Prodrug: prednisone is converted to active prednisolone (T½ ~3 h) by 11-beta-HSD.",
            "Pharmacological effect duration exceeds PK half-life; anti-inflammatory effect persists.",
            "High-dose, chronic use has HPA axis suppression considerations (not relevant to PK simulation).",
        ],
    },
    "glipizide": {
        "name": "Glipizide",
        "smiles": "Cc1cncc(CCC(=O)NS(=O)(=O)c2ccc(NC(=O)NCC3CCCCC3)cc2)c1",
        "route": "oral",
        "teaching_dose_mg": 5.0,
        "approximate_half_life_h": 3.5,
        "approximate_f": 0.90,
        "approximate_vd_l_kg": 0.17,
        "approximate_ka_per_h": 1.0,
        "approximate_kel_per_h": 0.20,
        "source_note": (
            "Approximate teaching values for glipizide, a second-generation sulfonylurea. "
            "Verify against primary literature before scientific use."
        ),
        "citation": "Rowland & Tozer, Clinical Pharmacokinetics and Pharmacodynamics (verify edition).",
        "warning_notes": [
            "High protein binding (>98%); drug interactions at albumin binding site are relevant.",
            "CYP2C9 substrate; enzyme inhibitors can increase exposure and hypoglycemia risk.",
            "Extended-release formulations markedly alter the absorption rate profile.",
        ],
    },
}

DRUG_PROFILE_NAMES = list(DRUG_PK_PROFILES.keys())


# ---------------------------------------------------------------------------
# Literature F reference values
# These are SEPARATE from the educational scenario F used in the PK simulator.
# The Caco-2 model does NOT predict these values.
# ---------------------------------------------------------------------------
_F_LITERATURE: dict[str, dict] = {
    "aspirin": {
        "f_literature": 0.60,
        "f_literature_range": "0.50–0.68 (formulation- and endpoint-dependent)",
        "f_literature_note": (
            "Aspirin F is highly variable because intact aspirin is rapidly hydrolysed to salicylate "
            "pre-systemically and in the gut wall. Measured F reflects the intact aspirin fraction, "
            "not total salicylate. Enteric-coated vs. non-coated formulations differ substantially. "
            "This illustrates why Caco-2 permeability alone cannot predict F."
        ),
    },
    "caffeine": {
        "f_literature": 1.00,
        "f_literature_range": "~1.0 (essentially complete absorption in most subjects)",
        "f_literature_note": (
            "Caffeine is generally treated as essentially completely orally bioavailable. "
            "High passive permeability and high aqueous solubility contribute to near-complete absorption. "
            "A Caco-2-based educational scenario should not override this known literature value."
        ),
    },
    "ibuprofen": {
        "f_literature": 0.80,
        "f_literature_range": "~0.80 (well-absorbed oral NSAID)",
        "f_literature_note": "High permeability and solubility support near-complete absorption. High protein binding does not affect F directly.",
    },
    "metformin": {
        "f_literature": 0.50,
        "f_literature_range": "0.40–0.60 (dose- and transporter-dependent)",
        "f_literature_note": (
            "Metformin absorption is transporter-mediated (OCT1, PMAT). Passive permeability is low. "
            "This is the paradigm case where Caco-2 passive permeability alone predicts low absorption "
            "but the drug is clinically effective because of active transport. "
            "The Caco-2 scenario F will underestimate the true F."
        ),
    },
    "propranolol": {
        "f_literature": 0.26,
        "f_literature_range": "0.20–0.35 (high first-pass extraction)",
        "f_literature_note": (
            "High permeability BUT low F due to extensive hepatic first-pass extraction. "
            "This illustrates that high Caco-2 permeability does not guarantee high F "
            "when first-pass metabolism is substantial."
        ),
    },
    "atenolol": {
        "f_literature": 0.50,
        "f_literature_range": "~0.50 (low permeability, moderate F via paracellular route)",
        "f_literature_note": "Low passive transcellular permeability; absorption partly via paracellular pathway. Caco-2 may underpredict F.",
    },
    "warfarin": {
        "f_literature": 0.93,
        "f_literature_range": "~0.90–0.97 (near-complete oral absorption)",
        "f_literature_note": "High permeability and high protein binding; F is near-complete. CYP2C9 metabolism affects clearance, not F.",
    },
    "diazepam": {
        "f_literature": 1.00,
        "f_literature_range": "~1.0 (essentially complete absorption)",
        "f_literature_note": "High lipophilicity and near-complete oral absorption. Long half-life due to high Vd.",
    },
    "midazolam": {
        "f_literature": 0.44,
        "f_literature_range": "0.30–0.50 (CYP3A4 first-pass extraction)",
        "f_literature_note": "Classic CYP3A4 probe substrate. High permeability but moderate F due to first-pass intestinal and hepatic CYP3A4.",
    },
    "omeprazole": {
        "f_literature": 0.50,
        "f_literature_range": "0.35–0.65 (CYP2C19-dependent, enteric coating)",
        "f_literature_note": "F is highly variable due to CYP2C19 polymorphism and acid-labile prodrug activation.",
    },
    "acetaminophen": {
        "f_literature": 0.88,
        "f_literature_range": "0.85–0.98 (well-absorbed)",
        "f_literature_note": "High oral bioavailability; primarily glucuronidation and sulfation at therapeutic doses.",
    },
    "morphine": {
        "f_literature": 0.24,
        "f_literature_range": "0.20–0.40 (extensive first-pass glucuronidation)",
        "f_literature_note": "Demonstrates that good permeability does not guarantee high F when first-pass metabolism is extensive.",
    },
    "atorvastatin": {
        "f_literature": 0.12,
        "f_literature_range": "~0.12 (very low first-pass F)",
        "f_literature_note": "Very low F despite moderate permeability; CYP3A4 and intestinal first-pass metabolism are the main determinants.",
    },
}

# Enrich each profile with literature F data where available
for _key, _fdata in _F_LITERATURE.items():
    if _key in DRUG_PK_PROFILES:
        DRUG_PK_PROFILES[_key].update({
            "f_literature": _fdata["f_literature"],
            "f_literature_range": _fdata["f_literature_range"],
            "f_literature_note": _fdata["f_literature_note"],
            "profile_type": "literature teaching preset",
        })

# Ensure all profiles that were not enriched have the profile_type field
for _key in DRUG_PK_PROFILES:
    DRUG_PK_PROFILES[_key].setdefault("profile_type", "literature teaching preset")
    DRUG_PK_PROFILES[_key].setdefault("f_literature", None)
    DRUG_PK_PROFILES[_key].setdefault("f_literature_range", None)
    DRUG_PK_PROFILES[_key].setdefault("f_literature_note", "Verify against primary literature before scientific use.")
