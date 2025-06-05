import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import zipfile

from pbix_utils import (
    process_pbix,
    package_pbix,
    update_power_query,
    add_data_source,
    set_parameter,
    set_refresh_policy,
    preview_table,
    run_dax_query,
)

sample_data = {
    "DataModelSchema": {"name": "model"},
    "Metadata": {"id": 1},
    "Layout": {"sections": []},
}


def create_sample_pbix_bytes():
    """Create a sample pbix file bytes for testing."""
    return package_pbix(sample_data)


def test_process_pbix_extracts_components():
    pbix_bytes = create_sample_pbix_bytes()
    extracted = process_pbix(pbix_bytes)
    assert extracted["DataModelSchema"] == sample_data["DataModelSchema"]
    assert extracted["Metadata"] == sample_data["Metadata"]
    assert extracted["Layout"] == sample_data["Layout"]


def test_package_pbix_creates_valid_archive():
    pbix_bytes = package_pbix(sample_data)
    with zipfile.ZipFile(io.BytesIO(pbix_bytes)) as zf:
        names = set(zf.namelist())
    assert "DataModelSchema" in names
    assert "Metadata" in names
    assert "Report/Layout" in names
    round_trip = process_pbix(pbix_bytes)
    assert round_trip == sample_data


def test_update_power_query_adds_script():
    data = {"Metadata": {"queries": []}}
    update_power_query(data, "Query1", "let x = 1 in x")
    assert data["Metadata"]["queries"][0]["name"] == "Query1"
    assert data["Metadata"]["queries"][0]["expression"] == "let x = 1 in x"


def test_add_data_source_appends_source():
    data = {}
    add_data_source(data, {"name": "src"})
    assert data["Metadata"]["dataSources"][0]["name"] == "src"


def test_set_parameter_updates_value():
    data = {}
    set_parameter(data, "Param", "Value")
    assert data["Metadata"]["parameters"][0]["currentValue"] == "Value"


def test_set_refresh_policy_stores_policy():
    data = {}
    set_refresh_policy(data, {"policy": "daily"})
    assert data["Metadata"]["refreshPolicy"]["policy"] == "daily"


def test_preview_table_and_run_dax_query():
    data = {
        "DataModelSchema": {
            "model": {"tables": [{"name": "T", "rows": [{"a": 1}, {"a": 2}]}]}
        }
    }
    rows = preview_table(data, "T", 1)
    assert rows == [{"a": 1}]
    count = run_dax_query(data, "ROWCOUNT(T)")
    assert count == 2
