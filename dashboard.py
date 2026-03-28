import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import os
from datetime import datetime, timedelta
import numpy as np

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Fotopia Dashboard", page_icon="\U0001F4CA")

DATA_DIR = os.path.join(os.path.dirname(__file__), "output")

# ---------------------------------------------------------------------------
# Corporate color palette
# ---------------------------------------------------------------------------
CORP_PRIMARY = "#1B2A4A"       # deep navy
CORP_SECONDARY = "#2E86DE"     # bright blue
CORP_ACCENT = "#0ABDE3"        # cyan accent
CORP_SUCCESS = "#10AC84"       # green
CORP_WARNING = "#F39C12"       # amber
CORP_DANGER = "#EE5A24"        # red-orange
CORP_LIGHT_BG = "#F8F9FB"      # near-white background
CORP_BORDER = "#D5DDE5"        # subtle border
CORP_TEXT = "#2C3E50"          # dark text
CORP_MUTED = "#7F8C8D"        # muted text

PRODUCT_COLORS = {
    "FotoCapture": "#2E86DE",
    "Fotognize": "#10AC84",
    "FotoFind": "#F39C12",
    "FotoScan": "#8E44AD",
    "Fototracker": "#EE5A24",
    "DET": "#0ABDE3",
    "FotoVerifAI": "#6D4C41",
    "FotoAnnotate": "#546E7A",
    "Internal/Management": "#95A5A6",
    "Unknown": "#BDC3C7",
}

DONE_STATES = {"Done", "Closed", "Released", "Cancelled", "Removed"}

# ---------------------------------------------------------------------------
# Corporate Plotly template
# ---------------------------------------------------------------------------
_corp_template = pio.templates["plotly_white"]
_corp_template.layout.font = dict(family="Inter, Segoe UI, Helvetica, Arial, sans-serif", size=13, color=CORP_TEXT)
_corp_template.layout.paper_bgcolor = "white"
_corp_template.layout.plot_bgcolor = "#FAFBFC"
_corp_template.layout.colorway = [CORP_SECONDARY, CORP_SUCCESS, CORP_WARNING, CORP_DANGER, "#8E44AD", CORP_ACCENT, "#6D4C41", "#546E7A", "#95A5A6"]
_corp_template.layout.xaxis = dict(gridcolor="#ECF0F1", linecolor=CORP_BORDER, zerolinecolor="#ECF0F1")
_corp_template.layout.yaxis = dict(gridcolor="#ECF0F1", linecolor=CORP_BORDER, zerolinecolor="#ECF0F1")
pio.templates["fotopia_corp"] = _corp_template

PLOTLY_TEMPLATE = "fotopia_corp"
COMPACT_MARGIN = dict(l=20, r=20, t=40, b=20)

# ---------------------------------------------------------------------------
# CSS styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* --- Global --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* --- Hide streamlit default metric styling, replace with corp boxes --- */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid """ + CORP_BORDER + """;
    border-left: 4px solid """ + CORP_SECONDARY + """;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    color: """ + CORP_MUTED + """ !important;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] div {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: unset !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: """ + CORP_PRIMARY + """ !important;
}
[data-testid="stMetricValue"] p,
[data-testid="stMetricValue"] div {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: unset !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* --- Tabs --- */
[data-testid="stTabs"] button {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: """ + CORP_MUTED + """ !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 16px !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: """ + CORP_SECONDARY + """ !important;
    border-bottom: 3px solid """ + CORP_SECONDARY + """ !important;
}

/* --- Headers --- */
h1, h2, h3, .stHeader {
    color: """ + CORP_PRIMARY + """ !important;
}

h1 { font-weight: 700 !important; }
h2 { font-weight: 600 !important; font-size: 1.5rem !important; }
h3 { font-weight: 600 !important; font-size: 1.15rem !important; }

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background: """ + CORP_PRIMARY + """ !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] [data-testid="stMultiSelect"],
[data-testid="stSidebar"] [data-testid="stDateInput"] {
    background: rgba(255,255,255,0.08);
    border-radius: 6px;
}

