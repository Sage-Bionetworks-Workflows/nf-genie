import importlib
from unittest.mock import MagicMock, patch

from synapseclient.models import Column

from scripts.table_schemas import (
    create_patient_sample_tracking_table_schema as create_schema,
)


def test_create_columns_returns_expected_number_and_types():
    cols = create_schema.create_columns()

    # Expect: 2 string id cols + all BOOLEAN_COLS + (STRING_COLS minus SAMPLE_ID/PATIENT_ID duplicates)
    expected_len = (
        2 + len(create_schema.BOOLEAN_COLS) + (len(create_schema.STRING_COLS) - 2)
    )
    assert isinstance(cols, list)
    assert len(cols) == expected_len

    # Verify all are synapseclient.models.Column
    assert all(isinstance(c, Column) for c in cols)

    # Verify order: SAMPLE_ID, PATIENT_ID first
    assert cols[0].name == "SAMPLE_ID"
    assert cols[0].column_type == "STRING"
    assert cols[0].maximum_size == 250

    assert cols[1].name == "PATIENT_ID"
    assert cols[1].column_type == "STRING"
    assert cols[1].maximum_size == 250

    # Verify booleans next, exactly in BOOLEAN_COLS order
    bool_slice = cols[2 : 2 + len(create_schema.BOOLEAN_COLS)]
    assert [c.name for c in bool_slice] == create_schema.BOOLEAN_COLS
    assert all(c.column_type == "BOOLEAN" for c in bool_slice)

    # Verify final string release cols in STRING_COLS order excluding SAMPLE_ID/PATIENT_ID
    expected_release_cols = [
        c for c in create_schema.STRING_COLS if c not in ("SAMPLE_ID", "PATIENT_ID")
    ]
    release_slice = cols[2 + len(create_schema.BOOLEAN_COLS) :]
    assert [c.name for c in release_slice] == expected_release_cols
    assert all(c.column_type == "STRING" for c in release_slice)
    assert all(c.maximum_size == 250 for c in release_slice)


def test_create_columns_has_no_duplicate_column_names():
    cols = create_schema.create_columns()
    names = [c.name for c in cols]
    assert len(names) == len(set(names)), "Duplicate column names found in schema"


def test_create_table(monkeypatch, tmp_path):
    """Test create_table flow with mocked Synapse login and Table.store(), using the old-style mocks."""

    # Mock a fake TSV file (kept for parity with the old test; new code won't read it)
    tsv_file = tmp_path / "fake_model.tsv"
    tsv_file.write_text("Attribute\tValidation Rules\tValid Values\nCOL1\tint\t1,2,3\n")

    # Mock syn object returned by synapseclient.login()
    mock_syn = MagicMock()
    mock_syn.get.return_value.path = str(tsv_file)

    # Mock schema/table objects (same as old test)
    mock_schema = MagicMock(id="synTableSchema", name="TestSchema")
    mock_table = MagicMock(schema=mock_schema, id="synTable123", name="TestTable")

    # Make store() return an object with name/id so print() formatting doesn't break
    mock_table.store.return_value = MagicMock(name="TestTable", id="synTable123")

    # IMPORTANT: Patch login BEFORE importing the module (module logs in at import time)
    with patch("synapseclient.login", return_value=mock_syn):
        from scripts.table_schemas import (
            create_patient_sample_tracking_table_schema as create_schema,
        )

        importlib.reload(create_schema)

        # Patch Table constructor to return our mock_table
        with patch.object(
            create_schema, "Table", MagicMock(return_value=mock_table)
        ) as mock_table_cls:
            create_schema.create_table(
                project_synid="synProject",
                table_name="TestTable",
            )

            # Assert Table(...) was created correctly
            mock_table_cls.assert_called_once()
            _, kwargs = mock_table_cls.call_args
            assert kwargs["name"] == "TestTable"
            assert kwargs["parent_id"] == "synProject"
            assert isinstance(kwargs["columns"], list)
            assert len(kwargs["columns"]) > 0

            # Assert store was called exactly once
            assert mock_table.store.call_count == 1


def test_constants_are_consistent():
    """
    Sanity checks for constants: required columns present and no obvious naming issues.
    """
    assert "SAMPLE_ID" in create_schema.STRING_COLS
    assert "PATIENT_ID" in create_schema.STRING_COLS

    # All boolean flags should start with IN_
    assert all(name.startswith("IN_") for name in create_schema.BOOLEAN_COLS)

    # Release columns (string) should not overlap with boolean columns
    overlap = set(create_schema.STRING_COLS) & set(create_schema.BOOLEAN_COLS)
    assert overlap == set(), f"STRING_COLS and BOOLEAN_COLS overlap: {overlap}"
