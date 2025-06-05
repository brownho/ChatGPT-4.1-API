# ChatGPT-4.1 API

This project provides a simple Streamlit UI for interacting with the ChatGPT 4.1 model.

The application also includes a utility for working with **Power BI** reports. Upload a `.pbix` file in the sidebar to extract the report's data model and layout as JSON. The extracted JSON can be downloaded, reviewed in the browser, or sent directly to ChatGPT for modification using the **Send PBIX JSON to ChatGPT** button. ChatGPT can inspect the JSON with the `get_pbix_json` tool and update it using the `update_pbix_json` tool. This makes it possible to ask questions about the uploaded report or instruct the assistant to add new measures or visuals to the file.

## Computer Use Mode

The interface now includes an optional **computer use** mode. When enabled in the
sidebar settings, ChatGPT can execute shell commands on your machine using the
`run_command` tool and display the output in the chat.

Use this mode with caution as it will run commands locally with the privileges
of the current user.

## PBIX Editing Tools

When a Power BI report is uploaded, ChatGPT can analyze or modify the extracted
JSON by calling several tools:

* `get_pbix_json` – returns the current PBIX JSON so the assistant can inspect
  it and answer questions about the report.
* `update_pbix_json` – accepts a complete JSON string and replaces the stored
  report data with the new version.
* `add_dax_measure` – create or update a DAX measure in the `DataModelSchema`.
* `create_relationship` – define a relationship between two tables.
* `add_visual` – append a new visual definition to the `Layout` of the report.
* `update_power_query` – modify or add a Power Query (M) script in the report metadata.
* `add_data_source` – register a new data source definition.
* `set_parameter` – create or update a query parameter value.
* `set_refresh_policy` – configure refresh policy details.
* `preview_table` – return sample rows from a table for inspection.
* `run_dax_query` – run a limited DAX query for debugging purposes.

The parsed data is saved in the session so you can continue editing or
download the updated JSON from the sidebar.
