# 📘 Complete Deployment Guide

## Quick Start Summary

You now have **TWO versions** of the application:

1. **streamlit_app.py** - For Streamlit Cloud (headless, no Chrome needed locally)
2. **streamlit_app_windows.py** - For Windows local deployment (uses webdriver-manager)

## 🚀 Option 1: Deploy on Streamlit Cloud (Recommended for Public Access)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)

### Step-by-Step Deployment

#### Step 1: Prepare Your Files
Ensure you have these files:
```
your-project-folder/
├── streamlit_app.py          # Main application
├── requirements.txt           # Python dependencies
├── packages.txt              # System dependencies (Chromium)
└── README.md                 # Documentation (optional)
```

#### Step 2: Create GitHub Repository
1. Go to GitHub.com and create a new repository
2. Name it (e.g., "karnataka-land-scraper")
3. Make it public or private (your choice)

#### Step 3: Upload Files to GitHub
```bash
# In your project folder, run:
git init
git add streamlit_app.py requirements.txt packages.txt README.md
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

#### Step 4: Deploy on Streamlit Cloud
1. Go to **share.streamlit.io**
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - Repository: Select your GitHub repo
   - Branch: main
   - Main file path: `streamlit_app.py`
5. Click **"Deploy!"**
6. Wait 5-10 minutes for initial deployment

#### Step 5: Use Your App
- Your app will be live at: `https://[your-app-name].streamlit.app`
- Share this URL with anyone who needs to use it
- Upload the input.csv file and start scraping!

### ⚠️ Streamlit Cloud Limitations
- Memory: 1 GB RAM (free tier)
- May timeout for very large datasets
- Network restrictions may apply

---

## 🖥️ Option 2: Run Locally on Windows

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser installed

### Installation Steps

#### Step 1: Install Python Packages
```bash
pip install streamlit pandas selenium webdriver-manager
```

#### Step 2: Run the Application
```bash
streamlit run streamlit_app_windows.py
```

#### Step 3: Access the App
- Browser will automatically open at `http://localhost:8501`
- Upload your input.csv file
- Toggle "Headless Mode" in sidebar:
  - ✅ Checked = Browser runs in background (faster)
  - ❌ Unchecked = See Chrome browser in action (for debugging)

### Benefits of Local Deployment
- No memory limitations
- Faster processing
- Full control over browser behavior
- Can see browser actions for debugging

---

## 📝 Input CSV Format

Create `input.csv` with these exact column names:

```csv
District,Taluk,Hobli,Village,HSSN
BENGALURU URBAN,BENGALURU NORTH,KASABA,BENGALURU,5
MYSURU,MYSURU NORTH,HOOTAGALLI,HOOTAGALLI,3
```

### Column Descriptions:
- **District**: Full district name in CAPS (as shown on website)
- **Taluk**: Full taluk name in CAPS
- **Hobli**: Full hobli name in CAPS
- **Village**: Full village name in CAPS
- **HSSN**: Highest Survey Serial Number (numeric, e.g., 5 means survey 1 to 5)

### Important Notes:
- Names must **exactly match** the dropdown values on the Karnataka website
- Use ALL CAPS for location names
- HSSN must be a positive integer
- CSV must be UTF-8 encoded

---

## 📤 Output Files

For each village in your input.csv, the app generates:

**Filename**: `{Village}.csv`

**Columns**:
| S.No. | Survey | Surnoc | Hissa |
|-------|--------|--------|-------|
| 1     | 1      | 0      | 0     |
| 2     | 1      | 0      | 1     |
| 3     | 2      | 1      | 0     |

- **S.No.**: Serial number (auto-generated)
- **Survey**: Survey number (from 1 to HSSN)
- **Surnoc**: Surnoc number (from website dropdown)
- **Hissa**: Hissa number (from website dropdown)

Files are saved in `output_csvs/` folder and available for download.

---

## 🔧 Troubleshooting

### Issue: "Chrome driver not found"
**Solution (Windows version):**
- Ensure Chrome browser is installed
- webdriver-manager will auto-download the driver
- First run may take 1-2 minutes

### Issue: "Timeout waiting for element"
**Solution:**
- Increase wait times in code (change `WebDriverWait(driver, 20)` to higher value)
- Check if website is accessible
- Verify internet connection

### Issue: "Cannot select dropdown value"
**Solution:**
- Verify exact spelling of District/Taluk/Hobli/Village in input.csv
- Check if values exist on the website
- Names are case-sensitive

### Issue: "No Surnoc or Hissa found"
**Solution:**
- Some survey numbers may not have data
- This is normal - warnings will be shown
- App continues to next survey number

### Issue: Streamlit Cloud deployment fails
**Solution:**
- Ensure `packages.txt` includes chromium and chromium-driver
- Check requirements.txt has correct package versions
- Review Streamlit Cloud logs for specific errors

### Issue: App runs slowly
**Solution:**
- Use headless mode for faster performance
- Reduce number of villages in input.csv
- Process in batches if dataset is large

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install --upgrade streamlit pandas selenium webdriver-manager
```

---

## 🎯 Best Practices

1. **Start Small**: Test with 1-2 villages first before processing large datasets
2. **Verify Names**: Double-check District/Taluk/Hobli/Village names on the website
3. **Monitor Progress**: Watch progress bars and status messages
4. **Save Frequently**: Download CSV files immediately after generation
5. **Batch Processing**: For 50+ villages, split into multiple input files
6. **Error Handling**: Review warnings for any skipped surveys
7. **Network Stability**: Use stable internet connection for cloud scraping

---

## ⚖️ Legal & Ethical Considerations

- This tool is for **educational purposes**
- Ensure compliance with Karnataka Government website terms of service
- Do not overwhelm the server with excessive requests
- Respect rate limits and add delays if needed
- Use data responsibly and ethically
- Verify scraped data accuracy before using officially

---

## 🆘 Need Help?

### Common Questions

**Q: Can I use this on Mac/Linux?**
A: Yes, but you'll need to adjust Chrome driver setup. Streamlit Cloud works on all OS.

**Q: How many villages can I process at once?**
A: Local: No limit (depends on your PC). Cloud: 20-30 recommended due to memory limits.

**Q: Does this work with other state land records?**
A: No, this is specifically designed for Karnataka's website structure.

**Q: Can I modify the fields collected?**
A: Yes, you can modify the code to extract additional information from the website.

**Q: Is there a faster way?**
A: You can reduce sleep/wait times in the code, but may cause failures.

---

## 📦 File Structure Summary

```
your-project/
├── streamlit_app.py              # Cloud version (use this for Streamlit Cloud)
├── streamlit_app_windows.py      # Windows version (use this locally)
├── requirements.txt              # Python packages
├── packages.txt                  # System packages (for cloud)
├── README.md                     # Documentation
├── input.csv                     # Your input file (create this)
└── output_csvs/                  # Generated output files (auto-created)
    ├── BENGALURU.csv
    ├── HOOTAGALLI.csv
    └── ...
```

---

## 🎉 Success Checklist

Before scraping, verify:
- ✅ Python and Chrome installed (local) or GitHub repo created (cloud)
- ✅ All dependencies installed
- ✅ input.csv created with correct format
- ✅ Location names verified on Karnataka website
- ✅ Stable internet connection
- ✅ Sufficient time allocated for processing

After successful scraping:
- ✅ Download all generated CSV files
- ✅ Verify data accuracy
- ✅ Backup files to safe location

---

**Created by:** Your Custom Development
**Version:** 1.0
**Last Updated:** October 2025
