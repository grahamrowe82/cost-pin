"""Flask application for the Unit Cost Pin utility."""
from __future__ import annotations

from typing import Dict, Optional, Tuple

from flask import Flask, render_template, request

from .logic import compute

app = Flask(__name__)

DEFAULTS = {
    "pr_in_1k": 0.003,
    "pr_out_1k": 0.015,
    "tok_in": 1500,
    "tok_out": 1000,
    "p": 0.8,
    "r": 1,
    "overhead": 1.15,
    "volume": 2000,
    "vps": 2.0,
}


def _format_input_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _parse_inputs(form) -> Tuple[Dict[str, Optional[float]], Dict[str, str]]:
    raw = {field: form.get(field, "") for field in DEFAULTS}
    numeric: Dict[str, Optional[float]] = {}
    display: Dict[str, str] = {}
    for field, default_value in DEFAULTS.items():
        value = raw[field].strip()
        if field == "vps" and value == "":
            numeric_value: Optional[float] = None
            display[field] = ""
        else:
            try:
                numeric_value = float(value) if value != "" else float(default_value)
            except ValueError:
                numeric_value = float(default_value)
            if field == "r" and numeric_value is not None:
                numeric_value = int(numeric_value)
            display[field] = value if value != "" else _format_input_value(default_value)
        numeric[field] = numeric_value
    return numeric, display


def format_currency(value) -> str:
    if value is None:
        return "—"
    magnitude = abs(value)
    if magnitude >= 10:
        decimals = 2
    elif magnitude >= 1:
        decimals = 3
    elif magnitude >= 0.1:
        decimals = 4
    else:
        decimals = 5
    return f"${value:,.{decimals}f}"


def format_number(value) -> str:
    if value is None:
        return "—"
    magnitude = abs(value)
    if magnitude >= 100:
        return f"{value:,.0f}"
    if magnitude >= 10:
        return f"{value:,.1f}"
    if magnitude >= 1:
        return f"{value:,.2f}"
    return f"{value:.4f}"


def format_percentage(value) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%"


@app.context_processor
def inject_formatters():
    return {
        "format_currency": format_currency,
        "format_number": format_number,
        "format_percentage": format_percentage,
    }


@app.get("/")
def index():
    numeric_inputs = DEFAULTS.copy()
    display_inputs = {field: _format_input_value(value) for field, value in DEFAULTS.items()}
    results = compute(**numeric_inputs)
    return render_template("index.html", inputs=display_inputs, results=results)


@app.post("/calc")
def calculate():
    numeric_inputs, display_inputs = _parse_inputs(request.form)
    results = compute(**numeric_inputs)
    return render_template("index.html", inputs=display_inputs, results=results)


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