[data-testid="stSidebar"] label {
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

/* --- DataFrames / Tables --- */
[data-testid="stDataFrame"] {
    border: 1px solid """ + CORP_BORDER + """;
    border-radius: 8px;
    overflow: hidden;
}

/* --- Alert boxes --- */
[data-testid="stAlert"] {
    border-radius: 8px;
    border-left-width: 4px !important;
}

/* --- Expanders --- */
[data-testid="stExpander"] {
    border: 1px solid """ + CORP_BORDER + """;
    border-radius: 8px;
    background: white;
}

/* --- Plotly charts container --- */
[data-testid="stPlotlyChart"] {
    background: white;
    border: 1px solid """ + CORP_BORDER + """;
    border-radius: 8px;
    padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* --- Dividers --- */
hr {
    border-color: """ + CORP_BORDER + """ !important;
}

/* --- Caption / Footer --- */
[data-testid="stCaptionContainer"] {
    color: """ + CORP_MUTED + """ !important;
}

/* --- Main area background --- */
[data-testid="stMain"] {
    background: """ + CORP_LIGHT_BG + """;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_clockify():
    df = pd.read_csv(os.path.join(DATA_DIR, "clockify_normalized.csv"))
    df["Start Date"] = pd.to_datetime(df["Start Date"], format="%d/%m/%Y", errors="coerce")
    df["End Date"] = pd.to_datetime(df["End Date"], format="%d/%m/%Y", errors="coerce")
    df["Duration (decimal)"] = pd.to_numeric(df["Duration (decimal)"], errors="coerce").fillna(0)
    df["Mapping_Confidence"] = pd.to_numeric(df["Mapping_Confidence"], errors="coerce")
    df["Normalized_Product"] = df["Normalized_Product"].fillna("").astype(str).str.strip()
    df["Normalized_Client"] = df["Normalized_Client"].fillna("").astype(str).str.strip()
    df["Normalized_Version"] = df["Normalized_Version"].fillna("").astype(str).str.strip()
    df["Work_Category"] = df["Work_Category"].fillna("").astype(str).str.strip()
    df["Project_Type"] = df["Project_Type"].fillna("").astype(str).str.strip()
    df["Team_Domain"] = df["Team_Domain"].fillna("").astype(str).str.strip()
    df["DevOps_Work_Item_ID"] = df["DevOps_Work_Item_ID"].fillna("").astype(str).str.strip()
    df["Is_Suspicious"] = df["Is_Suspicious"].fillna("").astype(str).str.strip()
    df["Suspicious_Reason"] = df["Suspicious_Reason"].fillna("").astype(str).str.strip()
    df["Description"] = df["Description"].fillna("").astype(str).str.strip()
    df["User"] = df["User"].fillna("").astype(str).str.strip()
    df["Email"] = df["Email"].fillna("").astype(str).str.strip()
    df["Project"] = df["Project"].fillna("").astype(str).str.strip()
    df["Tags"] = df["Tags"].fillna("").astype(str).str.strip()
    df["week"] = df["Start Date"].dt.isocalendar().week.astype(int, errors="ignore")
    df["year_week"] = df["Start Date"].dt.strftime("%Y-W%U")
    return df


@st.cache_data
def load_devops():
    df = pd.read_csv(os.path.join(DATA_DIR, "devops_normalized.csv"))
    df["Normalized_Product"] = df["Normalized_Product"].fillna("").astype(str).str.strip()
    df["Normalized_Version"] = df["Normalized_Version"].fillna("").astype(str).str.strip()
    df["Normalized_Client"] = df["Normalized_Client"].fillna("").astype(str).str.strip()
    df["Normalized_State"] = df["Normalized_State"].fillna("").astype(str).str.strip()
    df["Work Item Type"] = df["Work Item Type"].fillna("").astype(str).str.strip()
    df["Tags"] = df["Tags"].fillna("").astype(str).str.strip()
    df["Team_Domain"] = df["Team_Domain"].fillna("").astype(str).str.strip()
    df["Assigned To"] = df["Assigned To"].fillna("").astype(str).str.strip()
    df["Assigned_Email"] = df["Assigned_Email"].fillna("").astype(str).str.strip()
    # Parse display name from "Name <email>"
    df["Assigned_Display"] = df["Assigned To"].str.replace(r"\s*<.*>", "", regex=True)
    return df


@st.cache_data
def load_cross_links():
    df = pd.read_csv(os.path.join(DATA_DIR, "cross_system_links.csv"))
    df["Duration (decimal)"] = pd.to_numeric(df["Duration (decimal)"], errors="coerce").fillna(0)
    df["Start Date"] = pd.to_datetime(df["Start Date"], format="%d/%m/%Y", errors="coerce")
    return df


@st.cache_data
def load_person_master():
    return pd.read_csv(os.path.join(DATA_DIR, "person_master.csv"))


@st.cache_data
def load_product_summary():
    return pd.read_csv(os.path.join(DATA_DIR, "product_summary.csv"))


@st.cache_data
def load_client_summary():
    return pd.read_csv(os.path.join(DATA_DIR, "client_summary.csv"))


@st.cache_data
def load_quality_report():
    return pd.read_csv(os.path.join(DATA_DIR, "data_quality_report.csv"))


@st.cache_data
def load_mapping_audit():
    return pd.read_csv(os.path.join(DATA_DIR, "mapping_audit.csv"))


# ---------------------------------------------------------------------------
# Load all data
# ---------------------------------------------------------------------------
clockify = load_clockify()
devops = load_devops()
cross_links = load_cross_links()
person_master = load_person_master()
product_summary = load_product_summary()
client_summary = load_client_summary()
quality_report = load_quality_report()
mapping_audit = load_mapping_audit()

# ---------------------------------------------------------------------------
# Last refreshed + Corporate header
# ---------------------------------------------------------------------------
clockify_path = os.path.join(DATA_DIR, "clockify_normalized.csv")
last_mod = datetime.fromtimestamp(os.path.getmtime(clockify_path))

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; padding:4px 0 12px 0; border-bottom:2px solid {CORP_SECONDARY}; margin-bottom:16px;">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="background:{CORP_PRIMARY}; color:white; font-weight:700; font-size:1.1rem; padding:8px 16px; border-radius:6px; letter-spacing:1px;">FOTOPIA</div>
        <div style="color:{CORP_MUTED}; font-size:0.85rem;">Project Management Dashboard</div>
    </div>
    <div style="color:{CORP_MUTED}; font-size:0.78rem; text-align:right;">
        Last refreshed: <strong>{last_mod.strftime('%Y-%m-%d %H:%M')}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown(f"""
<div style="text-align:center; padding:8px 0 16px 0; border-bottom:1px solid rgba(255,255,255,0.15); margin-bottom:16px;">
    <div style="font-size:1.3rem; font-weight:700; letter-spacing:2px;">FOTOPIA</div>
    <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px; opacity:0.7; margin-top:2px;">Dashboard Filters</div>
</div>
""", unsafe_allow_html=True)

# Date range
min_date = clockify["Start Date"].dropna().min().date() if not clockify["Start Date"].dropna().empty else datetime(2025, 1, 1).date()
max_date = clockify["Start Date"].dropna().max().date() if not clockify["Start Date"].dropna().empty else datetime.today().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Product
all_products = sorted([p for p in clockify["Normalized_Product"].unique() if p])
sel_products = st.sidebar.multiselect("Product", all_products, default=[])

# Client
all_clients = sorted([c for c in clockify["Normalized_Client"].unique() if c])
sel_clients = st.sidebar.multiselect("Client", all_clients, default=[])

# Person
all_persons = sorted([u for u in clockify["User"].unique() if u])
sel_persons = st.sidebar.multiselect("Person", all_persons, default=[])

# Team domain
team_domain_opt = st.sidebar.radio("Team Domain", ["All", "Fotopia (Internal)", "InfaSME (Partner)"])

# Project type
all_proj_types = sorted([p for p in clockify["Project_Type"].unique() if p])
sel_proj_types = st.sidebar.multiselect("Project Type", all_proj_types, default=[])

# Work category
all_work_cats = sorted([w for w in clockify["Work_Category"].unique() if w])
sel_work_cats = st.sidebar.multiselect("Work Category", all_work_cats, default=[])

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------

def apply_clockify_filters(df):
    filtered = df.copy()
    if len(date_range) == 2:
        start_d, end_d = date_range
        filtered = filtered[
            (filtered["Start Date"].dt.date >= start_d) & (filtered["Start Date"].dt.date <= end_d)
        ]
    if sel_products:
        filtered = filtered[filtered["Normalized_Product"].isin(sel_products)]
    if sel_clients:
        filtered = filtered[filtered["Normalized_Client"].isin(sel_clients)]
    if sel_persons:
        filtered = filtered[filtered["User"].isin(sel_persons)]
    if team_domain_opt != "All":
        filtered = filtered[filtered["Team_Domain"] == team_domain_opt]
    if sel_proj_types:
        filtered = filtered[filtered["Project_Type"].isin(sel_proj_types)]
    if sel_work_cats:
        filtered = filtered[filtered["Work_Category"].isin(sel_work_cats)]
    return filtered


def apply_devops_filters(df):
    filtered = df.copy()
    if sel_products:
        filtered = filtered[filtered["Normalized_Product"].isin(sel_products)]
    if sel_clients:
        filtered = filtered[filtered["Normalized_Client"].isin(sel_clients)]
    if team_domain_opt != "All":
        filtered = filtered[filtered["Team_Domain"] == team_domain_opt]
    return filtered


cf = apply_clockify_filters(clockify)
dv = apply_devops_filters(devops)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "Executive Summary",
    "Portfolio Overview",
    "Project Health",
    "Resource & Team",
    "DevOps Delivery",
    "Time Tracking Intelligence",
    "Cross-System Reconciliation",
    "Data Quality & Governance",
    "Person-Product Matrix",
    "Weekly Digest & Alerts",
    "Bug Aging",
    "Knowledge Transfer Risk",
    "Clockify Hygiene",
])

# ===== TAB 1: Executive Summary =====
with tabs[0]:
    st.header("Executive Summary")

    total_hours = cf["Duration (decimal)"].sum()
    active_products = cf[cf["Normalized_Product"] != ""]["Normalized_Product"].nunique()
    active_clients = cf[cf["Normalized_Client"] != ""]["Normalized_Client"].nunique()
    num_people = cf[cf["User"] != ""]["User"].nunique()
    open_bugs = len(dv[(dv["Work Item Type"] == "Bug") & (~dv["Normalized_State"].isin(DONE_STATES))])
    completed_items = len(dv[dv["Normalized_State"].isin(DONE_STATES)])

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Hours", f"{total_hours:,.1f}")
    c2.metric("Active Products", active_products)
    c3.metric("Active Clients", active_clients)
    c4, c5, c6 = st.columns(3)
    c4.metric("People", num_people)
    c5.metric("Open Bugs", open_bugs)
    c6.metric("Completed Items", completed_items)

    st.subheader("Hours Trend (Weekly)")
    if not cf.empty and cf["Start Date"].notna().any():
        weekly = cf.copy()
        weekly["week_start"] = weekly["Start Date"] - pd.to_timedelta(weekly["Start Date"].dt.dayofweek, unit="D")
        weekly_agg = (
            weekly.groupby(["week_start", "Normalized_Product"])["Duration (decimal)"]
            .sum()
            .reset_index()
        )
        weekly_agg = weekly_agg[weekly_agg["Normalized_Product"] != ""]
        fig = px.area(
            weekly_agg, x="week_start", y="Duration (decimal)",
            color="Normalized_Product",
            color_discrete_map=PRODUCT_COLORS,
            template=PLOTLY_TEMPLATE,
            labels={"Duration (decimal)": "Hours", "week_start": "Week"},
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No data for the selected filters.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Work Distribution")
        wc = cf[cf["Work_Category"] != ""].groupby("Work_Category")["Duration (decimal)"].sum().reset_index()
        if not wc.empty:
            fig = px.pie(
                wc, names="Work_Category", values="Duration (decimal)", hole=0.45,
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(margin=COMPACT_MARGIN)
            st.plotly_chart(fig, width="stretch")

    with col_b:
        st.subheader("Top 5 People by Hours")
        top5 = cf.groupby("User")["Duration (decimal)"].sum().nlargest(5).reset_index()
        if not top5.empty:
            fig = px.bar(
                top5, x="Duration (decimal)", y="User", orientation="h",
                template=PLOTLY_TEMPLATE,
                labels={"Duration (decimal)": "Hours"},
            )
            fig.update_layout(margin=COMPACT_MARGIN, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, width="stretch")

    st.subheader("Project Status")
    proj_hours = cf[cf["Normalized_Product"] != ""].groupby(["Normalized_Product", "Normalized_Version"]).agg(
        Total_Hours=("Duration (decimal)", "sum")
    ).reset_index()
    devops_counts = dv.groupby(["Normalized_Product", "Normalized_Version"]).agg(
        DevOps_Items=("ID", "count"),
        Open_Bugs=("ID", lambda x: ((dv.loc[x.index, "Work Item Type"] == "Bug") & (~dv.loc[x.index, "Normalized_State"].isin(DONE_STATES))).sum()),
        Completed=("ID", lambda x: (dv.loc[x.index, "Normalized_State"].isin(DONE_STATES)).sum()),
        Total=("ID", "count"),
    ).reset_index()
    devops_counts["Completion %"] = (devops_counts["Completed"] / devops_counts["Total"].replace(0, 1) * 100).round(1)
    proj_status = proj_hours.merge(devops_counts, on=["Normalized_Product", "Normalized_Version"], how="left").fillna(0)
    st.dataframe(proj_status, width="stretch", hide_index=True)

# ===== TAB 2: Portfolio Overview =====
with tabs[1]:
    st.header("Portfolio Overview")

    st.subheader("Hours by Product")
    prod_cat = cf[cf["Normalized_Product"] != ""].groupby(["Normalized_Product", "Work_Category"])["Duration (decimal)"].sum().reset_index()
    if not prod_cat.empty:
        fig = px.bar(
            prod_cat, x="Duration (decimal)", y="Normalized_Product", color="Work_Category",
            orientation="h", template=PLOTLY_TEMPLATE,
            labels={"Duration (decimal)": "Hours", "Normalized_Product": "Product"},
        )
        fig.update_layout(margin=COMPACT_MARGIN, barmode="stack")
        st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hours by Client")
        client_hrs = cf[cf["Normalized_Client"] != ""].groupby("Normalized_Client")["Duration (decimal)"].sum().reset_index()
        if not client_hrs.empty:
            fig = px.bar(
                client_hrs, x="Duration (decimal)", y="Normalized_Client", orientation="h",
                template=PLOTLY_TEMPLATE, labels={"Duration (decimal)": "Hours", "Normalized_Client": "Client"},
            )
            fig.update_layout(margin=COMPACT_MARGIN)
            st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Internal vs External")
        domain_hrs = cf[cf["Team_Domain"] != ""].groupby("Team_Domain")["Duration (decimal)"].sum().reset_index()
        if not domain_hrs.empty:
            fig = px.pie(
                domain_hrs, names="Team_Domain", values="Duration (decimal)", hole=0.0,
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(margin=COMPACT_MARGIN)
            st.plotly_chart(fig, width="stretch")

    st.subheader("Hours by Version")
    ver_data = cf[(cf["Normalized_Product"] != "") & (cf["Normalized_Version"] != "")].groupby(
        ["Normalized_Product", "Normalized_Version"]
    )["Duration (decimal)"].sum().reset_index()
    if not ver_data.empty:
        fig = px.bar(
            ver_data, x="Normalized_Version", y="Duration (decimal)", color="Normalized_Product",
            barmode="group", template=PLOTLY_TEMPLATE,
            color_discrete_map=PRODUCT_COLORS,
            labels={"Duration (decimal)": "Hours", "Normalized_Version": "Version"},
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Investment Treemap")
    tree_data = cf[cf["Normalized_Product"] != ""].groupby(["Normalized_Product", "Normalized_Version"])["Duration (decimal)"].sum().reset_index()
    tree_data["Normalized_Version"] = tree_data["Normalized_Version"].replace("", "No Version")
    if not tree_data.empty:
        fig = px.treemap(
            tree_data, path=["Normalized_Product", "Normalized_Version"],
            values="Duration (decimal)", color="Duration (decimal)",
            color_continuous_scale="Blues", template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

# ===== TAB 3: Project Health =====
with tabs[2]:
    st.header("Project Health")
    products_list = sorted([p for p in cf["Normalized_Product"].unique() if p])
    for prod in products_list:
        with st.expander(prod, expanded=False):
            p_cf = cf[cf["Normalized_Product"] == prod]
            p_dv = dv[dv["Normalized_Product"] == prod]
            p_hours = p_cf["Duration (decimal)"].sum()
            p_devops = len(p_dv)
            p_bugs = len(p_dv[p_dv["Work Item Type"] == "Bug"])
            p_features = len(p_dv[p_dv["Work Item Type"] == "Feature"])
            p_done = len(p_dv[p_dv["Normalized_State"].isin(DONE_STATES)])
            p_completion = (p_done / p_devops * 100) if p_devops > 0 else 0

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Hours", f"{p_hours:,.1f}")
            m2.metric("DevOps Items", p_devops)
            m3.metric("Bugs", p_bugs)
            m4.metric("Features", p_features)
            m5.metric("Completion %", f"{p_completion:.1f}%")

            left, right = st.columns(2)
            with left:
                cat_data = p_cf[p_cf["Work_Category"] != ""].groupby("Work_Category")["Duration (decimal)"].sum().reset_index()
                if not cat_data.empty:
                    fig = px.pie(
                        cat_data, names="Work_Category", values="Duration (decimal)", hole=0.45,
                        template=PLOTLY_TEMPLATE, title="Effort by Category",
                    )
                    fig.update_layout(margin=COMPACT_MARGIN)
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.info("No category data.")

            with right:
                state_data = p_dv[p_dv["Normalized_State"] != ""].groupby("Normalized_State")["ID"].count().reset_index()
                state_data.columns = ["Normalized_State", "Count"]
                if not state_data.empty:
                    fig = px.bar(
                        state_data, x="Count", y="Normalized_State", orientation="h",
                        template=PLOTLY_TEMPLATE, title="DevOps State Distribution",
                    )
                    fig.update_layout(margin=COMPACT_MARGIN)
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.info("No DevOps items.")

            if not p_dv.empty:
                st.dataframe(
                    p_dv[["ID", "Work Item Type", "Title", "State", "Normalized_State", "Assigned To", "Tags"]],
                    width="stretch", hide_index=True,
                )

# ===== TAB 4: Resource & Team =====
with tabs[3]:
    st.header("Resource & Team")

    # Build person lookup from person_master
    person_lookup = dict(zip(person_master["Email"].str.lower(), person_master["Display_Name"]))

    def get_display_name(row):
        email = row["Email"].lower() if row["Email"] else ""
        return person_lookup.get(email, row["User"])

    cf_res = cf.copy()
    cf_res["Display_Name"] = cf_res.apply(get_display_name, axis=1)

    st.subheader("Utilization Heatmap")
    if cf_res["Start Date"].notna().any():
        cf_res["iso_week"] = cf_res["Start Date"].dt.strftime("%Y-W%U")
        heat_data = cf_res.groupby(["Display_Name", "iso_week"])["Duration (decimal)"].sum().reset_index()
        heat_pivot = heat_data.pivot(index="Display_Name", columns="iso_week", values="Duration (decimal)").fillna(0)
        heat_pivot = heat_pivot[sorted(heat_pivot.columns)]

        # Custom color scale: red <20, yellow 20-30, green 30-40, yellow 40-50, red >50
        colorscale = [
            [0.0, "#F44336"],    # red (0h)
            [0.25, "#FFEB3B"],   # yellow (~20h)
            [0.5, "#4CAF50"],    # green (~35h)
            [0.75, "#FFEB3B"],   # yellow (~50h)
            [1.0, "#F44336"],    # red (>60h)
        ]
        fig = go.Figure(data=go.Heatmap(
            z=heat_pivot.values,
            x=heat_pivot.columns.tolist(),
            y=heat_pivot.index.tolist(),
            colorscale=colorscale,
            zmin=0, zmax=60,
            hovertemplate="Person: %{y}<br>Week: %{x}<br>Hours: %{z:.1f}<extra></extra>",
        ))
        fig.update_layout(template=PLOTLY_TEMPLATE, margin=COMPACT_MARGIN, height=max(400, len(heat_pivot) * 25))
        st.plotly_chart(fig, width="stretch")

    st.subheader("Context Switching (Avg Distinct Projects/Day)")
    if cf_res["Start Date"].notna().any():
        ctx = cf_res.groupby(["Display_Name", cf_res["Start Date"].dt.date])["Normalized_Product"].nunique().reset_index()
        ctx.columns = ["Display_Name", "Date", "Project_Count"]
        ctx_avg = ctx.groupby("Display_Name")["Project_Count"].mean().reset_index().sort_values("Project_Count", ascending=True)
        ctx_avg.columns = ["Display_Name", "Avg_Projects_Per_Day"]
        fig = px.bar(
            ctx_avg, x="Avg_Projects_Per_Day", y="Display_Name", orientation="h",
            template=PLOTLY_TEMPLATE, labels={"Avg_Projects_Per_Day": "Avg Projects/Day"},
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("Hours by Person (by Product)")
        person_prod = cf_res[cf_res["Normalized_Product"] != ""].groupby(
            ["Display_Name", "Normalized_Product"]
        )["Duration (decimal)"].sum().reset_index()
        if not person_prod.empty:
            fig = px.bar(
                person_prod, x="Duration (decimal)", y="Display_Name", color="Normalized_Product",
                orientation="h", template=PLOTLY_TEMPLATE,
                color_discrete_map=PRODUCT_COLORS,
                labels={"Duration (decimal)": "Hours"},
            )
            fig.update_layout(margin=COMPACT_MARGIN, barmode="stack")
            st.plotly_chart(fig, width="stretch")

    with col_r2:
        st.subheader("Meeting Overhead")
        total_per_person = cf_res.groupby("Display_Name")["Duration (decimal)"].sum()
        meeting_per_person = cf_res[cf_res["Tags"].str.contains("Meeting", case=False, na=False)].groupby("Display_Name")["Duration (decimal)"].sum()
        meeting_pct = (meeting_per_person / total_per_person * 100).fillna(0).reset_index()
        meeting_pct.columns = ["Display_Name", "Meeting_%"]
        meeting_pct = meeting_pct.sort_values("Meeting_%", ascending=True)
        if not meeting_pct.empty:
            fig = px.bar(
                meeting_pct, x="Meeting_%", y="Display_Name", orientation="h",
                template=PLOTLY_TEMPLATE, labels={"Meeting_%": "Meeting %"},
            )
            fig.update_layout(margin=COMPACT_MARGIN)
            st.plotly_chart(fig, width="stretch")

    st.subheader("Team Domain Split")
    domain_split = cf_res[cf_res["Team_Domain"] != ""].groupby("Team_Domain")["Duration (decimal)"].sum().reset_index()
    if not domain_split.empty:
        fig = px.bar(
            domain_split, x="Team_Domain", y="Duration (decimal)",
            template=PLOTLY_TEMPLATE, labels={"Duration (decimal)": "Hours"},
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

# ===== TAB 5: DevOps Delivery =====
with tabs[4]:
    st.header("DevOps Delivery")

    st.subheader("Backlog by Product")
    backlog = dv[dv["Normalized_Product"] != ""].groupby(["Normalized_Product", "Normalized_State"])["ID"].count().reset_index()
    backlog.columns = ["Normalized_Product", "Normalized_State", "Count"]
    if not backlog.empty:
        fig = px.bar(
            backlog, x="Count", y="Normalized_Product", color="Normalized_State",
            orientation="h", template=PLOTLY_TEMPLATE, barmode="stack",
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.subheader("Bug Severity by Product")
        bug_df = dv[dv["Work Item Type"] == "Bug"].copy()
        def parse_severity(tags):
            tags_lower = tags.lower()
            if "critical" in tags_lower:
                return "Critical"
            elif "high priority" in tags_lower:
                return "High"
            elif "medium priority" in tags_lower:
                return "Medium"
            elif "low priority" in tags_lower:
                return "Low"
            return "Unspecified"
        bug_df["Severity"] = bug_df["Tags"].apply(parse_severity)
        sev_data = bug_df.groupby(["Normalized_Product", "Severity"])["ID"].count().reset_index()
        sev_data.columns = ["Product", "Severity", "Count"]
        if not sev_data.empty:
            fig = px.bar(
                sev_data, x="Count", y="Product", color="Severity",
                orientation="h", template=PLOTLY_TEMPLATE, barmode="stack",
                color_discrete_map={"Critical": "#D32F2F", "High": "#F44336", "Medium": "#FF9800", "Low": "#FFEB3B", "Unspecified": "#9E9E9E"},
            )
            fig.update_layout(margin=COMPACT_MARGIN)
            st.plotly_chart(fig, width="stretch")

    with col_d2:
        st.subheader("Work Item Type Distribution")
        type_dist = dv.groupby("Work Item Type")["ID"].count().reset_index()
        type_dist.columns = ["Type", "Count"]
        if not type_dist.empty:
            fig = px.bar(
                type_dist, x="Count", y="Type", orientation="h",
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(margin=COMPACT_MARGIN)
            st.plotly_chart(fig, width="stretch")

    st.subheader("Open Items by State Distribution")
    open_items = dv[~dv["Normalized_State"].isin(DONE_STATES)]
    state_dist = open_items.groupby("Normalized_State")["ID"].count().reset_index()
    state_dist.columns = ["State", "Count"]
    if not state_dist.empty:
        fig = px.bar(
            state_dist, x="Count", y="State", orientation="h",
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Blocked / On-Hold Items")
    blocked = dv[
        dv["State"].str.contains("hold|ice|Hold|Ice|On Hold|On Ice", case=False, na=False) |
        dv["Tags"].str.contains("blocked|on hold|on ice", case=False, na=False)
    ]
    if not blocked.empty:
        st.dataframe(
            blocked[["ID", "Work Item Type", "Title", "State", "Normalized_State", "Assigned To", "Normalized_Product", "Tags"]],
            width="stretch", hide_index=True,
        )
    else:
        st.info("No blocked or on-hold items found.")

# ===== TAB 6: Time Tracking Intelligence =====
with tabs[5]:
    st.header("Time Tracking Intelligence")

    total_hrs = cf["Duration (decimal)"].sum()
    unclassified = cf[cf["Normalized_Product"] == ""]["Duration (decimal)"].sum()
    suspicious_count = len(cf[cf["Is_Suspicious"].str.lower() == "true"])
    empty_desc_count = len(cf[cf["Description"] == ""])
    with_devops = len(cf[cf["DevOps_Work_Item_ID"] != ""])

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Hours", f"{total_hrs:,.1f}")
    k2.metric("Unclassified", f"{unclassified:,.1f}")
    k3.metric("Suspicious", suspicious_count)
    k4, k5, _ = st.columns(3)
    k4.metric("Empty Desc.", empty_desc_count)
    k5.metric("DevOps Linked", with_devops)

    st.subheader("Suspicious Entries")
    sus = cf[cf["Is_Suspicious"].str.lower() == "true"]
    if not sus.empty:
        st.dataframe(
            sus[["User", "Project", "Description", "Duration (decimal)", "Start Date", "Suspicious_Reason"]],
            width="stretch", hide_index=True,
        )
    else:
        st.info("No suspicious entries.")

    st.subheader("Empty Descriptions by User")
    empty_d = cf[cf["Description"] == ""].groupby("User").size().reset_index(name="Count").sort_values("Count", ascending=False)
    if not empty_d.empty:
        st.dataframe(empty_d, width="stretch", hide_index=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("DevOps Link Coverage")
        link_data = pd.DataFrame({
            "Category": ["With DevOps Link", "Without DevOps Link"],
            "Count": [with_devops, len(cf) - with_devops],
        })
        fig = px.pie(
            link_data, names="Category", values="Count", hole=0.0,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=COMPACT_MARGIN)
        st.plotly_chart(fig, width="stretch")

    with col_t2:
        st.subheader("'Fotopia' Bucket Analysis")
        fotopia_bucket = cf[cf["Project"] == "Fotopia"]
        if not fotopia_bucket.empty:
            fb_grouped = fotopia_bucket.groupby("Normalized_Product")["Duration (decimal)"].sum().reset_index()
            fb_grouped["Normalized_Product"] = fb_grouped["Normalized_Product"].replace("", "Unmapped")
            fig = px.bar(
                fb_grouped, x="Duration (decimal)", y="Normalized_Product", orientation="h",
                template=PLOTLY_TEMPLATE,
                color="Normalized_Product", color_discrete_map=PRODUCT_COLORS,
                labels={"Duration (decimal)": "Hours"},
            )
            fig.update_layout(margin=COMPACT_MARGIN, showlegend=False)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No entries in the 'Fotopia' bucket.")

# ===== TAB 7: Cross-System Reconciliation =====
with tabs[6]:
    st.header("Cross-System Reconciliation")

    matched_pairs = len(cross_links)
    total_clockify = len(cf)
    total_devops = len(dv)
    match_rate = (matched_pairs / total_clockify * 100) if total_clockify > 0 else 0

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Matched", matched_pairs)
    r2.metric("Clockify Entries", total_clockify)
    r3.metric("DevOps Items", total_devops)
    r4.metric("Match Rate", f"{match_rate:.1f}%")

    st.subheader("Matched Pairs")
    st.dataframe(cross_links, width="stretch", hide_index=True)

    st.subheader("Clockify Entries with DevOps References")
    cf_with_devops = cf[cf["DevOps_Work_Item_ID"] != ""]
    st.dataframe(
        cf_with_devops[["User", "Project", "Description", "Duration (decimal)", "Start Date", "DevOps_Work_Item_ID", "Normalized_Product"]],
        width="stretch", hide_index=True,
    )

    st.subheader("Completed DevOps Items Without Time Logged")
    linked_ids = set(cross_links["DevOps_Work_Item_ID"].astype(str).unique())
    done_devops = dv[dv["Normalized_State"].isin({"Done", "Closed", "Released"})]
    unlinked = done_devops[~done_devops["ID"].astype(str).isin(linked_ids)]
    if not unlinked.empty:
        st.dataframe(
            unlinked[["ID", "Work Item Type", "Title", "State", "Normalized_State", "Assigned To", "Normalized_Product"]],
            width="stretch", hide_index=True,
        )
    else:
        st.info("All completed items have time logged.")

# ===== TAB 8: Data Quality & Governance =====
with tabs[7]:
    st.header("Data Quality & Governance")

    total_entries = len(clockify)
    mapped_entries = len(clockify[clockify["Normalized_Product"] != ""])
    mapping_coverage = (mapped_entries / total_entries * 100) if total_entries > 0 else 0
    high_conf = len(clockify[(clockify["Normalized_Product"] != "") & (clockify["Mapping_Confidence"] >= 0.8)])
    high_conf_rate = (high_conf / mapped_entries * 100) if mapped_entries > 0 else 0
    pending_review = len(clockify[(clockify["Normalized_Product"] != "") & (clockify["Mapping_Confidence"] < 0.8)])
    unmapped_count = total_entries - mapped_entries

    q1, q2, q3, q4 = st.columns(4)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Coverage", f"{mapping_coverage:.1f}%")
    q2.metric("High Confidence", f"{high_conf_rate:.1f}%")
    q3.metric("Pending Review", pending_review)
    q4.metric("Unmapped", unmapped_count)

    st.subheader("Mapping Confidence Distribution")
    conf_vals = clockify[clockify["Mapping_Confidence"].notna()]["Mapping_Confidence"]
    if not conf_vals.empty:
        fig = px.histogram(
            conf_vals, nbins=20, template=PLOTLY_TEMPLATE,
            labels={"value": "Confidence", "count": "Entries"},
        )
        fig.update_layout(margin=COMPACT_MARGIN, xaxis_title="Confidence", yaxis_title="Count")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Quality Issues")
    st.dataframe(quality_report, width="stretch", hide_index=True)

    st.subheader("Unmapped Entries")
    unmapped = clockify[clockify["Normalized_Product"] == ""]
    if not unmapped.empty:
        st.dataframe(
            unmapped[["Project", "User", "Description", "Duration (decimal)"]],
            width="stretch", hide_index=True,
        )
    else:
        st.info("All entries are mapped.")

    with st.expander("Mapping Audit Sample (first 50 rows)"):
        st.dataframe(mapping_audit.head(50), width="stretch", hide_index=True)

    st.subheader("Data Quality Recommendations")
    st.info("**Rename 'Fotopia' project:** The generic 'Fotopia' project name forces auto-classification. Rename it to the specific product (e.g., Fotognize, FotoCapture) for accurate tracking.")
    st.info("**Add time entry descriptions:** 263 entries have empty descriptions, making it impossible to verify work content or link to DevOps items.")
    st.info("**Use tags consistently:** Add Work Category tags (Development, Testing, Meeting, etc.) to all time entries for better effort classification.")
    st.info("**Reference DevOps IDs:** Include #WorkItemID in descriptions to enable automatic cross-system linking and traceability.")
    st.info("**Review low-confidence mappings:** 248 entries have mapping confidence below 0.8 and should be manually verified.")

# ===== TAB 9: Person-Product Matrix =====
with tabs[8]:
    st.header("Person-Product Matrix")
    st.markdown("Who works on what — and how spread thin are they?")

    # Build person x product hours matrix
    pp = clockify[clockify["Normalized_Product"] != ""].groupby(
        ["User", "Normalized_Product"]
    )["Duration (decimal)"].sum().reset_index()
    if not pp.empty:
        pp_pivot = pp.pivot_table(
            index="User", columns="Normalized_Product",
            values="Duration (decimal)", aggfunc="sum", fill_value=0,
        )
        # Sort by total hours descending
        pp_pivot["_total"] = pp_pivot.sum(axis=1)
        pp_pivot = pp_pivot.sort_values("_total", ascending=False)
        pp_pivot = pp_pivot.drop(columns=["_total"])

        fig = px.imshow(
            pp_pivot.values,
            x=pp_pivot.columns.tolist(),
            y=pp_pivot.index.tolist(),
            color_continuous_scale=[[0, "#EBF5FB"], [0.3, "#85C1E9"], [0.6, "#2E86DE"], [1.0, "#1B2A4A"]],
            aspect="auto",
            labels=dict(x="Product", y="Person", color="Hours"),
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20), height=max(400, len(pp_pivot) * 28),
        )
        # Add text annotations
        for i, row_name in enumerate(pp_pivot.index):
            for j, col_name in enumerate(pp_pivot.columns):
                val = pp_pivot.iloc[i, j]
                if val > 0:
                    fig.add_annotation(
                        x=j, y=i, text=f"{val:.0f}",
                        showarrow=False, font=dict(size=10, color="white" if val > pp_pivot.values.max() * 0.5 else "black"),
                    )
        st.plotly_chart(fig, width="stretch")

        # Context switching summary
        st.subheader("Multi-Product Contributors")
        st.markdown("People working across 3+ products are at higher risk of context-switching overhead.")
        product_counts = clockify[clockify["Normalized_Product"] != ""].groupby("User")["Normalized_Product"].nunique().reset_index()
        product_counts.columns = ["Person", "Products Worked On"]
        product_counts = product_counts.sort_values("Products Worked On", ascending=False)

        # Add total hours
        total_hrs_per_person = clockify.groupby("User")["Duration (decimal)"].sum().reset_index()
        total_hrs_per_person.columns = ["Person", "Total Hours"]
        product_counts = product_counts.merge(total_hrs_per_person, on="Person", how="left")
        product_counts["Total Hours"] = product_counts["Total Hours"].round(1)

        # Add primary product
        primary = clockify[clockify["Normalized_Product"] != ""].groupby("User").apply(
            lambda x: x.groupby("Normalized_Product")["Duration (decimal)"].sum().idxmax(), include_groups=False
        ).reset_index()
        primary.columns = ["Person", "Primary Product"]
        product_counts = product_counts.merge(primary, on="Person", how="left")

        # Color code: 3+ products = warning
        def highlight_spread(row):
            if row["Products Worked On"] >= 4:
                return ["background-color: #ffcdd2"] * len(row)
            elif row["Products Worked On"] >= 3:
                return ["background-color: #fff9c4"] * len(row)
            return [""] * len(row)

        st.dataframe(
            product_counts[["Person", "Products Worked On", "Primary Product", "Total Hours"]].style.apply(highlight_spread, axis=1),
            width="stretch", hide_index=True,
        )
    else:
        st.info("No product-level data available.")


# ===== TAB 10: Weekly Digest & Alerts =====
with tabs[9]:
    st.header("Weekly Digest & Alerts")

    # Determine the latest full week in the data
    latest_date = clockify["Start Date"].max()
    if pd.isna(latest_date):
        st.warning("No date data available.")
    else:
        week_start = latest_date - timedelta(days=latest_date.weekday() + 7)
        week_end = week_start + timedelta(days=6)
        st.subheader(f"Week of {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")

        this_week = clockify[(clockify["Start Date"] >= week_start) & (clockify["Start Date"] <= week_end)]
        prev_week_start = week_start - timedelta(days=7)
        prev_week = clockify[(clockify["Start Date"] >= prev_week_start) & (clockify["Start Date"] < week_start)]

        tw_hours = this_week["Duration (decimal)"].sum()
        pw_hours = prev_week["Duration (decimal)"].sum()
        delta_hours = tw_hours - pw_hours

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Weekly Hours", f"{tw_hours:,.1f}", delta=f"{delta_hours:+.1f} vs prev")
        a2.metric("Active People", this_week["User"].nunique())
        a3.metric("Products", this_week[this_week["Normalized_Product"] != ""]["Normalized_Product"].nunique())
        a4.metric("DevOps Links", int((this_week["DevOps_Work_Item_ID"] != "").sum()))

        # --- ALERTS ---
        st.subheader("Alerts")
        alerts = []

        # Alert: People who logged 0 hours this week
        all_people = set(clockify["User"].unique())
        active_this_week = set(this_week["User"].unique())
        inactive = all_people - active_this_week
        if inactive:
            for person in sorted(inactive):
                alerts.append({"Severity": "Warning", "Category": "No Activity",
                    "Detail": f"**{person}** logged 0 hours this week"})

        # Alert: People with >50 hours this week
        weekly_by_person = this_week.groupby("User")["Duration (decimal)"].sum()
        overloaded = weekly_by_person[weekly_by_person > 50]
        for person, hrs in overloaded.items():
            alerts.append({"Severity": "Critical", "Category": "Overloaded",
                "Detail": f"**{person}** logged {hrs:.1f}h this week (>50h)"})

        # Alert: Entries without descriptions this week
        no_desc_this_week = this_week[this_week["Description"] == ""]
        if len(no_desc_this_week) > 5:
            top_offenders = no_desc_this_week.groupby("User").size().nlargest(3)
            names = ", ".join([f"{name} ({cnt})" for name, cnt in top_offenders.items()])
            alerts.append({"Severity": "Info", "Category": "Missing Descriptions",
                "Detail": f"**{len(no_desc_this_week)} entries** without descriptions. Top: {names}"})

        # Alert: Bugs opened on DevOps (if any are Fresh Bugz / New)
        new_bugs = devops[(devops["Work Item Type"] == "Bug") & (devops["Normalized_State"].isin(["New"]))]
        for prod in new_bugs["Normalized_Product"].unique():
            count = len(new_bugs[new_bugs["Normalized_Product"] == prod])
            if count > 0:
                alerts.append({"Severity": "Warning", "Category": "New Bugs",
                    "Detail": f"**{count} unresolved new bugs** on {prod}"})

        # Alert: Items stuck in same state (DevOps)
        stuck_states = ["In Progress", "In Review"]
        for prod in devops["Normalized_Product"].unique():
            if prod == "":
                continue
            prod_items = devops[(devops["Normalized_Product"] == prod) & (devops["Normalized_State"].isin(stuck_states))]
            if len(prod_items) > 20:
                alerts.append({"Severity": "Warning", "Category": "Potential Bottleneck",
                    "Detail": f"**{prod}** has {len(prod_items)} items in {'/'.join(stuck_states)}"})

        # Alert: High ratio of unclassified time
        if len(this_week) > 0:
            unclass_pct = len(this_week[this_week["Normalized_Product"] == ""]) / len(this_week) * 100
            if unclass_pct > 10:
                alerts.append({"Severity": "Info", "Category": "Data Quality",
                    "Detail": f"**{unclass_pct:.1f}%** of this week's entries have no product mapping"})

        # Alert: Suspicious entries this week
        sus_this_week = this_week[this_week["Is_Suspicious"].str.lower() == "true"]
        if len(sus_this_week) > 3:
            alerts.append({"Severity": "Info", "Category": "Suspicious Entries",
                "Detail": f"**{len(sus_this_week)} suspicious entries** this week (long durations, empty descriptions)"})

        if alerts:
            alerts_df = pd.DataFrame(alerts)
            # Sort: Critical first, then Warning, then Info
            severity_order = {"Critical": 0, "Warning": 1, "Info": 2}
            alerts_df["_sort"] = alerts_df["Severity"].map(severity_order)
            alerts_df = alerts_df.sort_values("_sort").drop(columns=["_sort"])

            for _, row in alerts_df.iterrows():
                if row["Severity"] == "Critical":
                    st.error(f"**{row['Category']}:** {row['Detail']}")
                elif row["Severity"] == "Warning":
                    st.warning(f"**{row['Category']}:** {row['Detail']}")
                else:
                    st.info(f"**{row['Category']}:** {row['Detail']}")
        else:
            st.success("No alerts this week.")

        # --- Weekly Summary by Product ---
        st.subheader("This Week by Product")
        if not this_week.empty:
            tw_by_product = this_week[this_week["Normalized_Product"] != ""].groupby(
                "Normalized_Product"
            )["Duration (decimal)"].sum().reset_index()
            tw_by_product.columns = ["Product", "Hours"]
            tw_by_product = tw_by_product.sort_values("Hours", ascending=False)
            tw_by_product["Hours"] = tw_by_product["Hours"].round(1)
            fig = px.bar(
                tw_by_product, x="Hours", y="Product", orientation="h",
                color="Product", color_discrete_map=PRODUCT_COLORS,
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(margin=COMPACT_MARGIN, showlegend=False, height=300)
            st.plotly_chart(fig, width="stretch")

        # --- Weekly Summary by Person ---
        st.subheader("This Week by Person")
        if not this_week.empty:
            tw_by_person = this_week.groupby("User")["Duration (decimal)"].sum().reset_index()
            tw_by_person.columns = ["Person", "Hours"]
            tw_by_person = tw_by_person.sort_values("Hours", ascending=False)
            tw_by_person["Hours"] = tw_by_person["Hours"].round(1)
            fig = px.bar(
                tw_by_person, x="Hours", y="Person", orientation="h",
                template=PLOTLY_TEMPLATE, color_discrete_sequence=["#42A5F5"],
            )
            fig.update_layout(margin=COMPACT_MARGIN, showlegend=False, height=max(300, len(tw_by_person) * 25))
            st.plotly_chart(fig, width="stretch")


# ===== TAB 11: Bug Aging =====
with tabs[10]:
    st.header("Bug Aging Timeline")
    st.markdown("How long have open bugs existed? Older bugs = higher risk of being forgotten.")

    bugs = devops[devops["Work Item Type"] == "Bug"].copy()
    open_bugs = bugs[~bugs["Normalized_State"].isin(DONE_STATES)].copy()

    if not open_bugs.empty:
        # Calculate age from ID ranges as proxy (higher ID = newer)
        # Since we don't have created_date, use ID as a rough proxy
        # Actually, let's check if we can derive age from tags or other signals
        open_bugs["ID"] = pd.to_numeric(open_bugs["ID"], errors="coerce")
        max_id = open_bugs["ID"].max()
        min_id = open_bugs["ID"].min()

        # Priority extraction from tags
        def extract_priority(tags):
            tags_lower = str(tags).lower()
            if "critical" in tags_lower:
                return "Critical"
            elif "high" in tags_lower:
                return "High"
            elif "medium" in tags_lower:
                return "Medium"
            elif "low" in tags_lower:
                return "Low"
            return "Unspecified"

        open_bugs["Priority"] = open_bugs["Tags"].apply(extract_priority)

        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Total Open Bugs", len(open_bugs))
        b2.metric("Critical", len(open_bugs[open_bugs["Priority"] == "Critical"]))
        b3.metric("High", len(open_bugs[open_bugs["Priority"] == "High"]))
        b4.metric("Medium + Low", len(open_bugs[open_bugs["Priority"].isin(["Medium", "Low"])]))

        # Bug scatter: X = ID (proxy for age, lower = older), Y = product, color = priority
        st.subheader("Open Bugs by Age (ID as proxy)")
        st.caption("Lower IDs are older. Dots furthest left have been open the longest.")

        priority_colors = {"Critical": "#D32F2F", "High": "#F57C00", "Medium": "#FBC02D", "Low": "#66BB6A", "Unspecified": "#90A4AE"}
        fig = px.strip(
            open_bugs, x="ID", y="Normalized_Product", color="Priority",
            hover_data=["Title", "Normalized_State", "Assigned To", "Tags"],
            color_discrete_map=priority_colors,
            template=PLOTLY_TEMPLATE,
            category_orders={"Priority": ["Critical", "High", "Medium", "Low", "Unspecified"]},
        )
        fig.update_layout(margin=COMPACT_MARGIN, height=350, xaxis_title="Work Item ID (lower = older)")
        fig.update_traces(marker=dict(size=10, opacity=0.8))
        st.plotly_chart(fig, width="stretch")

        # Bugs by product and priority
        st.subheader("Open Bugs by Product & Priority")
        bug_summary = open_bugs.groupby(["Normalized_Product", "Priority"]).size().reset_index(name="Count")
        fig = px.bar(
            bug_summary, x="Normalized_Product", y="Count", color="Priority",
            color_discrete_map=priority_colors, template=PLOTLY_TEMPLATE,
            category_orders={"Priority": ["Critical", "High", "Medium", "Low", "Unspecified"]},
        )
        fig.update_layout(margin=COMPACT_MARGIN, height=350, xaxis_title="Product", yaxis_title="Bug Count")
        st.plotly_chart(fig, width="stretch")

        # Detailed table: oldest bugs first (lowest ID)
        st.subheader("Open Bugs Detail (oldest first)")
        display_cols = ["ID", "Title", "Normalized_Product", "Priority", "Normalized_State", "Assigned To", "Tags"]
        available_cols = [c for c in display_cols if c in open_bugs.columns]
        st.dataframe(
            open_bugs[available_cols].sort_values("ID", ascending=True),
            width="stretch", hide_index=True, height=400,
        )

        # Version-level bug concentration
        st.subheader("Bug Concentration by Version")
        version_bugs = open_bugs[open_bugs["Normalized_Version"] != ""].groupby(
            ["Normalized_Product", "Normalized_Version"]
        ).size().reset_index(name="Open Bugs")
        version_bugs = version_bugs.sort_values("Open Bugs", ascending=False)
        if not version_bugs.empty:
            fig = px.bar(
                version_bugs, x="Open Bugs",
                y=version_bugs["Normalized_Product"] + " " + version_bugs["Normalized_Version"],
                orientation="h", template=PLOTLY_TEMPLATE,
                color="Normalized_Product", color_discrete_map=PRODUCT_COLORS,
            )
            fig.update_layout(margin=COMPACT_MARGIN, height=300, showlegend=False, yaxis_title="Product Version")
            st.plotly_chart(fig, width="stretch")
    else:
        st.success("No open bugs found.")


# ===== TAB 12: Knowledge Transfer Risk =====
with tabs[11]:
    st.header("Knowledge Transfer Risk")
    st.markdown("Identify single points of failure — people who are the sole contributor to critical areas.")

    # For each product, calculate each person's share of total hours
    product_person = clockify[clockify["Normalized_Product"] != ""].groupby(
        ["Normalized_Product", "User"]
    )["Duration (decimal)"].sum().reset_index()
    product_person.columns = ["Product", "Person", "Hours"]

    product_totals = product_person.groupby("Product")["Hours"].sum().reset_index()
    product_totals.columns = ["Product", "Total_Hours"]

    product_person = product_person.merge(product_totals, on="Product")
    product_person["Share %"] = (product_person["Hours"] / product_person["Total_Hours"] * 100).round(1)
    product_person["Hours"] = product_person["Hours"].round(1)

    # Bus factor: how many people contribute >5% of effort to a product
    bus_factor = product_person[product_person["Share %"] >= 5].groupby("Product")["Person"].count().reset_index()
    bus_factor.columns = ["Product", "Bus Factor"]
    bus_factor = bus_factor.merge(product_totals, on="Product")
    bus_factor["Total_Hours"] = bus_factor["Total_Hours"].round(1)
    bus_factor = bus_factor.sort_values("Bus Factor")

    st.subheader("Bus Factor by Product")
    st.caption("Bus Factor = number of people contributing >= 5% of effort. Lower = higher risk.")

    def color_bus(val):
        if val <= 1:
            return "background-color: #ffcdd2"
        elif val <= 2:
            return "background-color: #fff9c4"
        return "background-color: #c8e6c9"

    styled = bus_factor[["Product", "Bus Factor", "Total_Hours"]].style.map(
        color_bus, subset=["Bus Factor"]
    )
    st.dataframe(styled, width="stretch", hide_index=True)

    # Dominant contributors (>60% share)
    st.subheader("Single Points of Failure")
    st.caption("People with >60% of a product's total hours — if they leave, knowledge is at serious risk.")

    spof = product_person[product_person["Share %"] > 60].sort_values("Share %", ascending=False)
    if not spof.empty:
        for _, row in spof.iterrows():
            st.error(
                f"**{row['Person']}** owns **{row['Share %']}%** of {row['Product']} "
                f"({row['Hours']}h / {row['Total_Hours']}h)"
            )
    else:
        st.success("No single person dominates >60% of any product.")

    # Full heatmap: share % per person per product
    st.subheader("Effort Share Heatmap")
    share_pivot = product_person.pivot_table(
        index="Person", columns="Product", values="Share %", fill_value=0,
    )
    # Only show people with significant contributions
    share_pivot = share_pivot[share_pivot.max(axis=1) >= 5]
    share_pivot = share_pivot.sort_values(share_pivot.columns.tolist(), ascending=False)

    if not share_pivot.empty:
        fig = px.imshow(
            share_pivot.values,
            x=share_pivot.columns.tolist(),
            y=share_pivot.index.tolist(),
            color_continuous_scale=[[0, "#e8f5e9"], [0.3, "#fff9c4"], [0.6, "#ffcc80"], [1.0, "#ef5350"]],
            aspect="auto",
            labels=dict(x="Product", y="Person", color="Share %"),
            template=PLOTLY_TEMPLATE,
            zmin=0, zmax=100,
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=max(350, len(share_pivot) * 28))
        for i, row_name in enumerate(share_pivot.index):
            for j, col_name in enumerate(share_pivot.columns):
                val = share_pivot.iloc[i, j]
                if val > 0:
                    fig.add_annotation(
                        x=j, y=i, text=f"{val:.0f}%", showarrow=False,
                        font=dict(size=10, color="white" if val > 50 else "black"),
                    )
        st.plotly_chart(fig, width="stretch")

    # Recommendations
    st.subheader("Recommended Actions")
    if not spof.empty:
        for _, row in spof.iterrows():
            st.warning(
                f"**{row['Product']}:** Pair {row['Person']} with another team member. "
                f"Consider knowledge transfer sessions or documentation sprints."
            )
    # Low bus-factor products
    low_bf = bus_factor[bus_factor["Bus Factor"] <= 2]
    for _, row in low_bf.iterrows():
        if row["Total_Hours"] > 50:  # Only flag products with meaningful effort
            st.info(
                f"**{row['Product']}:** Bus factor of {row['Bus Factor']}. "
                f"Consider cross-training or rotating a team member in."
            )


# ===== TAB 13: Clockify Hygiene =====
with tabs[12]:
    st.header("Clockify Hygiene Score")
    st.markdown("How well is each person logging their time? Better hygiene = better data = better decisions.")

    hygiene_data = []
    for user in clockify["User"].unique():
        if user == "":
            continue
        user_entries = clockify[clockify["User"] == user]
        total_entries = len(user_entries)
        if total_entries == 0:
            continue

        # Metric 1: Description fill rate
        has_desc = (user_entries["Description"] != "").sum()
        desc_rate = has_desc / total_entries * 100

        # Metric 2: Tag fill rate
        has_tags = (user_entries["Tags"] != "").sum()
        tag_rate = has_tags / total_entries * 100

        # Metric 3: DevOps ID reference rate
        has_devops = (user_entries["DevOps_Work_Item_ID"] != "").sum()
        devops_rate = has_devops / total_entries * 100

        # Metric 4: Average entry duration (too short < 0.25h or too long > 8h is bad)
        avg_duration = user_entries["Duration (decimal)"].mean()
        duration_score = 100
        if avg_duration < 0.25:
            duration_score = 30  # too granular
        elif avg_duration > 6:
            duration_score = 40  # likely forgot timer
        elif avg_duration > 4:
            duration_score = 70
        elif avg_duration < 0.5:
            duration_score = 60

        # Metric 5: Suspicious entry rate (inverse)
        suspicious = (user_entries["Is_Suspicious"].str.lower() == "true").sum()
        clean_rate = (1 - suspicious / total_entries) * 100

        # Composite score (weighted)
        composite = (
            desc_rate * 0.30 +
            tag_rate * 0.20 +
            devops_rate * 0.15 +
            duration_score * 0.15 +
            clean_rate * 0.20
        )

        total_hours = user_entries["Duration (decimal)"].sum()
        team = user_entries["Team_Domain"].mode().iloc[0] if not user_entries["Team_Domain"].mode().empty else ""

        hygiene_data.append({
            "Person": user,
            "Team": team,
            "Entries": total_entries,
            "Total Hours": round(total_hours, 1),
            "Description %": round(desc_rate, 1),
            "Tags %": round(tag_rate, 1),
            "DevOps Ref %": round(devops_rate, 1),
            "Avg Duration (h)": round(avg_duration, 2),
            "Clean Entry %": round(clean_rate, 1),
            "Hygiene Score": round(composite, 1),
        })

    hygiene_df = pd.DataFrame(hygiene_data).sort_values("Hygiene Score", ascending=False)

    if not hygiene_df.empty:
        # KPIs
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Avg Score", f"{hygiene_df['Hygiene Score'].mean():.1f}/100")
        h2.metric("Best", f"{hygiene_df.iloc[0]['Hygiene Score']}")
        h3.metric("Worst", f"{hygiene_df.iloc[-1]['Hygiene Score']}")
        h4.metric("People Scored", len(hygiene_df))

        # Horizontal bar chart of hygiene scores
        st.subheader("Hygiene Score by Person")
        fig = px.bar(
            hygiene_df.sort_values("Hygiene Score", ascending=True),
            x="Hygiene Score", y="Person", orientation="h",
            color="Hygiene Score",
            color_continuous_scale=[[0, "#ef5350"], [0.5, "#FBC02D"], [1.0, "#66BB6A"]],
            range_color=[0, 100],
            template=PLOTLY_TEMPLATE,
            hover_data=["Total Hours", "Description %", "Tags %", "DevOps Ref %"],
        )
        fig.update_layout(margin=COMPACT_MARGIN, height=max(400, len(hygiene_df) * 28), showlegend=False)
        st.plotly_chart(fig, width="stretch")

        # Breakdown radar chart for top/bottom 3
        st.subheader("Score Breakdown")
        radar_metrics = ["Description %", "Tags %", "DevOps Ref %", "Clean Entry %"]

        col_top, col_bottom = st.columns(2)

        with col_top:
            st.markdown("**Top 3 (best hygiene)**")
            fig = go.Figure()
            for _, row in hygiene_df.head(3).iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[row[m] for m in radar_metrics],
                    theta=radar_metrics,
                    fill="toself",
                    name=row["Person"],
                    opacity=0.6,
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                template=PLOTLY_TEMPLATE, margin=COMPACT_MARGIN, height=350,
                showlegend=True, legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(fig, width="stretch")

        with col_bottom:
            st.markdown("**Bottom 3 (need improvement)**")
            fig = go.Figure()
            for _, row in hygiene_df.tail(3).iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[row[m] for m in radar_metrics],
                    theta=radar_metrics,
                    fill="toself",
                    name=row["Person"],
                    opacity=0.6,
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                template=PLOTLY_TEMPLATE, margin=COMPACT_MARGIN, height=350,
                showlegend=True, legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(fig, width="stretch")

        # Full detail table
        st.subheader("Full Hygiene Detail")

        def color_score(val):
            if isinstance(val, (int, float)):
                if val >= 70:
                    return "background-color: #c8e6c9"
                elif val >= 40:
                    return "background-color: #fff9c4"
                else:
                    return "background-color: #ffcdd2"
            return ""

        st.dataframe(
            hygiene_df.style.map(color_score, subset=["Hygiene Score", "Description %", "Tags %", "DevOps Ref %", "Clean Entry %"]),
            width="stretch", hide_index=True,
        )

        # Actionable recommendations
        st.subheader("Improvement Actions")
        low_desc = hygiene_df[hygiene_df["Description %"] < 50].sort_values("Description %")
        if not low_desc.empty:
            names = ", ".join(low_desc.head(5)["Person"].tolist())
            st.warning(f"**Add descriptions:** {names} — over half their entries have no description.")

        low_tags = hygiene_df[hygiene_df["Tags %"] < 20].sort_values("Tags %")
        if not low_tags.empty:
            names = ", ".join(low_tags.head(5)["Person"].tolist())
            st.info(f"**Use tags:** {names} — most entries lack category tags (Meeting, Development, etc.).")

        low_devops = hygiene_df[(hygiene_df["DevOps Ref %"] < 10) & (hygiene_df["Total Hours"] > 30)].sort_values("DevOps Ref %")
        if not low_devops.empty:
            names = ", ".join(low_devops.head(5)["Person"].tolist())
            st.info(f"**Reference DevOps IDs:** {names} — include #WorkItemID in descriptions for cross-system traceability.")
    else:
        st.info("No user data available.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
date_str = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}" if min_date and max_date else "N/A"
st.markdown(f"""
<div style="margin-top:40px; padding:16px 0; border-top:2px solid {CORP_BORDER}; text-align:center;">
    <span style="color:{CORP_MUTED}; font-size:0.78rem;">
        Fotopia Dashboard v2.0 &nbsp;&bull;&nbsp; Data: {date_str} &nbsp;&bull;&nbsp; Powered by Fotopia PMO
    </span>
</div>
""", unsafe_allow_html=True)
