import io
import json
import zipfile
from typing import Dict, Any

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


def add_dax_measure(data: Dict[str, Any], table_name: str, measure_name: str, expression: str) -> Dict[str, Any]:
    """Add or update a DAX measure in the DataModelSchema."""
    schema = data.setdefault("DataModelSchema", {})
    model = schema.setdefault("model", {})
    tables = model.setdefault("tables", [])
    for table in tables:
        if table.get("name") == table_name:
            measures = table.setdefault("measures", [])
            for m in measures:
                if m.get("name") == measure_name:
                    m["expression"] = expression
                    return data
            measures.append({"name": measure_name, "expression": expression})
            return data
    # Table not found - create simple table with the new measure
    tables.append({
        "name": table_name,
        "columns": [],
        "measures": [{"name": measure_name, "expression": expression}],
    })
    return data


def create_relationship(data: Dict[str, Any], from_table: str, from_column: str, to_table: str, to_column: str) -> Dict[str, Any]:
    """Create a simple relationship between two tables."""
    schema = data.setdefault("DataModelSchema", {})
    model = schema.setdefault("model", {})
    relationships = model.setdefault("relationships", [])
    relationships.append({
        "fromTable": from_table,
        "fromColumn": from_column,
        "toTable": to_table,
        "toColumn": to_column,
        "crossFilteringBehavior": "bothDirections",
    })
    return data


def add_visual(data: Dict[str, Any], page_index: int, visual: Dict[str, Any]) -> Dict[str, Any]:
    """Append a new visual definition to a layout page."""
    layout = data.setdefault("Layout", {})
    sections = layout.setdefault("sections", [])
    if page_index < 0 or page_index >= len(sections):
        raise IndexError("Invalid page index")
    page = sections[page_index]
    containers = page.setdefault("visualContainers", [])
    containers.append(visual)
    return data


def update_power_query(data: Dict[str, Any], query_name: str, script: str) -> Dict[str, Any]:
    """Add or update an M script in the Metadata section."""
    metadata = data.setdefault("Metadata", {})
    queries = metadata.setdefault("queries", [])
    for q in queries:
        if q.get("name") == query_name:
            q["expression"] = script
            return data
    queries.append({"name": query_name, "expression": script})
    return data


def add_data_source(data: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Append a new data source definition to Metadata."""
    metadata = data.setdefault("Metadata", {})
    sources = metadata.setdefault("dataSources", [])
    sources.append(source)
    return data


def set_parameter(data: Dict[str, Any], param_name: str, value: Any) -> Dict[str, Any]:
    """Create or update a parameter value in Metadata."""
    metadata = data.setdefault("Metadata", {})
    parameters = metadata.setdefault("parameters", [])
    for p in parameters:
        if p.get("name") == param_name:
            p["currentValue"] = value
            return data
    parameters.append({"name": param_name, "currentValue": value})
    return data


def set_refresh_policy(data: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    """Set refresh policy details inside Metadata."""
    metadata = data.setdefault("Metadata", {})
    metadata["refreshPolicy"] = policy
    return data


def preview_table(data: Dict[str, Any], table_name: str, max_rows: int = 5) -> Any:
    """Return the first rows from a table if present."""
    schema = data.get("DataModelSchema", {})
    model = schema.get("model", {})
    tables = model.get("tables", [])
    for table in tables:
        if table.get("name") == table_name:
            rows = table.get("rows", [])
            if max_rows is None:
                return rows
            return rows[:max_rows]
    return []


def run_dax_query(data: Dict[str, Any], expression: str) -> Any:
    """Very small subset of DAX query capability for debugging."""
    expr = expression.strip().upper()
    if expr.startswith("ROWCOUNT(") and expr.endswith(")"):
        table = expr[len("ROWCOUNT(") : -1].strip()
        rows = preview_table(data, table, None)
        return len(rows)
    return "Query not supported"
