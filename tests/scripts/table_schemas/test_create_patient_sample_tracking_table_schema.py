import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from synapseclient import Column, Schema, Table

from scripts.table_schemas import create_patient_sample_tracking_table_schema as create_schema


@pytest.mark.parametrize(
    "validation_rule,expected",
    [
        ("bool", "BOOLEAN"),
        ("int", "INTEGER"),
        ("float", "DOUBLE"),
        ("date", "DATE"),
        ("str", "STRING"),
        (None, "STRING"),  # NaN case
    ],
)
def test_get_synapse_col_type_valid(validation_rule, expected):
    if validation_rule is None:
        rule = pd.NA
    else:
        rule = validation_rule
    assert create_schema.get_synapse_col_type(rule) == expected


def test_get_synapse_col_type_invalid():
    with pytest.raises(ValueError, match="is not one of the supported rules"):
        create_schema.get_synapse_col_type("unsupported")


def test_create_columns_with_enum_values():
    data = pd.DataFrame(
        {
            "Attribute": ["COL1", "COL2"],
            "Validation Rules": ["int", "str"],
            "Valid Values": [pd.NA, "A, B, C"],
        }
    )

    columns = create_schema.create_columns(data)

    assert isinstance(columns, list)
    assert len(columns) == 2

    # Validate column properties
    col1 = columns[0]
    col2 = columns[1]

    assert col1.name == "COL1"
    assert col1.columnType == "INTEGER"
    assert col1.enumValues is None

    assert col2.name == "COL2"
    assert col2.columnType == "STRING"
    assert col2.enumValues == ["A", "B", "C"]


def test_create_schema(monkeypatch):
    mock_syn = MagicMock()
    fake_schema = MagicMock(id="syn999", name="FakeSchema")

    with patch.object(create_schema, "syn", mock_syn):
        mock_syn.store.return_value = fake_schema

        result = create_schema.create_schema(
            project_synid="synProject1",
            columns=[Column(name="test", columnType="STRING")],
            table_name="FakeTable",
        )

        mock_syn.store.assert_called_once()
        assert result.id == "syn999"
        assert result.name == "FakeSchema"


def test_create_table(monkeypatch, tmp_path):
    """Test full create_table flow with mocked Synapse and CSV file."""

    # Mock a fake TSV file
    tsv_file = tmp_path / "fake_model.tsv"
    tsv_file.write_text("Attribute\tValidation Rules\tValid Values\nCOL1\tint\t1,2,3\n")

    mock_syn = MagicMock()
    mock_syn.get.return_value.path = str(tsv_file)

    mock_schema = MagicMock(id="synTableSchema", name="TestSchema")
    mock_table = MagicMock(schema=mock_schema, id="synTable123")

    # Patch everything inside the function scope
    with patch.object(create_schema, "syn", mock_syn), \
         patch.object(create_schema, "Schema", MagicMock(return_value=mock_schema)), \
         patch.object(create_schema, "Table", MagicMock(return_value=mock_table)), \
         patch("pandas.read_csv", return_value=pd.read_csv(tsv_file, sep="\t")):

        # Mock Synapse store returning schema or table
        mock_syn.store.side_effect = [mock_schema, mock_table]

        create_schema.create_table(
            data_model_synid="synDataModel",
            project_synid="synProject",
            table_name="TestTable",
        )

        # Ensure we fetched and stored things properly
        mock_syn.get.assert_called_once_with("synDataModel")
        assert mock_syn.store.call_count == 2  # one for schema, one for table


def test_get_data_model(monkeypatch, tmp_path):
    """Tests reading TSV via mocked syn.get() and pandas.read_csv"""
    fake_tsv = tmp_path / "model.tsv"
    fake_tsv.write_text("Attribute\tValidation Rules\nCOL1\tint\n")

    mock_syn = MagicMock()
    mock_syn.get.return_value.path = str(fake_tsv)

    with patch.object(create_schema, "syn", mock_syn):
        df = create_schema.get_data_model("syn123")
        assert isinstance(df, pd.DataFrame)
        assert "COL1" in df["Attribute"].values
