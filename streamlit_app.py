import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="GrowEasy CSV Importer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern glassmorphism UI matching Next.js styling
st.markdown("""
<style>
    /* Main body background with soft gradients */
    .stApp {
        background: 
            radial-gradient(circle at top left, rgba(15, 23, 42, 0.04), transparent 28%),
            radial-gradient(circle at top right, rgba(15, 23, 42, 0.02), transparent 24%),
            linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header layout */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 24px;
        color: #ffffff !important;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .header-title {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff !important;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        font-size: 16px;
        color: #94a3b8 !important;
        margin: 10px 0 0;
    }

    /* Workflow progression pills */
    .workflow-container {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-bottom: 25px;
    }

    .workflow-pill {
        padding: 6px 16px;
        background: rgba(15, 23, 42, 0.03);
        border: 1px solid rgba(15, 23, 42, 0.06);
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569 !important;
        letter-spacing: 0.05em;
    }

    .workflow-pill.active {
        background: #0f172a;
        color: #ffffff !important;
        border-color: #0f172a;
    }

    /* Section container styling */
    .card-panel {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.04);
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .step-badge {
        background-color: #0f172a;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .section-desc {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 20px;
    }
    
    /* Metrics grid styling */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }
    
    .metric-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
    }
    
    /* Status Pills */
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid;
    }
    
    .status-active {
        color: #166534;
        background-color: rgba(22, 101, 52, 0.06);
        border-color: rgba(22, 101, 52, 0.18);
    }

    .status-pending {
        color: #9a6700;
        background-color: rgba(154, 103, 0, 0.06);
        border-color: rgba(154, 103, 0, 0.18);
    }

    .status-danger {
        color: #b91c1c;
        background-color: rgba(185, 28, 28, 0.06);
        border-color: rgba(185, 28, 28, 0.18);
    }

    /* Table custom styling */
    .stDataFrame {
        border-radius: 12px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        overflow: hidden;
    }
    
    /* Buttons custom style */
    .stButton>button {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important;
        color: #ffffff !important;
        border-radius: 999px !important;
        border: 1px solid rgba(15, 23, 42, 0.1) !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.1) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.15) !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px 0;
        color: #94a3b8;
        font-size: 13px;
        border-top: 1px solid rgba(15, 23, 42, 0.08);
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# CRM fields specification
CRM_COLUMNS = [
    "created_at",
    "name",
    "email",
    "country_code",
    "mobile_without_country_code",
    "company",
    "city",
    "state",
    "country",
    "lead_owner",
    "crm_status",
    "crm_note",
    "data_source",
    "possession_time",
    "description"
]

# Field matches
FIELD_MAPPINGS = {
    "created_at": ["date", "created", "created_at", "timestamp", "date_created", "appointment_time", "time"],
    "name": ["name", "full_name", "customer_name", "contact_name"],
    "email": ["email", "contact_email", "email_address"],
    "country_code": ["country_code", "country_prefix", "phone_prefix"],
    "mobile_without_country_code": ["phone", "phone_number", "mobile", "mobile_number"],
    "company": ["company", "company_name", "organization", "org"],
    "city": ["city", "city_name", "location"],
    "state": ["state", "state_name", "province"],
    "country": ["country", "country_name"],
    "lead_owner": ["lead_owner", "owner", "assigned_to", "representative"],
    "crm_status": ["status", "lead_status", "crm_status", "stage"],
    "crm_note": ["note", "notes", "crm_note", "remarks", "comment"],
    "data_source": ["source", "data_source", "data source", "origin", "channel"],
    "possession_time": ["possession_time", "possession", "possession time", "follow_up", "next_action", "follow up"],
    "description": ["description", "desc", "details", "extra_notes"]
}

ALLOWED_STATUSES = ['GOOD_LEAD_FOLLOW_UP', 'DID_NOT_CONNECT', 'BAD_LEAD', 'SALE_DONE']
ALLOWED_SOURCES = ['leads_on_demand', 'meridian_tower', 'eden_park', 'varah_swamy', 'sarjapur_plots']

STATUS_HINTS = [
    (re.compile(r'sale|closed|won|deal', re.I), 'SALE_DONE'),
    (re.compile(r'follow|interested|warm|good', re.I), 'GOOD_LEAD_FOLLOW_UP'),
    (re.compile(r'not connect|busy|call back|callback|no answer|unreachable', re.I), 'DID_NOT_CONNECT'),
    (re.compile(r'not interested|spam|invalid|bad lead|wrong number', re.I), 'BAD_LEAD')
]

SOURCE_HINTS = [
    (re.compile(r'leads? on demand', re.I), 'leads_on_demand'),
    (re.compile(r'meridian tower', re.I), 'meridian_tower'),
    (re.compile(r'eden park', re.I), 'eden_park'),
    (re.compile(r'varah swamy', re.I), 'varah_swamy'),
    (re.compile(r'sarjapur plots', re.I), 'sarjapur_plots')
]

def split_phone(phone_str):
    phone = re.sub(r'[^\d+]', '', phone_str)
    if not phone.startswith('+'):
        return '', phone
    
    # Simple country code extraction
    digits = re.sub(r'\D', '', phone)
    country_code = digits[:min(3, max(1, len(digits) - 10))]
    return f"+{country_code}" if country_code else '', digits[len(country_code):]

def map_status(text):
    for pattern, val in STATUS_HINTS:
        if pattern.search(text):
            return val
    return ''

def map_source(text):
    for pattern, val in SOURCE_HINTS:
        if pattern.search(text):
            return val
    return ''

def map_csv_to_crm(csv_data):
    """Maps CSV rows into CRM format and handles skipped rows (missing both email and phone)"""
    csv_columns = [col.lower().strip() for col in csv_data.columns]
    valid_records = []
    skipped_records = []
    
    for idx, row in csv_data.iterrows():
        # Replicate backend validation: check if row has email and/or mobile number anywhere
        row_values = [str(val).strip() for val in row.values if pd.notna(val)]
        row_text = " ".join(row_values)
        
        has_email = "@" in row_text
        has_phone = bool(re.search(r'\d{7,}', row_text))
        
        if not has_email and not has_phone:
            skipped_records.append({
                "Row Number": idx + 2,
                "Reason": "Missing both email and mobile number",
                "Original Row Data": str(dict(row))
            })
            continue
            
        crm_record = {}
        # Find values for each mapped field
        for crm_field, possible_names in FIELD_MAPPINGS.items():
            value = ""
            for possible_name in possible_names:
                if possible_name in csv_columns:
                    col_index = csv_columns.index(possible_name)
                    original_col = csv_data.columns[col_index]
                    val = row[original_col]
                    if pd.notna(val):
                        value = str(val).strip()
                    break
            crm_record[crm_field] = value
            
        # Clean & Normalize CRM Values
        crm_record["email"] = crm_record["email"].replace(" ", "")
        
        # Phone split normalization
        phone_val = crm_record["mobile_without_country_code"]
        if phone_val:
            cc, mob = split_phone(phone_val)
            crm_record["country_code"] = cc if not crm_record["country_code"] else crm_record["country_code"]
            crm_record["mobile_without_country_code"] = mob
            
        # Status normalization
        st_val = crm_record["crm_status"]
        if st_val not in ALLOWED_STATUSES:
            crm_record["crm_status"] = map_status(row_text)
            
        # Data source normalization
        src_val = crm_record["data_source"]
        if src_val not in ALLOWED_SOURCES:
            crm_record["data_source"] = map_source(row_text)
            
        # Created at normalization
        date_val = crm_record["created_at"]
        try:
            if date_val:
                # Reformat to ISO
                parsed_dt = pd.to_datetime(date_val)
                crm_record["created_at"] = parsed_dt.isoformat()
            else:
                crm_record["created_at"] = datetime.now().isoformat()
        except:
            crm_record["created_at"] = datetime.now().isoformat()
            
        valid_records.append(crm_record)
        
    return valid_records, skipped_records

# --- Streamlit Layout ---

# Header Section
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 GrowEasy CSV Importer</h1>
    <p class="header-subtitle">Intelligently map and normalize CRM leads from messy spreadsheets using GrowEasy AI schemas.</p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if "step" not in st.session_state:
    st.session_state.step = 1
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "df" not in st.session_state:
    st.session_state.df = None
if "valid_records" not in st.session_state:
    st.session_state.valid_records = None
if "skipped_records" not in st.session_state:
    st.session_state.skipped_records = None

# Workflow Pills Display
step = st.session_state.step
st.markdown(f"""
<div class="workflow-container">
    <span class="workflow-pill {"active" if step == 1 else ""}">1. Upload</span>
    <span class="workflow-pill {"active" if step == 2 else ""}">2. Preview</span>
    <span class="workflow-pill {"active" if step == 3 else ""}">3. Results</span>
</div>
""", unsafe_allow_html=True)

# STEP 1: Upload CSV
if st.session_state.step == 1:
    st.markdown("""
    <div class="card-panel">
        <div class="section-title"><span class="step-badge">Step 1</span> Upload CSV File</div>
        <p class="section-desc">Drop in exports from ads, CRM dumps, or custom spreadsheets. Your data stays secure and is parsed locally first.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        label_visibility="collapsed",
        key="csv_uploader"
    )
    
    if uploaded_file:
        try:
            # Fix float conversion issue by reading everything as strings (dtype=str)
            df = pd.read_csv(uploaded_file, dtype=str)
            st.session_state.uploaded_file = uploaded_file
            st.session_state.df = df
            st.session_state.step = 2
            st.rerun()
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")

