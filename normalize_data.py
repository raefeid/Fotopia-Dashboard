#!/usr/bin/env python3
"""
Fotopia Data Normalization Script
==================================
Processes Clockify time entries and Azure DevOps work items,
applies normalization rules, and produces unified analysis outputs.
"""

import pandas as pd
import numpy as np
import re
import os
from collections import Counter

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CLOCKIFY_PATH = os.path.expanduser(
    "~/Downloads/Clockify_Time_Report_Detailed_01_01_2026-31_12_2026.csv"
)
DEVOPS_FOTOCAPTURE_PATH = os.path.expanduser("~/Downloads/data (3).csv")
DEVOPS_FOTOGNIZE_PATH = os.path.expanduser("~/Downloads/data (1).csv")
DEVOPS_FOTOFIND_PATH = os.path.expanduser("~/Downloads/data.csv")

OUTPUT_DIR = os.path.expanduser("~/My Claude/fotopia-dashboard/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------
CLOCKIFY_TO_PRODUCT = {
    "FotoCapture": "FotoCapture",
    "FotoCapture V6.5": "FotoCapture",
    "FotoCapture V6.6": "FotoCapture",
    "FotoCapture V6.7": "FotoCapture",
    "Fotocapture Testing": "FotoCapture",
    "Foto Gnize V2": "Fotognize",
    "Foto GnizeV1": "Fotognize",
    "FotoGnize": "Fotognize",
    "Fotognize Testing": "Fotognize",
    "Fotofind": "FotoFind",
    "Fotofind AI": "FotoFind",
    "FotoScan": "FotoScan",
    "Fototracker": "Fototracker",
    "DET": "DET",
    "Fotoverifai": "FotoVerifAI",
    "FotoAnnotate": "FotoAnnotate",
    "KFH": None,
    "DU AMC": None,
    "Global Pharma": None,
    "Fotopia": None,
    "R&D": None,
    "Miscellaneous": None,
    "Demo Support": None,
    "Marketing": None,
}

# Version from project name
PROJECT_VERSION_MAP = {
    "FotoCapture V6.5": "6.5",
    "FotoCapture V6.6": "6.6",
    "FotoCapture V6.7": "6.7",
    "Foto Gnize V2": "2.0",
    "Foto GnizeV1": "1.0",
}

# Version from tags
TAG_VERSION_PATTERNS = [
    (r"\bCapture 6\.5\b", "6.5"),
    (r"\bCapture 6\.6\b", "6.6"),
    (r"\bCapture 6\.7\b", "6.7"),
    (r"\bV6\.7\b", "6.7"),
    (r"\bV6\.6\.1\b", "6.6.1"),
    (r"\bV6\.6\b", "6.6"),
    (r"\bV6\.5\b", "6.5"),
    (r"\bV1\.0\b", "1.0"),
    (r"\bv2\.0\b", "2.0"),
    (r"\bV2\.0\b", "2.0"),
]

# Client detection from project
PROJECT_CLIENT_MAP = {
    "KFH": "KFH (Kuwait Finance House)",
    "DU AMC": "DU AMC",
    "Global Pharma": "Global Pharma",
}

# Client detection from tags
TAG_CLIENT_MAP = {
    "Eneo": "Eneo",
    "ENEO": "Eneo",
    "UAQ": "UAQ (Umm Al Quwain)",
    "Shj Gov": "Sharjah Government",
    "Shj": "Sharjah Government",
    "Dubai Municipality": "Dubai Municipality",
}

# Client detection from description keywords
DESC_CLIENT_PATTERNS = [
    ("Eneo", "Eneo"),
    ("KFH", "KFH (Kuwait Finance House)"),
    ("UAQ", "UAQ (Umm Al Quwain)"),
    ("RTA", "RTA"),
]

# Work category from tags
TAG_WORK_CATEGORY = {
    "Meeting": "Meeting",
    "Development": "Development",
    "Deployment": "Deployment",
    "Bug Fixes": "Bug Fix",
    "Review": "Code Review",
    "Consultation": "Consultation",
    "Testing": "QA/Testing",
    "Troubleshooting": "Troubleshooting",
    "Planning": "Planning",
    "Knowledge Graph": "Feature - Knowledge Graph",
    "Chat API": "Feature - Chat API",
    "Demo": "Pre-sales/Demo",
}

# Fotopia bucket auto-classification by email
FOTOPIA_EMAIL_PRODUCT = {
    "i-nancy.amr@fotopiatech.com": "Fotognize",
    "i-mohamed.yasser@fotopiatech.com": "Fotognize",
    "i-abdulrahman.saeed@fotopiatech.com": "Fotognize",
    "sameh.amnoun@fotopiatech.com": "Internal/Management",
    "salma.elnadi@fotopiatech.com": "Unknown",
}

# DevOps state normalization
FOTOGNIZE_STATE_MAP = {
    "\U0001f9c3 Concept": "Backlog",
    "\U0001f4dd Queued Up": "Ready",
    "\u2728 Sparked": "Ready",
    "\U0001f4d0 Designing": "In Progress",
    "\u2705 Greenlit": "In Progress",
    "\u2699 In Dev": "In Progress",
    "\U0001f9fc Polished": "In Review",
    "\U0001f9ecDocked and Locked": "In Review",
    "\U0001f4e6 Boxed Up": "Done",
    "\U0001f680 Released": "Released",
    "\u23f8 On Ice": "On Hold",
    "\U0001f5d1 Dropped": "Cancelled",
    "Fresh Bugz": "New",
}

FOTOCAPTURE_STATE_MAP = {
    "New": "New",
    "Active": "In Progress",
    "Resolved": "Done",
    "Closed": "Closed",
    "Design": "In Progress",
}

FOTOFIND_STATE_MAP = {
    "New": "New",
    "Active": "In Progress",
    "Closed": "Closed",
    "Resolved": "Done",
    "Removed": "Cancelled",
}

# Project type classification
PROJECT_TYPE_MAP = {
    "KFH": "Client Project",
    "DU AMC": "Client Project",
    "Global Pharma": "Client Project",
    "FotoCapture": "Product Development",
    "FotoCapture V6.5": "Product Development",
    "FotoCapture V6.6": "Product Development",
    "FotoCapture V6.7": "Product Development",
    "Fotocapture Testing": "QA",
    "Foto Gnize V2": "Product Development",
    "Foto GnizeV1": "Product Development",
    "FotoGnize": "Product Development",
    "Fotognize Testing": "QA",
    "Fotofind": "Product Development",
    "Fotofind AI": "Product Development",
    "FotoScan": "Product Development",
    "Fototracker": "Product Development",
    "DET": "Product Development",
    "Fotoverifai": "Product Development",
    "FotoAnnotate": "Product Development",
    "R&D": "Research",
    "Demo Support": "Pre-sales",
    "Marketing": "Marketing",
    "Miscellaneous": "Unclassified",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def safe_str(val):
    """Return stripped string, empty string for NaN."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def extract_version_from_tags(tags_str):
    """Extract the most specific version from a tags string."""
    tags = safe_str(tags_str)
    if not tags:
        return ""
    for pattern, version in TAG_VERSION_PATTERNS:
        if re.search(pattern, tags):
            return version
    return ""


def extract_client_from_tags(tags_str):
    """Detect client from tag string."""
    tags = safe_str(tags_str)
    if not tags:
        return ""
    # Split tags and check each one
    tag_list = [t.strip() for t in tags.split(";")]
    for tag in tag_list:
        tag_clean = tag.strip()
        if tag_clean in TAG_CLIENT_MAP:
            return TAG_CLIENT_MAP[tag_clean]
    return ""


def extract_client_from_description(desc):
    """Detect client from description text."""
    desc = safe_str(desc)
    if not desc:
        return ""
    for keyword, client in DESC_CLIENT_PATTERNS:
        if keyword.lower() in desc.lower():
            return client
    return ""


def extract_devops_id(desc):
    """Extract DevOps work item ID from Clockify description (#NNNNN)."""
    desc = safe_str(desc)
    match = re.search(r"#(\d{4,6})", desc)
    return match.group(1) if match else ""


def extract_work_category(tags_str):
    """Determine work category from tags."""
    tags = safe_str(tags_str)
    if not tags:
        return ""
    tag_list = [t.strip() for t in tags.split(";")]
    for tag in tag_list:
        tag_clean = tag.strip()
        if tag_clean in TAG_WORK_CATEGORY:
            return TAG_WORK_CATEGORY[tag_clean]
    return ""


def classify_team_domain(email):
    """Classify team from email domain."""
    email = safe_str(email).lower()
    if "@fotopiatech.com" in email:
        return "Fotopia (Internal)"
    if "@infasme.com" in email:
        return "InfaSME (Partner)"
    return "Unknown"


def parse_duration_decimal(val):
    """Parse duration decimal, return float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def extract_assigned_email(assigned_to):
    """Extract email from 'Name <email>' format."""
    assigned = safe_str(assigned_to)
    match = re.search(r"<([^>]+)>", assigned)
    if match:
        return match.group(1).strip()
    # Sometimes just the name, no email
    return assigned.lower().replace(" ", ".") if assigned else ""


def extract_assigned_name(assigned_to):
    """Extract display name from 'Name <email>' format."""
    assigned = safe_str(assigned_to)
    match = re.match(r"^([^<]+)", assigned)
    if match:
        return match.group(1).strip()
    return assigned


# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
print("=" * 70)
print("FOTOPIA DATA NORMALIZATION")
print("=" * 70)

print("\n[1/8] Loading CSV files...")

clockify = pd.read_csv(CLOCKIFY_PATH, encoding="utf-8-sig")
devops_fc = pd.read_csv(DEVOPS_FOTOCAPTURE_PATH, encoding="utf-8-sig")
devops_fg = pd.read_csv(DEVOPS_FOTOGNIZE_PATH, encoding="utf-8-sig")
devops_ff = pd.read_csv(DEVOPS_FOTOFIND_PATH, encoding="utf-8-sig")

print(f"  Clockify:           {len(clockify):>6} entries")
print(f"  DevOps FotoCapture: {len(devops_fc):>6} items")
print(f"  DevOps Fotognize:   {len(devops_fg):>6} items")
print(f"  DevOps FotoFind:    {len(devops_ff):>6} items")

# Tag source board
devops_fc["Source_Board"] = "FotoCapture"
devops_fg["Source_Board"] = "Fotognize"
devops_ff["Source_Board"] = "FotoFind"

# Merge all DevOps
devops_all = pd.concat([devops_fc, devops_fg, devops_ff], ignore_index=True)
print(f"  DevOps total:       {len(devops_all):>6} items")

# ---------------------------------------------------------------------------
# 2. Normalize Clockify
# ---------------------------------------------------------------------------
print("\n[2/8] Normalizing Clockify entries...")

mapping_audit = []  # Collect all mapping decisions


def audit(raw, normalized, confidence, method, explanation, field):
    mapping_audit.append({
        "Field": field,
        "Raw_Value": raw,
        "Normalized_Value": normalized,
        "Confidence": confidence,
        "Method": method,
        "Explanation": explanation,
    })


# --- Product ---
products = []
confidences = []
methods = []
for _, row in clockify.iterrows():
    project = safe_str(row.get("Project", ""))
    email = safe_str(row.get("Email", "")).lower()
    desc = safe_str(row.get("Description", ""))

    if project in CLOCKIFY_TO_PRODUCT and CLOCKIFY_TO_PRODUCT[project] is not None:
        prod = CLOCKIFY_TO_PRODUCT[project]
        conf = 1.0
        meth = "direct_project_map"
        audit(project, prod, conf, meth, f"Project '{project}' maps to '{prod}'", "Product")
    elif project == "Fotopia":
        # Auto-classify from email
        if email in FOTOPIA_EMAIL_PRODUCT:
            prod = FOTOPIA_EMAIL_PRODUCT[email]
            conf = 0.75
            meth = "fotopia_email_autoclassify"
            audit(project, prod, conf, meth,
                  f"Fotopia bucket: email '{email}' -> '{prod}'", "Product")
        else:
            prod = "Unknown"
            conf = 0.3
            meth = "fotopia_unmatched"
            audit(project, prod, conf, meth,
                  f"Fotopia bucket: email '{email}' not in known map", "Product")
    elif project in CLOCKIFY_TO_PRODUCT:
        # None-mapped projects (client projects, etc.)
        prod = ""
        conf = 1.0
        meth = "client_or_nonproduct"
        audit(project, prod, conf, meth,
              f"Project '{project}' is not a product", "Product")
    else:
        prod = "Unknown"
        conf = 0.5
        meth = "unmapped_project"
        audit(project, prod, conf, meth,
              f"Project '{project}' not in mapping table", "Product")

    products.append(prod)
    confidences.append(conf)
    methods.append(meth)

clockify["Normalized_Product"] = products
clockify["Mapping_Confidence"] = confidences
clockify["Mapping_Method"] = methods

# --- Version ---
versions = []
for _, row in clockify.iterrows():
    project = safe_str(row.get("Project", ""))
    tags = safe_str(row.get("Tags", ""))

    ver = PROJECT_VERSION_MAP.get(project, "")
    if not ver:
        ver = extract_version_from_tags(tags)
    if ver:
        audit(f"project='{project}', tags='{tags}'", ver, 1.0,
              "version_extract", f"Version '{ver}' extracted", "Version")
    versions.append(ver)

clockify["Normalized_Version"] = versions

# --- Client ---
clients = []
for _, row in clockify.iterrows():
    project = safe_str(row.get("Project", ""))
    tags = safe_str(row.get("Tags", ""))
    desc = safe_str(row.get("Description", ""))

    client = ""
    source = ""

    # Check project name first
    if project in PROJECT_CLIENT_MAP:
        client = PROJECT_CLIENT_MAP[project]
        source = "project_name"
    # Then tags
    if not client:
        client = extract_client_from_tags(tags)
        if client:
            source = "tag"
    # Then description
    if not client:
        client = extract_client_from_description(desc)
        if client:
            source = "description"

    if client:
        audit(f"project='{project}', tags='{tags}', desc='{desc[:50]}'",
              client, 0.9 if source == "project_name" else 0.8,
              f"client_{source}", f"Client '{client}' detected from {source}", "Client")
    clients.append(client)

clockify["Normalized_Client"] = clients

# --- Work Category ---
clockify["Work_Category"] = clockify["Tags"].apply(
    lambda t: extract_work_category(safe_str(t))
)

# --- Project Type ---
project_types = []
for _, row in clockify.iterrows():
    project = safe_str(row.get("Project", ""))
    email = safe_str(row.get("Email", "")).lower()

    if project in PROJECT_TYPE_MAP:
        pt = PROJECT_TYPE_MAP[project]
    elif project == "Fotopia":
        if email == "sameh.amnoun@fotopiatech.com":
            pt = "Internal/Management"
        elif email in FOTOPIA_EMAIL_PRODUCT:
            pt = "Product R&D"
        else:
            pt = "Unclassified"
    else:
        pt = "Unclassified"

    project_types.append(pt)

clockify["Project_Type"] = project_types

# --- Team Domain ---
clockify["Team_Domain"] = clockify["Email"].apply(
    lambda e: classify_team_domain(safe_str(e))
)

# --- DevOps Work Item ID ---
clockify["DevOps_Work_Item_ID"] = clockify["Description"].apply(
    lambda d: extract_devops_id(safe_str(d))
)

# --- Suspicious Entry Detection ---
suspicious_flags = []
suspicious_reasons = []

for _, row in clockify.iterrows():
    reasons = []
    duration_dec = parse_duration_decimal(row.get("Duration (decimal)", 0))
    desc = safe_str(row.get("Description", ""))
    tags = safe_str(row.get("Tags", ""))
    email = safe_str(row.get("Email", "")).lower()
    user = safe_str(row.get("User", ""))

    if duration_dec > 10:
        reasons.append("Duration > 10 hours")
    if not desc and duration_dec > 1:
        reasons.append("Empty description with duration > 1 hour")
    if not desc and not tags:
        reasons.append("Empty description AND empty tags (low quality)")
    if "thejaswini.nagaraju" in email.lower():
        reasons.append("Thejaswini.nagaraju: possible automated minimal logging (0:08 pattern)")

    suspicious_flags.append(bool(reasons))
    suspicious_reasons.append("; ".join(reasons) if reasons else "")

clockify["Is_Suspicious"] = suspicious_flags
clockify["Suspicious_Reason"] = suspicious_reasons

print(f"  Products mapped: {sum(1 for p in products if p and p not in ('Unknown', ''))}")
print(f"  Versions found:  {sum(1 for v in versions if v)}")
print(f"  Clients found:   {sum(1 for c in clients if c)}")
print(f"  Suspicious:      {sum(suspicious_flags)}")

# ---------------------------------------------------------------------------
# 3. Normalize DevOps
# ---------------------------------------------------------------------------
print("\n[3/8] Normalizing DevOps entries...")

# Normalized Product
devops_product_map = {
    "FotoCapture": "FotoCapture",
    "Fotognize": "Fotognize",
    "FotoFind": "FotoFind",
}
devops_all["Normalized_Product"] = devops_all["Source_Board"].map(devops_product_map)

# Normalized Version from tags
devops_all["Normalized_Version"] = devops_all["Tags"].apply(
    lambda t: extract_version_from_tags(safe_str(t))
)

# Normalized Client from tags
devops_clients = []
for _, row in devops_all.iterrows():
    tags = safe_str(row.get("Tags", ""))
    client = ""
    if tags:
        tag_list = [t.strip() for t in tags.split(";")]
        for tag in tag_list:
            tag_clean = tag.strip()
            if tag_clean in TAG_CLIENT_MAP:
                client = TAG_CLIENT_MAP[tag_clean]
                break
    devops_clients.append(client)
devops_all["Normalized_Client"] = devops_clients

# Normalized State
def normalize_devops_state(row):
    state = safe_str(row.get("State", ""))
    board = safe_str(row.get("Source_Board", ""))

    if board == "Fotognize":
        return FOTOGNIZE_STATE_MAP.get(state, state)
    elif board == "FotoCapture":
        return FOTOCAPTURE_STATE_MAP.get(state, state)
    elif board == "FotoFind":
        return FOTOFIND_STATE_MAP.get(state, state)
    return state

devops_all["Normalized_State"] = devops_all.apply(normalize_devops_state, axis=1)

# Assigned Email and Team Domain
devops_all["Assigned_Email"] = devops_all["Assigned To"].apply(
    lambda a: extract_assigned_email(safe_str(a))
)
devops_all["Team_Domain"] = devops_all["Assigned_Email"].apply(
    lambda e: classify_team_domain(e)
)

print(f"  States normalized: {len(devops_all)}")
print(f"  Unique states: {devops_all['Normalized_State'].nunique()}")

# ---------------------------------------------------------------------------
# 4. Cross-system links
# ---------------------------------------------------------------------------
print("\n[4/8] Building cross-system links...")

clockify_with_ids = clockify[clockify["DevOps_Work_Item_ID"] != ""].copy()
devops_all["ID_str"] = devops_all["ID"].astype(str).str.strip()

cross_links = clockify_with_ids.merge(
    devops_all,
    left_on="DevOps_Work_Item_ID",
    right_on="ID_str",
    how="inner",
    suffixes=("_clockify", "_devops"),
)

print(f"  Clockify entries with DevOps IDs: {len(clockify_with_ids)}")
print(f"  Matched cross-system links:       {len(cross_links)}")

# Select relevant columns for output
cross_link_cols = [
    "DevOps_Work_Item_ID", "User", "Email",
    "Description", "Duration (decimal)", "Start Date",
    "Project", "Normalized_Product_clockify",
    "ID", "Work Item Type", "Title", "Assigned To",
    "State", "Normalized_State", "Source_Board",
]
existing_cols = [c for c in cross_link_cols if c in cross_links.columns]
cross_links_out = cross_links[existing_cols].copy()

# ---------------------------------------------------------------------------
# 5. Person master
# ---------------------------------------------------------------------------
print("\n[5/8] Building person master list...")

clockify["Duration_Dec"] = clockify["Duration (decimal)"].apply(parse_duration_decimal)

person_data = []
for email, group in clockify.groupby("Email"):
    email_str = safe_str(email)
    display_name = safe_str(group.iloc[0]["User"])
    domain = classify_team_domain(email_str)
    total_hours = group["Duration_Dec"].sum()
    entry_count = len(group)

    # Primary product = most frequent non-empty Normalized_Product
    prods = group["Normalized_Product"][
        (group["Normalized_Product"] != "") & (group["Normalized_Product"] != "Unknown")
    ]
    primary_product = prods.mode().iloc[0] if len(prods) > 0 and len(prods.mode()) > 0 else "Unknown"

    person_data.append({
        "Email": email_str,
        "Display_Name": display_name,
        "Team_Domain": domain,
        "Primary_Product": primary_product,
        "Total_Hours": round(total_hours, 2),
        "Entry_Count": entry_count,
    })

person_master = pd.DataFrame(person_data)
print(f"  Unique people: {len(person_master)}")

# ---------------------------------------------------------------------------
# 6. Product summary
# ---------------------------------------------------------------------------
print("\n[6/8] Building product summary...")

product_data = []
all_products = set(
    clockify["Normalized_Product"][
        (clockify["Normalized_Product"] != "") & (clockify["Normalized_Product"] != "Unknown")
    ].unique()
) | set(devops_all["Normalized_Product"].dropna().unique())

for prod in sorted(all_products):
    # Clockify hours
    ck_mask = clockify["Normalized_Product"] == prod
    total_hours = clockify.loc[ck_mask, "Duration_Dec"].sum()

    # DevOps items
    dv_mask = devops_all["Normalized_Product"] == prod
    dv_items = devops_all[dv_mask]
    total_devops = len(dv_items)
    bugs = len(dv_items[dv_items["Work Item Type"] == "Bug"])
    features = len(dv_items[dv_items["Work Item Type"] == "Feature"])
    tasks = len(dv_items[dv_items["Work Item Type"].isin(["Task", "Test Case", "Issue"])])

    open_states = {"New", "In Progress", "Ready", "Backlog", "In Review", "On Hold"}
    closed_states = {"Done", "Closed", "Released", "Cancelled"}
    open_items = len(dv_items[dv_items["Normalized_State"].isin(open_states)])
    closed_items = len(dv_items[dv_items["Normalized_State"].isin(closed_states)])

    product_data.append({
        "Product": prod,
        "Total_Clockify_Hours": round(total_hours, 2),
        "Total_DevOps_Items": total_devops,
        "Bugs": bugs,
        "Features": features,
        "Tasks": tasks,
        "Open_Items": open_items,
        "Closed_Items": closed_items,
    })

product_summary = pd.DataFrame(product_data)
print(f"  Products tracked: {len(product_summary)}")

# ---------------------------------------------------------------------------
# 7. Client summary
# ---------------------------------------------------------------------------
print("\n[7/8] Building client summary...")

client_data = []
# Combine Clockify and DevOps client info
ck_clients = clockify[clockify["Normalized_Client"] != ""][
    ["Normalized_Client", "Normalized_Product", "Duration_Dec", "Email"]
].copy()
ck_clients.rename(columns={"Normalized_Client": "Client"}, inplace=True)

dv_clients = devops_all[devops_all["Normalized_Client"] != ""][
    ["Normalized_Client", "Normalized_Product"]
].copy()
dv_clients.rename(columns={"Normalized_Client": "Client"}, inplace=True)

all_client_names = set(ck_clients["Client"].unique()) | set(dv_clients["Client"].unique())

for client in sorted(all_client_names):
    ck_c = ck_clients[ck_clients["Client"] == client]
    dv_c = dv_clients[dv_clients["Client"] == client]

    products_used = set(ck_c["Normalized_Product"].dropna().unique()) | set(
        dv_c["Normalized_Product"].dropna().unique()
    )
    products_used = sorted([p for p in products_used if p and p != "Unknown"])

    total_hours = ck_c["Duration_Dec"].sum() if len(ck_c) > 0 else 0
    entry_count = len(ck_c)

    sources = []
    if len(ck_c) > 0:
        sources.append("Clockify")
    if len(dv_c) > 0:
        sources.append("DevOps")

    client_data.append({
        "Client": client,
        "Products_Used": "; ".join(products_used) if products_used else "N/A",
        "Total_Hours": round(total_hours, 2),
        "Entry_Count": entry_count,
        "Sources": "; ".join(sources),
    })

client_summary = pd.DataFrame(client_data)
print(f"  Clients tracked: {len(client_summary)}")

# ---------------------------------------------------------------------------
# 8. Data quality report
# ---------------------------------------------------------------------------
print("\n[8/8] Building data quality report...")

quality_rows = []

# Unmapped entries
unmapped = clockify[clockify["Normalized_Product"].isin(["Unknown", ""])]
quality_rows.append({
    "Category": "Unmapped Entries",
    "Count": len(unmapped),
    "Details": "Clockify entries with no product mapping",
    "Examples": "; ".join(unmapped["Project"].unique()[:5]),
})

# Low confidence
low_conf = clockify[clockify["Mapping_Confidence"] < 0.8]
quality_rows.append({
    "Category": "Low Confidence Mappings",
    "Count": len(low_conf),
    "Details": "Mapping confidence < 0.8",
    "Examples": "; ".join(low_conf["Mapping_Method"].unique()[:5]),
})

# Suspicious entries
suspicious = clockify[clockify["Is_Suspicious"]]
quality_rows.append({
    "Category": "Suspicious Entries",
    "Count": len(suspicious),
    "Details": "Flagged by suspicious entry detection",
    "Examples": "; ".join(suspicious["Suspicious_Reason"].unique()[:5]),
})

# Empty descriptions
empty_desc = clockify[clockify["Description"].apply(lambda d: safe_str(d) == "")]
quality_rows.append({
    "Category": "Empty Descriptions",
    "Count": len(empty_desc),
    "Details": "Entries with no description text",
    "Examples": "",
})

# Fotopia bucket breakdown
fotopia_entries = clockify[clockify["Project"] == "Fotopia"]
fotopia_breakdown = fotopia_entries.groupby("Normalized_Product").size()
for prod, count in fotopia_breakdown.items():
    quality_rows.append({
        "Category": "Fotopia Bucket",
        "Count": count,
        "Details": f"Auto-classified as '{prod}'",
        "Examples": "",
    })

quality_report = pd.DataFrame(quality_rows)
print(f"  Quality issues found: {len(quality_rows)}")

# ---------------------------------------------------------------------------
# 9. Mapping audit
# ---------------------------------------------------------------------------
mapping_audit_df = pd.DataFrame(mapping_audit)

# ---------------------------------------------------------------------------
# 10. Write outputs
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("WRITING OUTPUT FILES")
print("=" * 70)

# a) clockify_normalized.csv
clockify_out_cols = list(clockify.columns)
# Remove the helper column
clockify_out = clockify.drop(columns=["Duration_Dec"], errors="ignore")
clockify_out.to_csv(os.path.join(OUTPUT_DIR, "clockify_normalized.csv"), index=False)
print(f"  clockify_normalized.csv     ({len(clockify_out)} rows)")

# b) devops_normalized.csv
devops_out = devops_all.drop(columns=["ID_str"], errors="ignore")
devops_out.to_csv(os.path.join(OUTPUT_DIR, "devops_normalized.csv"), index=False, encoding="utf-8-sig")
print(f"  devops_normalized.csv       ({len(devops_out)} rows)")

# c) cross_system_links.csv
cross_links_out.to_csv(os.path.join(OUTPUT_DIR, "cross_system_links.csv"), index=False)
print(f"  cross_system_links.csv      ({len(cross_links_out)} rows)")

# d) person_master.csv
person_master.to_csv(os.path.join(OUTPUT_DIR, "person_master.csv"), index=False)
print(f"  person_master.csv           ({len(person_master)} rows)")

# e) product_summary.csv
product_summary.to_csv(os.path.join(OUTPUT_DIR, "product_summary.csv"), index=False)
print(f"  product_summary.csv         ({len(product_summary)} rows)")

# f) client_summary.csv
client_summary.to_csv(os.path.join(OUTPUT_DIR, "client_summary.csv"), index=False)
print(f"  client_summary.csv          ({len(client_summary)} rows)")

# g) data_quality_report.csv
quality_report.to_csv(os.path.join(OUTPUT_DIR, "data_quality_report.csv"), index=False)
print(f"  data_quality_report.csv     ({len(quality_report)} rows)")

# h) mapping_audit.csv
mapping_audit_df.to_csv(os.path.join(OUTPUT_DIR, "mapping_audit.csv"), index=False)
print(f"  mapping_audit.csv           ({len(mapping_audit_df)} rows)")

# ---------------------------------------------------------------------------
# Summary Report
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SUMMARY REPORT")
print("=" * 70)

total_ck_hours = clockify["Duration (decimal)"].apply(parse_duration_decimal).sum()
print(f"\n  Total Clockify entries:      {len(clockify)}")
print(f"  Total Clockify hours:        {total_ck_hours:.1f}")
print(f"  Total DevOps items:          {len(devops_all)}")
print(f"  Cross-system linked entries: {len(cross_links_out)}")
print(f"  Unique people:               {len(person_master)}")
print(f"  Products:                    {len(product_summary)}")
print(f"  Clients:                     {len(client_summary)}")

print(f"\n  --- Product Hours Breakdown ---")
prod_hours = clockify.groupby("Normalized_Product")["Duration_Dec"].sum().sort_values(ascending=False)
for prod, hours in prod_hours.items():
    if hours > 0:
        print(f"    {prod:<25} {hours:>8.1f} hrs")

print(f"\n  --- Suspicious Entry Summary ---")
print(f"    Total suspicious:          {sum(suspicious_flags)}")
sus_reasons = Counter()
for r in suspicious_reasons:
    if r:
        for part in r.split("; "):
            sus_reasons[part] += 1
for reason, count in sus_reasons.most_common():
    print(f"    {reason:<55} {count:>4}")

print(f"\n  --- Data Quality ---")
mapped_pct = sum(1 for p in products if p and p not in ("Unknown", "")) / len(products) * 100
print(f"    Product mapping rate:      {mapped_pct:.1f}%")
print(f"    Entries with version:      {sum(1 for v in versions if v)}/{len(versions)}")
print(f"    Entries with client:       {sum(1 for c in clients if c)}/{len(clients)}")
print(f"    Empty descriptions:        {len(empty_desc)}/{len(clockify)}")

fotopia_count = len(fotopia_entries)
print(f"\n  --- Fotopia Bucket ({fotopia_count} entries) ---")
for prod, count in fotopia_breakdown.items():
    print(f"    -> {prod:<25} {count:>4} entries")

print(f"\n  --- DevOps State Distribution ---")
state_dist = devops_all["Normalized_State"].value_counts()
for state, count in state_dist.items():
    print(f"    {state:<20} {count:>5}")

print("\n" + "=" * 70)
print("DONE. Output files written to:")
print(f"  {OUTPUT_DIR}")
print("=" * 70)
