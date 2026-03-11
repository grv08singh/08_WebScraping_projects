
# Create requirements.txt for Streamlit Cloud deployment

requirements_txt = '''streamlit==1.32.0
pandas==2.2.0
selenium==4.18.1
webdriver-manager==4.0.1
'''

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_txt)

print("✅ Created: requirements.txt")

# Create packages.txt for system dependencies (Streamlit Cloud specific)

packages_txt = '''chromium
chromium-driver
'''

with open('packages.txt', 'w', encoding='utf-8') as f:
    f.write(packages_txt)

print("✅ Created: packages.txt")

# Create README with deployment instructions

readme_md = '''# Karnataka Land Records Scraper

A Streamlit application to scrape land records data from Karnataka Government Portal.

## Features
- Upload CSV file with District, Taluk, Hobli, Village, and HSSN information
- Automated web scraping using Selenium
- Headless browser for cloud deployment
- Download results as CSV files for each village

## Local Setup

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run streamlit_app.py
```

## Streamlit Cloud Deployment

### Files Required
- `streamlit_app.py` - Main application code
- `requirements.txt` - Python dependencies
- `packages.txt` - System dependencies (Chromium)

### Deployment Steps

1. **Push to GitHub:**
   - Create a new GitHub repository
   - Push all files (streamlit_app.py, requirements.txt, packages.txt)

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select the repository and branch
   - Set Main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Important Notes for Cloud Deployment:**
   - The `packages.txt` file installs Chromium browser on the cloud server
   - The application uses headless Chrome mode automatically
   - First deployment may take 5-10 minutes to install all dependencies

## Input CSV Format

Your `input.csv` should have these columns:

| District | Taluk | Hobli | Village | HSSN |
|----------|-------|-------|---------|------|
| BENGALURU URBAN | BENGALURU NORTH | KASABA | BENGALURU | 5 |

- **District**: District name (e.g., "BENGALURU URBAN")
- **Taluk**: Taluk name (e.g., "BENGALURU NORTH")
- **Hobli**: Hobli name (e.g., "KASABA")
- **Village**: Village name (e.g., "BENGALURU")
- **HSSN**: Highest Survey Serial Number (numeric value)

## Output

For each village, the application generates a CSV file with:
- **S.No.**: Serial number
- **Survey**: Survey number
- **Surnoc**: Surnoc number
- **Hissa**: Hissa number

## Troubleshooting

### Local Issues
- **Chrome driver error**: Install Chrome browser or update Selenium
- **Timeout errors**: Increase wait times in the code
- **Connection issues**: Check internet connectivity

### Streamlit Cloud Issues
- **Deployment fails**: Ensure packages.txt includes chromium dependencies
- **Scraping errors**: The website may have rate limiting or anti-bot measures
- **Memory errors**: Reduce the number of rows processed at once

## Alternative: Modified Code for Windows with Chrome Driver

If deploying on Streamlit Cloud doesn't work or you want to run locally on Windows with visible browser:

Replace the `setup_driver()` function with:

```python
def setup_driver():
    """Setup Chrome driver for local Windows deployment"""
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    # Remove headless for visible browser
    # chrome_options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
```

## Limitations

- The Karnataka Land Records website may have CAPTCHA or anti-scraping measures
- Large datasets may take considerable time to process
- Network connectivity issues may cause failures
- The website structure may change, requiring code updates

## Legal Notice

This tool is for educational purposes. Ensure compliance with:
- Website terms of service
- Data scraping regulations
- Applicable laws and regulations

Use responsibly and respect website rate limits.
'''

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_md)

print("✅ Created: README.md")
