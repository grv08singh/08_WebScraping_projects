import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import sys
import os

def setup_chrome_driver():
    """Setup Chrome driver with comprehensive options for Streamlit Cloud"""
    chrome_options = Options()
    
    # Essential options for Streamlit Cloud deployment
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Additional timeout and performance options
    chrome_options.add_argument("--max_old_space_size=4096")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    
    # Set page load strategy to eager (don't wait for all resources)
    chrome_options.add_argument("--page-load-strategy=eager")
    
    # User agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Create Chrome service with timeout settings
        service = Service()
        service.start_error_message = "Failed to start chrome service"
        
        # Create driver with extended timeouts
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts - increased for cloud environment
        driver.set_page_load_timeout(60)  # 60 seconds for page load
        driver.implicitly_wait(10)  # 10 seconds for element finding
        
        # Additional driver settings
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        return driver
        
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {str(e)}")
        return None

def safe_element_interaction(driver, wait, by, value, action="click", text=None, max_retries=3):
    """Safely interact with elements with retries and timeout handling"""
    for attempt in range(max_retries):
        try:
            element = wait.until(EC.element_to_be_clickable((by, value)))
            
            if action == "click":
                element.click()
            elif action == "send_keys":
                element.clear()
                element.send_keys(text)
                element.send_keys(Keys.TAB)
            elif action == "select":
                select = Select(element)
                select.select_by_visible_text(text)
                element.send_keys(Keys.TAB)
            
            return element
            
        except TimeoutException:
            if attempt < max_retries - 1:
                st.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                time.sleep(2)
                continue
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Error on attempt {attempt + 1}: {str(e)}, retrying...")
                time.sleep(2)
                continue
            else:
                raise

