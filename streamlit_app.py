import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="GrowEasy CSV Importer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for white theme
st.markdown("""
<style>
    :root {
        --bg: #ffffff;
        --text: #0f172a;
        --panel: rgba(255, 255, 255, 0.96);
        --border: rgba(15, 23, 42, 0.08);
        --accent: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
    }
    
    * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    .stMarkdown, .stText {
        color: #0f172a !important;
    }
    
    .stButton > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #2563eb !important;
    }
    
    .stDataFrame {
        background-color: #ffffff !important;
    }
    
    .stDataFrame table {
        background-color: #ffffff !important;
    }
    
    .stDataFrame table tr th {
        background-color: #f3f4f6 !important;
        color: #0f172a !important;
        font-weight: 600;
        border-bottom: 2px solid rgba(15, 23, 42, 0.1) !important;
    }
    
    .stDataFrame table tr td {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-bottom: 1px solid rgba(15, 23, 42, 0.08) !important;
    }
    
    .stDataFrame table tr:hover td {
        background-color: #f9fafb !important;
    }
    
    .metric-card {
        background-color: #f9fafb;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    .status-success {
        color: #10b981;
        font-weight: 600;
    }
    
    .status-pending {
        color: #f59e0b;
        font-weight: 600;
    }
    
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 24px;
        margin-bottom: 12px;
        border-bottom: 2px solid rgba(15, 23, 42, 0.08);
        padding-bottom: 12px;
    }
    
    .step-badge {
        display: inline-block;
        background-color: #3b82f6;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# CRM field mapping configuration
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

# Input field mappings (common CSV column names)
FIELD_MAPPINGS = {
    "created_at": ["date", "created", "created_at", "timestamp", "date_created"],
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
    "data_source": ["source", "data_source", "origin", "channel"],
    "possession_time": ["possession_time", "follow_up", "next_action"],
    "description": ["description", "desc", "details", "extra_notes"]
}


def map_csv_to_crm(csv_data):
    """Map CSV columns to CRM fields"""
    csv_columns = set(col.lower().strip() for col in csv_data.columns)
    crm_records = []
    
    for idx, row in csv_data.iterrows():
        crm_record = {}
        
        for crm_field, possible_names in FIELD_MAPPINGS.items():
            found = False
            for possible_name in possible_names:
                if possible_name.lower() in csv_columns:
                    csv_col = [col for col in csv_data.columns if col.lower().strip() == possible_name.lower()][0]
                    value = row[csv_col]
                    crm_record[crm_field] = str(value) if pd.notna(value) else ""
                    found = True
                    break
            
            if not found:
                crm_record[crm_field] = ""
        
        crm_records.append(crm_record)
    
    return crm_records


# Header
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="font-size: 32px; font-weight: 700; color: #0f172a; margin: 0;">📊 GrowEasy CSV Importer</h1>
    <p style="font-size: 16px; color: #6b7280; margin: 8px 0;">Import messy CSVs with AI-grade field mapping</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "preview_data" not in st.session_state:
    st.session_state.preview_data = None
if "parsed_results" not in st.session_state:
    st.session_state.parsed_results = None

# Step 1: Upload CSV
st.markdown('<div class="section-title"><span class="step-badge">Step 1</span>Upload CSV</div>', unsafe_allow_html=True)
st.markdown("Drop in exports from ads, sheets, CRMs, or hand-built spreadsheets. Preview rows instantly.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        label_visibility="collapsed",
        key="csv_uploader"
    )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.step = 2

if st.session_state.uploaded_file:
    with col2:
        st.success(f"✓ {st.session_state.uploaded_file.name}")

# Step 2: Preview
if st.session_state.step >= 2 and st.session_state.uploaded_file:
    st.divider()
    st.markdown('<div class="section-title"><span class="step-badge">Step 2</span>Preview</div>', unsafe_allow_html=True)
    st.markdown("5 rows shown locally before AI processing")
    
    try:
        df = pd.read_csv(st.session_state.uploaded_file)
        st.session_state.preview_data = df
        
        st.info(f"📋 Found {len(df)} rows and {len(df.columns)} columns")
        
        # Show preview table
        st.markdown("**Preview (first 5 rows):**")
        st.dataframe(df.head(5), use_container_width=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✓ Confirm Import", key="confirm_btn", use_container_width=True):
                st.session_state.step = 3
        
        with col2:
            st.markdown("*Tip: The backend will process this CSV and map fields to CRM format*")
    
    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")

# Step 3: Process & Results
if st.session_state.step >= 3 and st.session_state.preview_data is not None:
    st.divider()
    st.markdown('<div class="section-title"><span class="step-badge">Step 3</span>Parsed Results</div>', unsafe_allow_html=True)
    st.markdown("Structured output mapped to CRM fields")
    
    with st.spinner("🔄 Processing CSV and mapping to CRM fields..."):
        # Map CSV to CRM format
        crm_records = map_csv_to_crm(st.session_state.preview_data)
        st.session_state.parsed_results = crm_records
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">Total Imported</div>
            <div style="font-size: 28px; font-weight: 700; color: #10b981;">{len(crm_records)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">CRM Fields Mapped</div>
            <div style="font-size: 28px; font-weight: 700; color: #3b82f6;">{len(CRM_COLUMNS)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">Processing Status</div>
            <div style="font-size: 28px; font-weight: 700; color: #10b981;">✓ Complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Display results table
    st.markdown("**Parsed Records (scroll right to see more columns):**")
    
    # Convert to DataFrame for display
    results_df = pd.DataFrame(crm_records)
    st.dataframe(results_df, use_container_width=True, height=400)
    
    # Download results as CSV
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.download_button(
            label="📥 Download Results",
            data=csv_data,
            file_name=f"crm_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("↻ Import Another", use_container_width=True):
            st.session_state.step = 1
            st.session_state.uploaded_file = None
            st.session_state.preview_data = None
            st.session_state.parsed_results = None
            st.rerun()

st.divider()

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #9ca3af; font-size: 12px;">
    <p>GrowEasy CSV Importer • Built with Streamlit • <a href="#" style="color: #3b82f6; text-decoration: none;">Documentation</a></p>
</div>
""", unsafe_allow_html=True)
