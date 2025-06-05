import json
from typing import Dict, Any


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
