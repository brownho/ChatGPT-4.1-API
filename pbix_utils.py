import io
import json
import zipfile


def process_pbix(pbix_bytes: bytes) -> dict:
    """Extract key JSON files from a PBIX archive."""
    result = {}
    try:
        with zipfile.ZipFile(io.BytesIO(pbix_bytes)) as zf:
            for name in zf.namelist():
                lower = name.lower()
                if lower.endswith("datamodelschema"):
                    result["DataModelSchema"] = json.loads(
                        zf.read(name).decode("utf-8", errors="ignore")
                    )
                elif lower.endswith("metadata"):
                    result["Metadata"] = json.loads(
                        zf.read(name).decode("utf-8", errors="ignore")
                    )
                elif lower.endswith("report/layout") or lower.endswith("layout"):
                    result["Layout"] = json.loads(
                        zf.read(name).decode("utf-8", errors="ignore")
                    )
    except Exception as e:
        result["error"] = str(e)
    return result


def package_pbix(data: dict) -> bytes:
    """Create a PBIX archive from a data dictionary."""
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        if "DataModelSchema" in data:
            zf.writestr("DataModelSchema", json.dumps(data["DataModelSchema"]))
        if "Metadata" in data:
            zf.writestr("Metadata", json.dumps(data["Metadata"]))
        if "Layout" in data:
            zf.writestr("Report/Layout", json.dumps(data["Layout"]))
    return bio.getvalue()