def scrape_land_records(district, taluk, hobli, village, hssn):
    """Main scraping function with enhanced error handling"""
    
    # Initialize DataFrame
    df = pd.DataFrame(columns=["S.No.", "Survey", "Surnoc", "Hissa"])
    driver = None
    
    try:
        # Setup driver
        st.info("🔄 Initializing Chrome browser...")
        driver = setup_chrome_driver()
        if not driver:
            st.error("❌ Failed to initialize browser")
            return df
        
        # Create wait object with longer timeout
        wait = WebDriverWait(driver, 30)
        
        # Open the website with retry mechanism
        max_page_retries = 3
        for page_attempt in range(max_page_retries):
            try:
                st.info(f"🌐 Opening Karnataka Land Records website (Attempt {page_attempt + 1})...")
                driver.get("https://landrecords.karnataka.gov.in/service2/RTC.aspx")
                
                # Wait for page to fully load
                wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCDistrict")))
                break
                
            except TimeoutException:
                if page_attempt < max_page_retries - 1:
                    st.warning(f"⚠️ Page load timeout, retrying... (Attempt {page_attempt + 2})")
                    time.sleep(5)
                    continue
                else:
                    raise Exception("Failed to load the website after multiple attempts")
        
        # Fill form fields with safe interactions
        st.info(f"📍 Selecting District: {district}")
        safe_element_interaction(driver, wait, By.ID, "ctl00_MainContent_ddlCDistrict", "select", district)
        time.sleep(3)
        
        st.info(f"📍 Selecting Taluk: {taluk}")
        safe_element_interaction(driver, wait, By.ID, "ctl00_MainContent_ddlCTaluk", "select", taluk)
        time.sleep(3)
        
        st.info(f"📍 Selecting Hobli: {hobli}")
        safe_element_interaction(driver, wait, By.ID, "ctl00_MainContent_ddlCHobli", "select", hobli)
        time.sleep(3)
        
        st.info(f"📍 Selecting Village: {village}")
        safe_element_interaction(driver, wait, By.ID, "ctl00_MainContent_ddlCVillage", "select", village)
        time.sleep(3)
        
        # Initialize data collection
        all_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process surveys with enhanced error handling
        successful_surveys = 0
        failed_surveys = 0
        
        for survey_num in range(1, hssn + 1):
            try:
                status_text.text(f"🔍 Processing Survey {survey_num}/{hssn} (✅{successful_surveys} ❌{failed_surveys})")
                progress_bar.progress(survey_num / hssn)
                
                # Fill survey number with retry
                safe_element_interaction(driver, wait, By.ID, "ctl00_MainContent_txtCSurveyNo", "send_keys", str(survey_num))
                time.sleep(2)
                
                # Click Go button with retry
                safe_element_interaction(driver, wait, By.ID, "ctl00_MainContent_btnCGo", "click")
                time.sleep(5)  # Increased wait time
                
                # Process Surnoc dropdown
                try:
                    surnoc_dropdown = wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCSurnocNo")))
                    surnoc_select = Select(surnoc_dropdown)
                    surnoc_options = surnoc_select.options
                    
                    if len(surnoc_options) <= 1:  # Only "Select" option
                        st.info(f"⚠️ No Surnoc data for Survey {survey_num}")
                        failed_surveys += 1
                        continue
                    
                    # Process each surnoc option
                    for surnoc_option in surnoc_options[1:]:
                        surnoc_value = surnoc_option.text.strip()
                        if surnoc_value and surnoc_value != "Select":
                            try:
                                # Select surnoc
                                surnoc_select.select_by_visible_text(surnoc_value)
                                driver.find_element(By.ID, "ctl00_MainContent_ddlCSurnocNo").send_keys(Keys.TAB)
                                time.sleep(3)
                                
                                # Get Hissa data
                                try:
                                    hissa_dropdown = wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddlCHissaNo")))
                                    hissa_select = Select(hissa_dropdown)
                                    hissa_options = hissa_select.options
                                    
                                    if len(hissa_options) > 1:
                                        for hissa_option in hissa_options[1:]:
                                            hissa_value = hissa_option.text.strip()
                                            if hissa_value and hissa_value != "Select":
                                                all_data.append({
                                                    "Survey": survey_num,
                                                    "Surnoc": surnoc_value,
                                                    "Hissa": hissa_value
                                                })
                                    else:
                                        # No hissa data, record surnoc only
                                        all_data.append({
                                            "Survey": survey_num,
                                            "Surnoc": surnoc_value,
                                            "Hissa": "N/A"
                                        })
                                
                                except (TimeoutException, NoSuchElementException):
                                    # Record surnoc without hissa
                                    all_data.append({
                                        "Survey": survey_num,
                                        "Surnoc": surnoc_value,
                                        "Hissa": "N/A"
                                    })
                                    
                            except Exception as e:
                                st.warning(f"⚠️ Error processing Surnoc {surnoc_value}: {str(e)}")
                                continue
                    
                    successful_surveys += 1
                    
                except (TimeoutException, NoSuchElementException):
                    st.warning(f"⚠️ No Surnoc dropdown found for Survey {survey_num}")
                    failed_surveys += 1
                    continue
                    
            except Exception as e:
                st.warning(f"⚠️ Error processing Survey {survey_num}: {str(e)}")
                failed_surveys += 1
                continue
        
        # Create final DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            df.reset_index(drop=True, inplace=True)
            df.insert(0, "S.No.", range(1, len(df) + 1))
        
        status_text.text(f"✅ Completed! Processed {successful_surveys} surveys successfully, {failed_surveys} failed")
        progress_bar.progress(1.0)
        
    except Exception as e:
        st.error(f"❌ Critical error during scraping: {str(e)}")
        st.info("💡 Try reducing the HSSN value or check if the website is accessible")
        
    finally:
        # Ensure driver is properly closed
        if driver:
            try:
                driver.quit()
                st.info("🔒 Browser closed successfully")
            except:
                pass
    
    return df

