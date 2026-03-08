
# First, let me create the main Streamlit application code

streamlit_app_code = '''
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os

st.set_page_config(page_title="Karnataka Land Records Scraper", layout="wide")

st.title("🗺️ Karnataka Land Records Data Scraper")
st.markdown("Upload your **input.csv** file to scrape land records data from Karnataka Government Portal")

def setup_driver():
    """Setup headless Chrome driver for cloud deployment"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_land_records(district, taluk, hobli, village, hssn, progress_bar, status_text):
    """Scrape land records for a given village"""
    
    # Initialize DataFrame
    df = pd.DataFrame(columns=["S.No.", "Survey", "Surnoc", "Hissa"])
    
    # Setup driver
    driver = None
    try:
        status_text.text(f"Setting up browser for {village}...")
        driver = setup_driver()
        
        # Open the website
        status_text.text(f"Opening Karnataka Land Records website...")
        driver.get("https://landrecords.karnataka.gov.in/service2/RTC.aspx")
        time.sleep(2)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 20)
        
        # Select District
        status_text.text(f"Selecting District: {district}...")
        district_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCDistrict"))
        )
        Select(district_dropdown).select_by_visible_text(district)
        district_dropdown.send_keys(Keys.TAB)
        time.sleep(2)
        
        # Select Taluk
        status_text.text(f"Selecting Taluk: {taluk}...")
        taluk_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCTaluk"))
        )
        Select(taluk_dropdown).select_by_visible_text(taluk)
        taluk_dropdown.send_keys(Keys.TAB)
        time.sleep(2)
        
        # Select Hobli
        status_text.text(f"Selecting Hobli: {hobli}...")
        hobli_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCHobli"))
        )
        Select(hobli_dropdown).select_by_visible_text(hobli)
        hobli_dropdown.send_keys(Keys.TAB)
        time.sleep(2)
        
        # Select Village
        status_text.text(f"Selecting Village: {village}...")
        village_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCVillage"))
        )
        Select(village_dropdown).select_by_visible_text(village)
        village_dropdown.send_keys(Keys.TAB)
        time.sleep(2)
        
        # Loop through survey numbers
        data_rows = []
        total_surveys = int(hssn)
        
        for survey in range(1, total_surveys + 1):
            progress = survey / total_surveys
            progress_bar.progress(progress)
            status_text.text(f"Processing Survey {survey} of {total_surveys} for {village}...")
            
            try:
                # Enter survey number
                survey_field = wait.until(
                    EC.presence_of_element_located((By.ID, "ctl00_MainContent_txtCSurveyNo"))
                )
                survey_field.clear()
                survey_field.send_keys(str(survey))
                survey_field.send_keys(Keys.TAB)
                time.sleep(1)
                
                # Click Go button
                go_button = driver.find_element(By.ID, "ctl00_MainContent_btnCGo")
                go_button.click()
                time.sleep(2)
                
                # Get Surnoc dropdown values
                try:
                    surnoc_dropdown = wait.until(
                        EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCSurnocNo"))
                    )
                    surnoc_select = Select(surnoc_dropdown)
                    surnoc_options = [option.text for option in surnoc_select.options if option.text.strip()]
                    
                    # Loop through each surnoc value
                    for surnoc in surnoc_options:
                        if not surnoc.strip() or surnoc.strip() == "Select":
                            continue
                            
                        # Select surnoc
                        Select(surnoc_dropdown).select_by_visible_text(surnoc)
                        surnoc_dropdown.send_keys(Keys.TAB)
                        time.sleep(1)
                        
                        # Get Hissa dropdown values
                        try:
                            hissa_dropdown = wait.until(
                                EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCHissaNo"))
                            )
                            hissa_select = Select(hissa_dropdown)
                            hissa_options = [option.text for option in hissa_select.options if option.text.strip()]
                            
                            # Save each hissa value
                            for hissa in hissa_options:
                                if not hissa.strip() or hissa.strip() == "Select":
                                    continue
                                    
                                data_rows.append({
                                    "Survey": survey,
                                    "Surnoc": surnoc.strip(),
                                    "Hissa": hissa.strip()
                                })
                        
                        except Exception as e:
                            st.warning(f"No Hissa found for Survey {survey}, Surnoc {surnoc}")
                            continue
                
                except Exception as e:
                    st.warning(f"No Surnoc found for Survey {survey}")
                    continue
                    
            except Exception as e:
                st.warning(f"Error processing Survey {survey}: {str(e)}")
                continue
        
        # Create DataFrame from collected data
        if data_rows:
            df = pd.DataFrame(data_rows)
            df.insert(0, "S.No.", range(1, len(df) + 1))
        
        status_text.text(f"✅ Completed scraping for {village}!")
        
    except Exception as e:
        st.error(f"Error scraping {village}: {str(e)}")
        
    finally:
        if driver:
            driver.quit()
    
    return df

# File uploader
uploaded_file = st.file_uploader("Upload input.csv", type=['csv'])

if uploaded_file is not None:
    try:
        # Read input CSV
        input_df = pd.read_csv(uploaded_file)
        
        # Validate columns
        required_columns = ["District", "Taluk", "Hobli", "Village", "HSSN"]
        if not all(col in input_df.columns for col in required_columns):
            st.error(f"❌ Input CSV must contain columns: {', '.join(required_columns)}")
        else:
            st.success(f"✅ Loaded {len(input_df)} villages from input file")
            st.dataframe(input_df)
            
            # Start scraping button
            if st.button("🚀 Start Scraping", type="primary"):
                
                st.markdown("---")
                st.subheader("Scraping Progress")
                
                # Create output directory
                output_dir = "output_csvs"
                os.makedirs(output_dir, exist_ok=True)
                
                all_files = []
                
                # Process each row
                for idx, row in input_df.iterrows():
                    st.markdown(f"### Processing Village {idx + 1} of {len(input_df)}: {row['Village']}")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Scrape data
                    result_df = scrape_land_records(
                        district=row['District'],
                        taluk=row['Taluk'],
                        hobli=row['Hobli'],
                        village=row['Village'],
                        hssn=row['HSSN'],
                        progress_bar=progress_bar,
                        status_text=status_text
                    )
                    
                    # Save to CSV
                    if not result_df.empty:
                        filename = f"{row['Village']}.csv"
                        filepath = os.path.join(output_dir, filename)
                        result_df.to_csv(filepath, index=False)
                        all_files.append(filepath)
                        
                        # Show download button
                        with open(filepath, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download {filename}",
                                data=f,
                                file_name=filename,
                                mime='text/csv',
                                key=f"download_{idx}"
                            )
                        
                        st.success(f"✅ Saved {len(result_df)} records for {row['Village']}")
                        st.dataframe(result_df.head(10))
                    else:
                        st.warning(f"⚠️ No data found for {row['Village']}")
                    
                    st.markdown("---")
                
                st.balloons()
                st.success(f"🎉 Completed scraping all {len(input_df)} villages!")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

else:
    st.info("👆 Please upload your input.csv file to begin")
    
    # Show sample format
    st.markdown("### 📋 Sample Input Format")
    sample_df = pd.DataFrame({
        "District": ["BENGALURU URBAN"],
        "Taluk": ["BENGALURU NORTH"],
        "Hobli": ["KASABA"],
        "Village": ["BENGALURU"],
        "HSSN": [5]
    })
    st.dataframe(sample_df)

# Footer
st.markdown("---")
st.markdown("**Note:** This application uses Selenium for web scraping. Ensure proper configuration on Streamlit Cloud.")
'''

# Save to file
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(streamlit_app_code)

print("✅ Created: streamlit_app.py")
