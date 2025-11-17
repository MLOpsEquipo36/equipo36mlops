import pandas as pd
from src.data.clean_data import DataCleaner
import os

# =========== Integracion ==============

def test_run_pipeline(): # Test para cubrir el main() completo de clean_data.py --> El df final posee todos los requisitos de limpieza
    # DataFrame
    df = pd.DataFrame({
        "Performance": ["Excellent", "Excellent", "Excellent"],
        "Gender": ["male", " MALE ", "male"],
        "Caste": ["General", "OBC", "OBC"],
        "coaching": ["NO", "WA", "OA"],
        "time": [" one ", "TWO", ""],
        "Class_ten_education": ["SEBA", "SEBA", "others"],
        "twelve_education": ["AHSEC", "AHSEC", "CBSE"],
        "medium": ["ENGLISH", "OTHERS", "ENGLISH"],
        "Class_ X_Percentage": ["Excellent", "Excellent", "Excellent"],
        "Class_XII_Percentage": ["Excellent", "Excellent", "Excellent"],
        "Father_occupation": ["DOCTOR", "SCHOOL_TEACHER", "BUSINESS"],
        "Mother_occupation": ["OTHERS", "HOUSE_WIFE", "HOUSE_WIFE"],
        "mixed_type_col": ["unknown", "666", "unknown"],
    })

    cleaner = DataCleaner(input_path="dummy.csv", output_path="dummy_out.csv")

    cleaner.load_data = lambda: df.copy()
    cleaner.df = df.copy()
    cleaned_df = cleaner.run_pipeline()

    assert isinstance(cleaned_df, pd.DataFrame)
    assert "Performance" in cleaned_df.columns
    assert all(not x.startswith(" ") and not x.endswith(" ") for x in cleaned_df["Gender"].astype(str))
    assert cleaned_df["Gender"].str.isupper().all()
    assert "mixed_type_col" not in cleaned_df.columns
    assert len(cleaned_df) > 0

# =========== Unitarios ==============

def test_load_data(tmp_path): # funcion load_data 80-90
    d = tmp_path / "data"
    d.mkdir()
    file = d / "test.csv"

    df_original = pd.DataFrame({
        "Performance": ["Excellent", "Good"],
        "Gender": ["MALE", "FEMALE"]
    })
    df_original.to_csv(file, index=False)
    cleaner = DataCleaner(input_path=file, output_path="dummy.csv")

    df_loaded = cleaner.load_data()

    assert isinstance(df_loaded, pd.DataFrame)
    assert len(df_loaded) == len(df_original)
    assert list(df_loaded.columns) == list(df_original.columns)

def test_save_cleaned_data(tmp_path): # funcion save_cleaned_data 260-273

    output_file = tmp_path / "processed" / "cleaned.csv"

    # df
    df_raw = pd.DataFrame({
        "Performance": ["Excellent", "Good", "Poor"],
        "Gender": ["MALE", "FEMALE", "MALE"]
    })

    df_cleaned = df_raw.iloc[:2]

    cleaner = DataCleaner(input_path="dummy.csv", output_path=output_file)

    cleaner.df_raw = df_raw.copy()
    cleaner.df = df_cleaned.copy()

    result_path = cleaner.save_cleaned_data()

    assert output_file.exists()
    assert result_path == output_file
    df_loaded = pd.read_csv(output_file)
    assert len(df_loaded) == 2

def test_handle_target_nulls(): # funcion handle_target_nulls 145
    df = pd.DataFrame({
        "Performance": ["Excellent", None, "Good"],
        "Gender": ["Male", "Female", "Male"]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()

    cleaned = cleaner.handle_target_nulls("Performance")

    # Performance = None
    assert len(cleaned) == 2
    assert cleaned["Performance"].isna().sum() == 0

def test_fill_ordinal_nulls(): # funcion fill_ordinal_nulls_with_mode 198-199
    df = pd.DataFrame({
        "Performance": ["Excellent", None, "Good"]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()

    cleaned = cleaner.fill_ordinal_nulls_with_mode(
        columns=["Performance"],
        fill_value="EXCELLENT"
    )

    assert cleaned["Performance"].isna().sum() == 0
    assert cleaned["Performance"].iloc[1] == "EXCELLENT"

def test_normalize_case():
    df = pd.DataFrame({
        "Gender": ["male", "FEmale", " MALE "],
        "Performance": ["excellent", "GOOD", " average "]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()
    cleaner.columns_to_normalize = ["Gender", "Performance"]

    cleaned = cleaner.normalize_case()

    assert cleaned["Gender"].str.isupper().all()
    assert cleaned["Performance"].str.isupper().all()

def test_trim_whitespace():
    df = pd.DataFrame({
        "Gender": [" male ", "female ", "  male"],
        "medium": [" ENGLISH ", " HINDI ", "OTHER"]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()

    cleaned = cleaner.trim_whitespace()

    assert all(not x.startswith(" ") and not x.endswith(" ") for x in cleaned["Gender"])
    assert all(not x.startswith(" ") and not x.endswith(" ") for x in cleaned["medium"])

def test_replace_null_strings():
    df = pd.DataFrame({
        "Caste": ["NA", "null", "unknown", "OBC", None],
        "Gender": ["male", "NULL", "female", "n/a", "MALE"]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()

    cleaned = cleaner.replace_null_strings()

    assert cleaned.isna().sum().sum() >= 1

def test_drop_uninformative_columns():
    df = pd.DataFrame({
        "useful_col": [1, 2, 3],
        "mixed_type_col": ["a", 1, "b"]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()

    cleaned = cleaner.drop_uninformative_columns(["mixed_type_col"])

    assert "mixed_type_col" not in cleaned.columns

def test_rename_columns():
    df = pd.DataFrame({
        "Class_ X_Percentage": [80, 90],
        "Class_XII_Percentage": [85, 92]
    })

    cleaner = DataCleaner("dummy.csv", "dummy_out.csv")
    cleaner.df = df.copy()

    rename_dict = {"Class_ X_Percentage": "Class_X_Percentage"}
    cleaned = cleaner.rename_columns(rename_dict)

    assert "Class_X_Percentage" in cleaned.columns
    assert "Class_ X_Percentage" not in cleaned.columns
