import pandas as pd
import glob
from src.features.build_features import FeatureBuilder

# =========== Integracion ==============

def test_main_build_features(tmp_path, monkeypatch):
    """
    Test para cubrir el main() completo de build_features.py
    incluyendo argparse, pipeline y guardado de artefactos.
    """

    import src.features.build_features as bf
    import sys
    import pandas as pd

    # Crear archivos temporales simulando datos limpios
    input_file = tmp_path / "cleaned.csv"
    output_file = tmp_path / "features.csv"
    encoder_dir = tmp_path / "encoders"
    preprocessor_dir = tmp_path / "preprocessors"

    df = pd.DataFrame({
        "Performance": ["Excellent", "Good", "Poor"],
        "Gender": ["MALE", "FEMALE", "MALE"],
        "Class_X_Percentage": [90, 80, 70]
    })
    df.to_csv(input_file, index=False)

    # Simular argumentos de consola
    fake_args = [
        "prog",
        "--input", str(input_file),
        "--output", str(output_file),
        "--encoder-dir", str(encoder_dir),
        "--preprocessor-dir", str(preprocessor_dir),
        "--no-encoding",     # para evitar OneHotEncoder
        "--no-feature-selection",
        "--no-pca"
    ]

    monkeypatch.setattr(sys, "argv", fake_args)

    # Ejecutar main()
    bf.main()

    # Validar salida
    assert output_file.exists()

def test_feature_builder_pipeline(tmp_path):
    # === 1. Crear un CSV temporal con datos realistas ===
    input_file = tmp_path / "cleaned.csv"
    output_file = tmp_path / "features.csv"
    encoder_dir = tmp_path / "encoders"
    preprocessor_dir = tmp_path / "preprocessors"

    df = pd.DataFrame({
        "Performance": ["Excellent", "Good", "Poor"],
        "Gender": ["MALE", "FEMALE", "MALE"],
        "Caste": ["General", "OBC", "SC"],
        "Class_X_Percentage": [90, 80, 70],
        "coaching": ["NO", "WA", "OA"],
        "twelve_education": ["AHSEC", "CBSE", "AHSEC"],
        "time": ["ONE", "TWO", "TWO"],
        "medium": ["ENGLISH", "OTHER", "ENGLISH"],
        "Father_occupation": ["DOCTOR", "BUSINESS", "TEACHER"],
        "Mother_occupation": ["HOUSE_WIFE", "HOUSE_WIFE", "OTHER"],
        "Class_ten_education": ["SEBA", "SEBA", "CBSE"]
    })

    df.to_csv(input_file, index=False)

    # === 2. Crear FeatureBuilder ===
    builder = FeatureBuilder(
        input_path=input_file,
        output_path=output_file,
        encoder_dir=encoder_dir,
        preprocessor_dir=preprocessor_dir,
    )

    # === 3. Ejecutar pipeline ===
    X = builder.run_pipeline(
        feature_selection=True,
        apply_encoding=True,
        apply_pca=True,
        variance_threshold=0.95,
    )

    # === 4. Guardar features y artefactos ===
    builder.save_features()
    builder.save_artifacts()

    # ==================== VALIDACIONES ====================
    assert isinstance(X, pd.DataFrame)
    assert len(X) > 0
    assert output_file.exists()

    # === Artefactos ===
    encoder_files = glob.glob(str(encoder_dir / "*.pkl"))
    preprocessor_files = glob.glob(str(preprocessor_dir / "*.pkl"))

    # No debe haber encoder porque no quedan columnas categóricas
    assert len(encoder_files) == 0

    # Debe haber PCA guardado
    assert len(preprocessor_files) > 0

# =========== Unitarios ==============

def test_onehot_encode_basic():
    from src.features.build_features import FeatureBuilder
    import pandas as pd

    # DataFrame con nominales
    df = pd.DataFrame({
        "Performance": ["Excellent", "Good", "Poor"],
        "Gender": ["MALE", "FEMALE", "MALE"],
        "Caste": ["General", "OBC", "SC"],
    })

    builder = FeatureBuilder("in.csv", "out.csv", "enc/", "prep/")
    builder.df = df.copy()

    # Nominales a codificar
    nominal_features = ["Gender", "Caste"]

    result = builder.onehot_encode(nominal_features, drop_original=True)

    # Validaciones
    assert isinstance(result, pd.DataFrame)

    # Las columnas originales deben haber desaparecido
    assert "Gender" not in result.columns
    assert "Caste" not in result.columns

    # Deben existir columnas codificadas
    encoded_cols = [c for c in result.columns if c.startswith("Gender_") or c.startswith("Caste_")]
    assert len(encoded_cols) > 0

    # Debe tener misma cantidad de filas
    assert len(result) == len(df)

def test_onehot_encode_no_valid_columns():
    from src.features.build_features import FeatureBuilder
    import pandas as pd

    df = pd.DataFrame({
        "Performance": ["Excellent", "Good"],
        "Age": [20, 21]   # no es nominal
    })

    builder = FeatureBuilder("in.csv", "out.csv", "enc/", "prep/")
    builder.df = df.copy()

    # Pasar columnas que NO existen ni son nominales
    result = builder.onehot_encode(["Gender", "Caste"])

    # No debe codificar nada
    assert result.equals(df)

    # No debe cambiar columnas
    assert list(result.columns) == list(df.columns)
