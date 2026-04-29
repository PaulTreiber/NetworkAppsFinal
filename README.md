# REF620 Modbus Client

Windows-based educational Modbus TCP client for the ABB REF620 ANSI feeder protection relay.

## Project Status

This repository is scaffolded for the COMPENG 3510 final project. It includes:

- assignment documents and ABB reference manuals
- starter Python package layout
- folders for Wireshark captures, screenshots, and prompt logs
- a basic entry point for the application

## Repository Layout

```text
docs/
  assignment/     Project brief and extracted notes
  references/     ABB manuals and reference material
artifacts/
  captures/       Wireshark capture files
  screenshots/    Annotated screenshots for report/presentation
  prompt-log/     AI prompt log and decision notes
src/
  ref620_modbus_client/
    app.py
    config.py
    modbus.py
    points.py
tests/
```

## Getting Started

1. Install Python 3.11 or newer on Windows.
2. Create and activate a virtual environment.
3. Install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements.txt
```

4. Run the starter app:

```powershell
python -m ref620_modbus_client.app
```

## Planned Features

- Modbus TCP read support for REF620 points
- engineering-value scaling and decoding
- multi-point polling
- bounded control write workflow
- small Windows GUI for read/write inspection
- request/response hex display for Wireshark comparison

## Documentation Checklist

- Put Wireshark captures in [artifacts/captures](/C:/Users/posca/OneDrive/Documents/New%20project/artifacts/captures).
- Put screenshots in [artifacts/screenshots](/C:/Users/posca/OneDrive/Documents/New%20project/artifacts/screenshots).
- Keep prompt history in [artifacts/prompt-log](/C:/Users/posca/OneDrive/Documents/New%20project/artifacts/prompt-log).

## Notes

- `git` does not appear to be installed in this environment yet, so I could not initialize the repository locally.
- The ABB manuals and assignment brief are already organized under `docs/`.

test test
