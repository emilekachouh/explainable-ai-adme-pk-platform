import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from adme_predictor.data import preprocess_caco2_wang
from adme_predictor.modeling import build_feature_matrix, make_single_feature_row


def test_dataset_preprocessing_validates_and_deduplicates_rows():
    raw = pd.DataFrame(
        {
            "smiles": ["CCO", "OCC", "", "not_a_smiles"],
            "caco2_log_papp": [-5.0, -4.0, -6.0, -7.0],
        }
    )

    processed = preprocess_caco2_wang(raw)

    assert len(processed) == 1
    assert processed.loc[0, "canonical_smiles"] == "CCO"
    assert processed.loc[0, "caco2_log_papp"] == -4.5
    assert "permeability_class" in processed.columns


def test_feature_matrix_shape_matches_rows_and_expected_features():
    df = pd.DataFrame(
        {
            "canonical_smiles": ["CCO", "CC(=O)OC1=CC=CC=C1C(=O)O"],
            "permeability_class": [1, 0],
            "caco2_log_papp": [-4.5, -5.5],
        }
    )

    X, columns = build_feature_matrix(df)

    assert X.shape[0] == 2
    assert X.shape[1] == len(columns)
    assert "molecular_weight" in columns
    assert "morgan_2047" in columns


def test_prediction_feature_row_aligns_to_training_columns():
    df = pd.DataFrame({"canonical_smiles": ["CCO"]})
    _, columns = build_feature_matrix(df)

    row = make_single_feature_row("CCO", columns)

    assert row.shape == (1, len(columns))


def test_prediction_output_shape_is_single_label_and_probability():
    df = pd.DataFrame(
        {
            "canonical_smiles": ["CCO", "CC(=O)OC1=CC=CC=C1C(=O)O", "Cn1cnc2c1c(=O)n(C)c(=O)n2C"],
            "permeability_class": [1, 0, 1],
        }
    )
    X, columns = build_feature_matrix(df)
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    model.fit(X, df["permeability_class"])

    row = make_single_feature_row("CCO", columns)
    prediction = model.predict(row)
    probability = model.predict_proba(row)

    assert prediction.shape == (1,)
    assert probability.shape == (1, 2)
