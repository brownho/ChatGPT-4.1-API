import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import zipfile

from pbix_utils import process_pbix, package_pbix

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