def main():
    """Main Streamlit application with enhanced UI"""
    
    st.set_page_config(
        page_title="Karnataka Land Records Scraper",
        page_icon="🏞️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏞️ Karnataka Land Records Data Scraper")
    st.markdown("""
    ### Enhanced Cloud-Optimized Version
    This application scrapes land records data from the Karnataka Government website with improved timeout handling and error recovery.
    
    ⚠️ **Important Notes:**
    - Start with small HSSN values (5-10) to test connectivity
    - The process may take several minutes depending on data volume
    - Some surveys may fail due to website limitations - this is normal
    """)
    
    # Sidebar with tips
    with st.sidebar:
        st.header("💡 Usage Tips")
        st.markdown("""
        **For Best Results:**
        - Use exact names as they appear on the website
        - Start with HSSN = 5 for testing
        - Allow 1-2 minutes per survey number
        - If errors occur, try reducing HSSN value
        
        **Troubleshooting:**
        - Timeout errors: Reduce HSSN to 5-10
        - No data: Verify location names
        - Slow performance: Normal for cloud deployment
        """)
    
    # Main form
    with st.form("land_records_form"):
        st.subheader("📝 Enter Land Record Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            district = st.text_input(
                "District *",
                placeholder="e.g., Bengaluru Urban",
                help="Enter exact district name as shown in dropdown"
            )
            
            taluk = st.text_input(
                "Taluk *",
                placeholder="e.g., Bengaluru North",
                help="Enter exact taluk name as shown in dropdown"
            )
            
            hobli = st.text_input(
                "Hobli *",
                placeholder="e.g., Dasarahalli",
                help="Enter exact hobli name as shown in dropdown"
            )
        
        with col2:
            village = st.text_input(
                "Village *",
                placeholder="e.g., Jalahalli",
                help="Enter exact village name as shown in dropdown"
            )
            
            hssn = st.number_input(
                "HSSN (Max Survey Number) *",
                min_value=1,
                max_value=5000,  # Reduced max for cloud limitations
                value=1,
                help="Start with low values. Higher values take longer."
            )
        
        # Warning for high HSSN values
        if hssn > 1000:
            st.warning(f"⚠️ HSSN of {hssn} may take many hours and could timeout.")
        
        submitted = st.form_submit_button(
            "🚀 Start Scraping",
            type="primary",
            use_container_width=True
        )
    
    # Process submission
    if submitted:
        if not all([district, taluk, hobli, village]):
            st.error("❌ Please fill in all required fields!")
            return
        
        # Show estimated time
        estimated_time = 0.43 * hssn  # 0.43 minutes per survey
        st.info(f"⏱️ Estimated processing time: {estimated_time:.1f} minutes for {hssn} surveys")
        
        # Input summary
        with st.expander("📋 Processing Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**District:** {district}")
                st.write(f"**Taluk:** {taluk}")
                st.write(f"**Hobli:** {hobli}")
            with col2:
                st.write(f"**Village:** {village}")
                st.write(f"**Max Survey:** {hssn}")
                st.write(f"**Est. Time:** {estimated_time:.1f} min")
        
        # Start scraping
        start_time = time.time()
        df = scrape_land_records(district, taluk, hobli, village, int(hssn))
        end_time = time.time()
        
        # Results
        if not df.empty:
            processing_time = (end_time - start_time) / 60
            st.success(f"✅ Successfully scraped {len(df)} records in {processing_time:.1f} minutes!")
            
            # Display data
            st.subheader("📊 Scraped Data")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download and stats
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"land_records_{district}_{village}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                st.metric("Processing Time", f"{processing_time:.1f} min")
            
            # Summary
            with st.expander("📈 Data Summary", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Records", len(df))
                with col2:
                    st.metric("Unique Surveys", df['Survey'].nunique())
                with col3:
                    st.metric("Unique Surnocs", df['Surnoc'].nunique() if 'Surnoc' in df.columns else 0)
                with col4:
                    st.metric("Success Rate", f"{(df['Survey'].nunique()/hssn)*100:.1f}%")
        else:
            st.error("❌ No data was scraped. Please check your inputs and try with a smaller HSSN value.")

if __name__ == "__main__":
    main()