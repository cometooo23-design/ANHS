"""
Arayat National High School — Streamlit dashboard.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from anhs_data import (  # noqa: E402
    GRADES,
    SEAT_GROUPS,
    SUBJECTS,
    add_year,
    load_data,
    normalize,
    save_data,
)

def resolve_dashboard_path() -> Path:
    """Prefer dashboard/index.html (dynamic); fall back to index.html at repo root."""
    candidates = [
        ROOT / "dashboard" / "index.html",
        ROOT / "index.html",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "Dashboard HTML not found. Add dashboard/index.html to your GitHub repo "
        "(the updated file from this project, not the old static-only HTML)."
    )


def inject_data(html: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    script = f"<script>window.__ANHS_DATA__ = {payload};</script>"
    if "<head>" in html:
        return html.replace("<head>", f"<head>{script}", 1)
    return script + html


def render_dashboard(data: dict) -> None:
    path = resolve_dashboard_path()
    html = path.read_text(encoding="utf-8")
    if "window.__ANHS_DATA__" not in html and "function initData" not in html:
        st.warning(
            f"Using `{path.name}` at repo root may be the **old static** file. "
            "Upload `dashboard/index.html` from this project for year filtering and charts."
        )
    components.html(inject_data(html, data), height=1400, scrolling=True)


def render_manage_data(data: dict) -> dict:
    st.subheader("School year")
    years: list[str] = data.get("YEARS", [])
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        year = st.selectbox("Edit year", years, index=len(years) - 1 if years else 0)
    with c2:
        new_year = st.text_input("Add new year (YYYY-YYYY)", placeholder="2026-2027")
    with c3:
        st.write("")
        if st.button("Add year", use_container_width=True):
            if not re.fullmatch(r"\d{4}-\d{4}", new_year.strip()):
                st.error("Use format YYYY-YYYY (e.g. 2026-2027).")
            else:
                try:
                    data = add_year(data, new_year.strip())
                    save_data(data)
                    st.success(f"Added {new_year.strip()}.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

    if not year:
        st.info("Add a school year to begin.")
        return data

    st.divider()
    st.subheader(f"Enrollment — {year}")
    enr_cols = st.columns(len(GRADES))
    enrollment = data["enrollment"].setdefault(year, {})
    for i, g in enumerate(GRADES):
        row = enrollment.setdefault(g, {"m": 0, "f": 0})
        with enr_cols[i]:
            st.markdown(f"**Grade {g[1:]}**")
            row["m"] = int(st.number_input("Male", 0, 9999, int(row.get("m", 0)), key=f"enr_m_{year}_{g}"))
            row["f"] = int(st.number_input("Female", 0, 9999, int(row.get("f", 0)), key=f"enr_f_{year}_{g}"))

    st.divider()
    st.subheader(f"Promotion rates (%) — {year}")
    promo = data["promoRates"].setdefault(year, {})
    promo_cols = st.columns(len(GRADES))
    for i, g in enumerate(GRADES):
        pr = promo.setdefault(g, {"m": 0.0, "f": 0.0})
        with promo_cols[i]:
            st.markdown(f"**Grade {g[1:]}**")
            pr["m"] = float(st.number_input("Male %", 0.0, 100.0, float(pr.get("m", 0)), key=f"pro_m_{year}_{g}"))
            pr["f"] = float(st.number_input("Female %", 0.0, 100.0, float(pr.get("f", 0)), key=f"pro_f_{year}_{g}"))
    total = promo.setdefault("total", {"m": 0.0, "f": 0.0})
    t1, t2 = st.columns(2)
    with t1:
        total["m"] = float(st.number_input("Total male avg %", 0.0, 100.0, float(total.get("m", 0)), key=f"pro_tot_m_{year}"))
    with t2:
        total["f"] = float(st.number_input("Total female avg %", 0.0, 100.0, float(total.get("f", 0)), key=f"pro_tot_f_{year}"))

    st.divider()
    st.subheader("Other indicators")
    drop = next((d for d in data["dropouts"] if d.get("year") == year), None)
    if drop is None:
        drop = {"year": year, "male": 0, "female": 0}
        data["dropouts"].append(drop)
    o1, o2, o3 = st.columns(3)
    with o1:
        drop["male"] = int(st.number_input("Dropouts (male)", 0, 9999, int(drop.get("male", 0)), key=f"drop_m_{year}"))
    with o2:
        drop["female"] = int(st.number_input("Dropouts (female)", 0, 9999, int(drop.get("female", 0)), key=f"drop_f_{year}"))
    with o3:
        data["lwd"][year] = int(st.number_input("PWD count", 0, 9999, int(data["lwd"].get(year, 0)), key=f"pwd_{year}"))

    st.divider()
    st.subheader("Teachers per subject")
    tcols = st.columns(3)
    for i, subj in enumerate(SUBJECTS):
        row = next((r for r in data["teachers"] if r.get("s") == subj), None)
        if row is None:
            row = {"s": subj}
            data["teachers"].append(row)
        with tcols[i % 3]:
            row[year] = int(st.number_input(subj, 0, 99, int(row.get(year, 0)), key=f"tch_{year}_{subj}"))

    st.divider()
    st.subheader("Seat capacity")
    scols = st.columns(len(SEAT_GROUPS))
    for i, grp in enumerate(SEAT_GROUPS):
        row = next((r for r in data["seats"] if r.get("g") == grp), None)
        if row is None:
            row = {"g": grp}
            data["seats"].append(row)
        with scols[i]:
            row[year] = int(st.number_input(grp, 0, 9999, int(row.get(year, 0)), key=f"seat_{year}_{grp}"))

    st.divider()
    ins = data["insightsData"].setdefault(year, {"insights": [], "recommendations": []})
    ins["insights"] = [
        line.strip()
        for line in st.text_area(
            "Insights (one per line)",
            "\n".join(ins.get("insights", [])),
            height=140,
            key=f"ins_{year}",
        ).splitlines()
        if line.strip()
    ]
    ins["recommendations"] = [
        line.strip()
        for line in st.text_area(
            "Recommendations (one per line)",
            "\n".join(ins.get("recommendations", [])),
            height=140,
            key=f"rec_{year}",
        ).splitlines()
        if line.strip()
    ]

    st.divider()
    if st.button("Save all changes", type="primary", use_container_width=True):
        save_data(data)
        st.success("Saved. Open the Dashboard tab and pick a school year to see updated charts.")
        st.rerun()

    with st.expander("Advanced: upload / download JSON"):
        up = st.file_uploader("Replace all data from backup JSON", type=["json"])
        if up is not None:
            try:
                uploaded = normalize(json.loads(up.getvalue().decode("utf-8")))
                save_data(uploaded)
                st.success("Backup imported.")
                st.rerun()
            except json.JSONDecodeError:
                st.error("Invalid JSON file.")
        st.download_button(
            "Download backup JSON",
            data=json.dumps(normalize(deepcopy(data)), indent=2, ensure_ascii=False),
            file_name="ANHS_backup.json",
            mime="application/json",
        )

    return data


def main() -> None:
    st.set_page_config(
        page_title="ANHS Dashboard",
        page_icon="🏫",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    data_file = ROOT / "data" / "school_data.json"
    using_default = not data_file.is_file()
    data = load_data(allow_default=True)

    if using_default:
        st.error(
            "**Missing `data/school_data.json` on GitHub.** "
            "The app is running with empty placeholder data. "
            "Upload the `data` folder from your computer, then reboot the app."
        )
    try:
        resolve_dashboard_path()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    st.title("Arayat National High School")
    st.caption("Enrollment, promotion, teachers, and facilities — filter by school year on the dashboard.")

    tab_dash, tab_data = st.tabs(["Dashboard", "Manage Data"])

    with tab_dash:
        st.markdown(
            "Use the **School Year** control in the header to switch years. "
            "Charts and KPIs update automatically."
        )
        try:
            render_dashboard(data)
        except Exception as exc:
            st.exception(exc)

    with tab_data:
        updated = render_manage_data(deepcopy(data))
        if updated is not None:
            data = updated


main()
