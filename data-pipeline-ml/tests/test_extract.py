from src.etl.extract import extract_csv


def test_extract_csv_reads_required_columns():
    payload = b"feature_1,feature_2,feature_3,target\n1,2,3,4\n"
    dataframe = extract_csv(payload)
    assert list(dataframe.columns) == ["feature_1", "feature_2", "feature_3", "target"]
