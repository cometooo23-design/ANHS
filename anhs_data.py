"""Load, save, and normalize ANHS dashboard data (used by app.py)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "school_data.json"

GRADES = ["G7", "G8", "G9", "G10", "G11", "G12"]
SUBJECTS = [
    "Filipino",
    "English",
    "Math",
    "Science",
    "Aral. Pan.",
    "TLE",
    "MAPEH",
    "ESP",
    "SHS",
]
SEAT_GROUPS = ["Grade 7 & 8", "Grade 9 & 10", "Grade 11 & 12"]


def recompute_transitions(years: list[str], enrollment: dict[str, Any]) -> list[dict[str, Any]]:
    """G10 completers (year Y) vs G11 enrollees (year Y+1)."""
    out: list[dict[str, Any]] = []
    for i in range(1, len(years)):
        y0, y1 = years[i - 1], years[i]
        g10 = _grade_total(enrollment, y0, "G10")
        g11 = _grade_total(enrollment, y1, "G11")
        pct = round(g11 / g10 * 100, 1) if g10 else 0.0
        label = f"{y0[2:4]}-{y0[7:9]}→{y1[2:4]}-{y1[7:9]}"
        out.append({"label": label, "g10": g10, "g11": g11, "pct": pct})
    return out


def _grade_total(enrollment: dict, year: str, grade: str) -> int:
    row = enrollment.get(year, {}).get(grade, {})
    return int(row.get("m", 0)) + int(row.get("f", 0))


def empty_year_bundle(year: str) -> dict[str, Any]:
    return {
        "enrollment": {g: {"m": 0, "f": 0} for g in GRADES},
        "promoRates": {
            **{g: {"m": 0.0, "f": 0.0} for g in GRADES},
            "total": {"m": 0.0, "f": 0.0},
        },
        "dropout": {"male": 0, "female": 0},
        "lwd": 0,
        "insights": [],
        "recommendations": [],
    }


def normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Ensure every year has required keys; refresh transition rows."""
    data = deepcopy(data)
    years: list[str] = list(data.get("YEARS") or [])
    enrollment = data.setdefault("enrollment", {})
    promo_rates = data.setdefault("promoRates", {})
    dropouts = data.setdefault("dropouts", [])
    lwd = data.setdefault("lwd", {})
    teachers = data.setdefault("teachers", [])
    seats = data.setdefault("seats", [])
    insights = data.setdefault("insightsData", {})

    if not teachers:
        teachers.extend({"s": s} for s in SUBJECTS)
    if not seats:
        seats.extend({"g": g} for g in SEAT_GROUPS)

    for yr in years:
        enrollment.setdefault(yr, {g: {"m": 0, "f": 0} for g in GRADES})
        for g in GRADES:
            enrollment[yr].setdefault(g, {"m": 0, "f": 0})

        promo_rates.setdefault(yr, {})
        for g in GRADES:
            promo_rates[yr].setdefault(g, {"m": 0.0, "f": 0.0})
        promo_rates[yr].setdefault("total", {"m": 0.0, "f": 0.0})

        if not any(d.get("year") == yr for d in dropouts):
            dropouts.append({"year": yr, "male": 0, "female": 0})
        lwd.setdefault(yr, 0)
        insights.setdefault(yr, {"insights": [], "recommendations": []})

        for row in teachers:
            row.setdefault(yr, 0)
        for row in seats:
            row.setdefault(yr, 0)

    data["transitions"] = recompute_transitions(years, enrollment)
    data["YEARS"] = years
    return data


def _builtin_default() -> dict[str, Any]:
    """Minimal data so the app still loads if school_data.json was not pushed."""
    year = "2025-2026"
    return {
        "YEARS": [year],
        "enrollment": {year: {g: {"m": 0, "f": 0} for g in GRADES}},
        "promoRates": {
            year: {
                **{g: {"m": 0.0, "f": 0.0} for g in GRADES},
                "total": {"m": 0.0, "f": 0.0},
            }
        },
        "dropouts": [{"year": year, "male": 0, "female": 0}],
        "lwd": {year: 0},
        "teachers": [{"s": s, year: 0} for s in SUBJECTS],
        "seats": [{"g": g, year: 0} for g in SEAT_GROUPS],
        "insightsData": {year: {"insights": [], "recommendations": []}},
    }


def load_data(*, allow_default: bool = True) -> dict[str, Any]:
    if DATA_FILE.exists():
        with DATA_FILE.open(encoding="utf-8") as f:
            return normalize(json.load(f))
    if allow_default:
        return normalize(_builtin_default())
    raise FileNotFoundError(
        f"Missing {DATA_FILE.as_posix()}. Upload the data/ folder to GitHub."
    )


def save_data(data: dict[str, Any]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = normalize(data)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def add_year(data: dict[str, Any], year: str) -> dict[str, Any]:
    data = deepcopy(data)
    years: list[str] = data.setdefault("YEARS", [])
    if year in years:
        raise ValueError(f"School year {year} already exists.")
    years.append(year)
    bundle = empty_year_bundle(year)
    data["enrollment"][year] = bundle["enrollment"]
    data["promoRates"][year] = bundle["promoRates"]
    data["dropouts"].append({"year": year, **bundle["dropout"]})
    data["lwd"][year] = bundle["lwd"]
    data["insightsData"][year] = {
        "insights": bundle["insights"],
        "recommendations": bundle["recommendations"],
    }
    for row in data.get("teachers", []):
        row[year] = 0
    for row in data.get("seats", []):
        row[year] = 0
    return normalize(data)
