"""Pop-out dashboard for REF620 readings and manual extracts."""

import csv
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .points import TEST_POINT_GROUPS

DEFAULT_CSV_PATH = "artifacts/ref620_readings.csv"
MANUAL_TEXT_GLOB = "artifacts/ref620_points_page_*.txt"
POINT_LABELS = {
    point.name: point.label or point.name
    for points in TEST_POINT_GROUPS.values()
    for point in points
}


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_CSV_PATH)
    rows = _read_rows(csv_path)
    if not rows:
        raise SystemExit(f"No rows found in {csv_path}")

    root = tk.Tk()
    root.title("REF620 Modbus Dashboard")
    root.geometry("1060x720")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    _build_latest_tab(notebook, csv_path, rows[-1])
    _build_history_tab(notebook, rows)
    _build_points_tab(notebook)
    _build_manual_text_tab(notebook)

    root.mainloop()


def _build_latest_tab(parent: ttk.Notebook, csv_path: Path, latest: dict[str, str]) -> None:
    frame = ttk.Frame(parent, padding=16)
    parent.add(frame, text="Latest")

    ttk.Label(frame, text="Latest REF620 Readings", font=("Segoe UI", 16, "bold")).pack(
        anchor="w"
    )
    ttk.Label(frame, text=str(csv_path), font=("Segoe UI", 9)).pack(anchor="w")
    ttk.Label(frame, text=latest.get("timestamp_utc", ""), font=("Segoe UI", 10)).pack(
        anchor="w", pady=(0, 12)
    )

    table_frame = ttk.Frame(frame)
    table_frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(
        table_frame,
        columns=("value", "label"),
        show="tree headings",
        height=24,
    )
    tree.heading("#0", text="Point")
    tree.heading("value", text="Value")
    tree.heading("label", text="Manual Label")
    tree.column("#0", width=260)
    tree.column("value", width=140, anchor="e")
    tree.column("label", width=560)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for name, value in _numeric_values(latest):
        tree.insert("", "end", text=name, values=(f"{value:g}", POINT_LABELS.get(name, "")))


def _build_history_tab(parent: ttk.Notebook, rows: list[dict[str, str]]) -> None:
    frame = ttk.Frame(parent, padding=16)
    parent.add(frame, text="CSV History")

    ttk.Label(frame, text="Nested CSV Results", font=("Segoe UI", 16, "bold")).pack(
        anchor="w", pady=(0, 12)
    )

    tree = ttk.Treeview(frame, columns=("value", "label"), show="tree headings")
    tree.heading("#0", text="Timestamp / Point")
    tree.heading("value", text="Value")
    tree.heading("label", text="Manual Label")
    tree.column("#0", width=300)
    tree.column("value", width=140, anchor="e")
    tree.column("label", width=520)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for index, row in enumerate(rows, start=1):
        timestamp = row.get("timestamp_utc", f"row {index}")
        parent_id = tree.insert("", "end", text=timestamp, values=("", ""))
        for name, value in _numeric_values(row):
            tree.insert(
                parent_id,
                "end",
                text=name,
                values=(f"{value:g}", POINT_LABELS.get(name, "")),
            )
        tree.item(parent_id, open=index == len(rows))


def _build_points_tab(parent: ttk.Notebook) -> None:
    frame = ttk.Frame(parent, padding=16)
    parent.add(frame, text="Manual Points")

    ttk.Label(frame, text="Manual Point Labels and Test Groups", font=("Segoe UI", 16, "bold")).pack(
        anchor="w", pady=(0, 12)
    )

    tree = ttk.Treeview(
        frame,
        columns=("address", "type", "scale", "source", "description"),
        show="tree headings",
    )
    tree.heading("#0", text="Group / Label")
    tree.heading("address", text="Address")
    tree.heading("type", text="Type")
    tree.heading("scale", text="Scale")
    tree.heading("source", text="Manual Source")
    tree.heading("description", text="Description")
    tree.column("#0", width=280)
    tree.column("address", width=90)
    tree.column("type", width=70)
    tree.column("scale", width=70, anchor="e")
    tree.column("source", width=210)
    tree.column("description", width=360)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for group_name, points in TEST_POINT_GROUPS.items():
        group_id = tree.insert("", "end", text=group_name, values=("", "", "", "", ""))
        for point in points:
            address = str(point.address)
            if point.bit is not None:
                address = f"{point.address}:{point.bit}"
            tree.insert(
                group_id,
                "end",
                text=point.label or point.name,
                values=(
                    address,
                    point.data_type,
                    point.scale_factor,
                    point.source,
                    point.description,
                ),
            )
        tree.item(group_id, open=True)


def _build_manual_text_tab(parent: ttk.Notebook) -> None:
    frame = ttk.Frame(parent, padding=16)
    parent.add(frame, text="Manual Text")

    ttk.Label(frame, text="Extracted Manual Text Pages", font=("Segoe UI", 16, "bold")).pack(
        anchor="w", pady=(0, 12)
    )

    text = tk.Text(frame, wrap="word", font=("Consolas", 10))
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    files = sorted(Path(".").glob(MANUAL_TEXT_GLOB))
    if not files:
        text.insert(
            "end",
            "No extracted manual text files were found.\n\n"
            f"Expected files matching: {MANUAL_TEXT_GLOB}\n",
        )
        text.configure(state="disabled")
        return

    for path in files:
        text.insert("end", f"\n{'=' * 88}\n{path}\n{'=' * 88}\n\n")
        text.insert("end", path.read_text(encoding="utf-8", errors="replace"))
        text.insert("end", "\n")
    text.configure(state="disabled")


def _read_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def _numeric_values(row: dict[str, str]) -> list[tuple[str, float]]:
    values = []
    for key, raw_value in row.items():
        if key == "timestamp_utc" or raw_value == "":
            continue
        try:
            values.append((key, float(raw_value)))
        except ValueError:
            continue
    return values


if __name__ == "__main__":
    main()
