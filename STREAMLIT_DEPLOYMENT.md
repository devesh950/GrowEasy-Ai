# GrowEasy Streamlit CSV Importer

Streamlit version of the GrowEasy CSV importer with integrated field mapping logic.

## Features

✅ **White Light Theme** - Clean, modern interface  
✅ **CSV Upload** - Drag & drop or file picker  
✅ **Live Preview** - See your data before importing  
✅ **Smart Field Mapping** - Automatic CRM field detection  
✅ **15 CRM Fields** - Full structured output  
✅ **Download Results** - Export mapped data as CSV  
✅ **Session State** - Wizard-style workflow  

## Quick Start (Local)

### 1. Install Dependencies
```bash
pip install -r requirements-streamlit.txt
```

### 2. Run Streamlit App
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## Usage Flow

1. **Step 1 - Upload** → Select your CSV file
2. **Step 2 - Preview** → Review 5 rows before processing
3. **Step 3 - Results** → See 15 mapped CRM fields + download CSV

## CRM Fields Mapped

```
created_at, name, email, country_code, 
mobile_without_country_code, company, city, 
state, country, lead_owner, crm_status, 
crm_note, data_source, possession_time, description
```

## Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
# Initialize git repo if needed
git init
git add streamlit_app.py requirements-streamlit.txt
git commit -m "Add Streamlit CSV importer"
git push origin main
```

### Step 2: Deploy on Share.Streamlit.io

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `your-repo`
5. Branch: `main`
6. File path: `streamlit_app.py`
7. Click "Deploy"

**That's it!** Your app will be live at:
```
https://[your-username]-[app-name].streamlit.app
```

## Configuration Files

### .streamlit/config.toml (Optional)

Create `.streamlit/config.toml` for custom settings:

```toml
[client]
showErrorDetails = false

[logger]
level = "info"

[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f9fafb"
textColor = "#0f172a"
font = "sans serif"
```

### Deployment with Environment

For cloud deployment, add `.streamlit/secrets.toml` (not versioned):

```toml
# Add any API keys or secrets here
# API_KEY = "your-key"
```

Access in code:
```python
api_key = st.secrets["API_KEY"]
```

## CSV Format Requirements

Your CSV should have columns that match common field names:

| CRM Field | Accepted Column Names |
|-----------|---------------------|
| name | name, full_name, customer_name |
| email | email, contact_email, email_address |
| phone | phone, phone_number, mobile |
| company | company, company_name, organization |
| city | city, city_name, location |
| country | country, country_name |
| status | status, lead_status, crm_status |
| notes | note, notes, remarks, comment |

*The app auto-detects columns and maps them intelligently.*

## Troubleshooting

### Port Already in Use
```bash
streamlit run streamlit_app.py --logger.level=debug --server.port 8502
```

### Clear Cache
```bash
streamlit cache clear
```

### Deployment Issues
- Check GitHub repo is public (for Streamlit Cloud)
- Verify `requirements-streamlit.txt` has all dependencies
- Check `.streamlit/config.toml` syntax (if using)

## Performance Notes

- **File Size**: Tested with up to 10,000 rows
- **Processing**: Real-time field mapping
- **Session State**: Remembers your progress within session
- **Memory**: ~50MB for typical 1,000-row CSV

## Next Steps

- Add database integration (SQLite, PostgreSQL)
- Add email notifications on import
- Implement batch processing for large files
- Add data validation rules
- Create admin dashboard

## Support

For issues, check:
- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- Your app logs in Streamlit Cloud dashboard

---

**Deployed Version:** Replace with your Streamlit Cloud URL after deployment  
**Local Version:** `http://localhost:8501`