# STEP 2: Preview
elif st.session_state.step == 2:
    st.markdown("""
    <div class="card-panel">
        <div class="section-title"><span class="step-badge">Step 2</span> Local Preview</div>
        <p class="section-desc">Review your raw data headers and row samples before importing. No AI processing is executed yet.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File details badge
    col_details, col_confirm = st.columns([3, 1])
    with col_details:
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 15px; align-items: center;">
            <span class="status-badge status-active">✓ File: {st.session_state.uploaded_file.name}</span>
            <span class="status-badge status-pending">📋 {len(st.session_state.df)} Rows found</span>
            <span class="status-badge status-pending">🗂️ {len(st.session_state.df.columns)} Columns</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_confirm:
        if st.button("Confirm Import", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
            
    st.markdown("##### Raw Data Preview (First 8 Rows):")
    st.dataframe(st.session_state.df.head(8), use_container_width=True)
    
    if st.button("← Upload Different File"):
        st.session_state.step = 1
        st.session_state.uploaded_file = None
        st.session_state.df = None
        st.rerun()

# STEP 3: Results
elif st.session_state.step == 3:
    if st.session_state.valid_records is None:
        with st.spinner("Processing records and mapping to CRM fields..."):
            valid, skipped = map_csv_to_crm(st.session_state.df)
            st.session_state.valid_records = valid
            st.session_state.skipped_records = skipped
            
    valid_len = len(st.session_state.valid_records)
    skipped_len = len(st.session_state.skipped_records)
    total_len = len(st.session_state.df)
    
    st.markdown("""
    <div class="card-panel">
        <div class="section-title"><span class="step-badge">Step 3</span> Parsed Results</div>
        <p class="section-desc">View successfully normalized CRM records and rows that failed validation checks.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Beautiful metrics cards
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total CSV Rows</div>
            <div class="metric-value" style="color: #475569;">{total_len}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Successfully Imported</div>
            <div class="metric-value" style="color: #166534;">{valid_len}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Skipped Rows</div>
            <div class="metric-value" style="color: #b91c1c;">{skipped_len}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">CRM Schema Fields</div>
            <div class="metric-value" style="color: #2563eb;">{len(CRM_COLUMNS)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display Options / Actions
    col_actions, col_download = st.columns([3, 1])
    with col_actions:
        if st.button("Import Another File"):
            st.session_state.step = 1
            st.session_state.uploaded_file = None
            st.session_state.df = None
            st.session_state.valid_records = None
            st.session_state.skipped_records = None
            st.rerun()
            
    with col_download:
        valid_df = pd.DataFrame(st.session_state.valid_records)
        csv_buffer = io.StringIO()
        valid_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Mapped CSV",
            data=csv_data,
            file_name=f"crm_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    # Table of valid records
    st.markdown("##### 🟢 Successfully Mapped CRM Records:")
    if valid_len > 0:
        st.dataframe(valid_df[CRM_COLUMNS], use_container_width=True)
    else:
        st.warning("No records were successfully mapped.")
        
    # Table of skipped records
    if skipped_len > 0:
        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("##### 🔴 Skipped Rows (No Contact Info):")
        st.markdown("These rows were excluded because they lacked both a valid email address and a mobile number.")
        skipped_df = pd.DataFrame(st.session_state.skipped_records)
        st.dataframe(skipped_df, use_container_width=True)

# Footer
st.markdown("""
<div class="footer">
    GrowEasy CSV Importer • Built with Streamlit • Designed with Premium Aesthetics
</div>
""", unsafe_allow_html=True)
