import csv
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def rotate_driver():
    chrome_service = Service(ChromeDriverManager().install())
    firefox_service = Service(GeckoDriverManager().install())
    edge_service = Service(EdgeChromiumDriverManager().install())
    
    browsers = [
        ('Chrome', webdriver.Chrome(service=chrome_service)),
        ('Firefox', webdriver.Firefox(service=firefox_service)),
        ('Edge', webdriver.Edge(service=edge_service))
    ]
    return browsers

def scrape_emails(input_csv, output_csv):
    data = []
    
    # Regular expression to find email addresses
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # Setup initial driver
    browsers = rotate_driver()
    browser_name, driver = browsers[0]  # Start with the first browser

    # Read URLs from input CSV
    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)
        processed_count = 0
        
        for row in rows:
            facebook_url = row['Facebook URL']
            domain = row['URL']
            business_name = row['Business Name']
            phone_number = row['Phone Number']
            
            if not facebook_url or 'facebook.com' not in facebook_url:
                print(f"Invalid URL {facebook_url}")
                processed_count += 1
                continue
            
            try:
                driver.get(facebook_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                # Handle any popups here if needed
                # Example:
                try:
                    popup_close_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mount_0_0_ef"]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div')))
                    popup_close_button.click()
                    print("Closed popup successfully")
                except:
                    print("No popup found or could not be closed")

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Find all <span> elements that potentially contain email addresses
                email_elements = soup.find_all('span', text=re.compile(email_regex))
                
                email = None
                if email_elements:
                    # Extract the email address from the first matching <span> element
                    email_text = email_elements[0].get_text(strip=True)
                    email_matches = re.findall(email_regex, email_text)
                    if email_matches:
                        email = email_matches[0]

                # Add the entry even if email is not found
                data.append({
                    'URL': domain,
                    'Business Name': business_name,
                    'Phone Number': phone_number,
                    'Facebook URL': facebook_url,
                    'Email': email if email else 'No email found'
                })
                if email:
                    print(f"Success: {domain} - {business_name} - {phone_number} - {facebook_url} - {email}")
                else:
                    print(f"No email found for {facebook_url}")
            except Exception as e:
                print(f"Error fetching {facebook_url}: {e}")
                data.append({
                    'URL': domain,
                    'Business Name': business_name,
                    'Phone Number': phone_number,
                    'Facebook URL': facebook_url,
                    'Email': 'Error'
                })

            processed_count += 1
            progress_percentage = (processed_count / total_rows) * 100
            print(f"Progress: {progress_percentage:.2f}% complete")

            # Rotate to the next browser every 100 URLs
            if processed_count % 100 == 0:
                browser_name, driver = browsers[processed_count // 100 % len(browsers)]

    driver.quit()

    # Write data to output CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['URL', 'Business Name', 'Phone Number', 'Facebook URL', 'Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Usage
input_csv = 'urls-to-scrape-fb.csv'  # Input CSV file containing Facebook URLs and other details
output_csv = 'fb_business_emails.csv'  # Output CSV file to save the scraped email addresses
scrape_emails(input_csv, output_csv)
