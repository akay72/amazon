import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
import requests
from selenium.webdriver.chrome.options import Options
import traceback
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


# Set the layout to 'wide'
st.set_page_config(layout="wide")

def solve_captcha(captcha_image_path):
    solver = TwoCaptcha('0b68384ccb5fe1b87d3c4dd5464fd9c3')
    result = solver.normal(captcha_image_path)
    time.sleep(15)
    return result

def process_url(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Specify chromedriver path here
        driver_path = 'chromedriver.exe' # Change this to your path
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        
        driver.get(url)
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find('form')
        captcha_image = form.find('img')['src']

        response = requests.get(captcha_image)
        captcha_image_path = 'captcha_image.jpg'
        with open(captcha_image_path, 'wb') as fp:
            fp.write(response.content)

        captcha_solution = solve_captcha(captcha_image_path)
        captcha_input_field = driver.find_element(By.XPATH,'//*[@id="captchacharacters"]')
        captcha_input_field.send_keys(captcha_solution['code'])
        time.sleep(5)
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and @class='a-button-text' and contains(text(), 'Continue shopping')]")
        submit_button.click()
        time.sleep(10)
        page_html = driver.page_source
        driver.quit()
        return page_html
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.text(traceback.format_exc())
        return None

def main():
    st.title('CAPTCHA Solver for Amazon')

    # Sidebar
    st.sidebar.header("Navigation")
    page_selection = st.sidebar.radio("Go to", ["CAPTCHA Solver", "How to Use", "About"])

    if page_selection == "How to Use":
        st.info("""
        1. Navigate to the CAPTCHA Solver tab.
        2. Enter the URL of the Amazon product page with a CAPTCHA.
        3. Click on 'Process CAPTCHA'.
        4. After processing, a download button will appear.
        5. Click it to download the page content.
        """)

    elif page_selection == "About":
        st.info("""
        This app is designed to automate CAPTCHA solving for Amazon product pages. 
        It uses the TwoCaptcha service for CAPTCHA solving. The main purpose is to showcase the power of automation and Streamlit.
        """)

    elif page_selection == "CAPTCHA Solver":
        
        st.write("""
        Enter the URL of the Amazon product page, and we'll handle the CAPTCHA for you!
        """)
        url = st.text_input('URL:')
        if st.button('Process CAPTCHA'):
            if not url:
                st.warning('Please enter a URL in the input box.')
                return

            with st.spinner('Processing...'):
                page_html = process_url(url)
                if page_html:
                    st.download_button(
                        label="Download Page HTML",
                        data=page_html.encode('utf-8'),
                        file_name='page_html.txt',
                        mime='text/plain'
                    )
                    st.success('CAPTCHA Processed! Download the page content using the button above.')

if __name__ == '__main__':
    main()
