import time
import urllib.parse
from pyotp import TOTP
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_session_token(user_id, password, totp_key, api_key):
    """
    Automates the ICICI Direct login process to retrieve a session token.

    Args:
        user_id (str): Your ICICI Direct User ID.
        password (str): Your ICICI Direct password.
        totp_key (str): The TOTP key for 2-factor authentication.
        api_key (str): Your Breeze API key.

    Returns:
        str: The session token if login is successful, otherwise None.
    """
    browser = None
    try:
        # Use webdriver-manager to automatically handle the chromedriver
        service = ChromeService(executable_path=ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        browser = webdriver.Chrome(service=service, options=options)

        login_url = f"https://api.icicidirect.com/apiuser/login?api_key={urllib.parse.quote_plus(api_key)}"
        browser.get(login_url)
        browser.implicitly_wait(10)

        # WARNING: The XPaths used here are brittle and may break if the
        # ICICI Direct website changes its layout.

        # Enter user ID and password
        username_field = browser.find_element(By.XPATH, '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[1]/input')
        password_field = browser.find_element(By.XPATH, '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[3]/div/input')

        username_field.send_keys(user_id)
        password_field.send_keys(password)

        # Click checkbox and login button
        browser.find_element(By.XPATH, '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[4]/div/input').click()
        browser.find_element(By.XPATH, '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[5]/input[1]').click()

        time.sleep(2) # Wait for the next page to load

        # Enter TOTP
        pin_field = browser.find_element(By.XPATH, '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/input')
        totp = TOTP(totp_key)
        token = totp.now()
        pin_field.send_keys(token)

        # Click submit
        browser.find_element(By.XPATH, '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[4]/input[1]').click()

        time.sleep(5) # Wait for the redirect and token generation

        # Extract the session token from the URL
        current_url = browser.current_url
        if 'apisession=' in current_url:
            session_token = current_url.split('apisession=')[1]
            # The token might have other URL parameters after it, so we split by '&'
            session_token = session_token.split('&')[0]
            print(f"Successfully retrieved session token.")
            return session_token
        else:
            print("Failed to retrieve session token. Check credentials or website flow.")
            return None

    except Exception as e:
        print(f"An error occurred during the login process: {e}")
        return None
    finally:
        if browser:
            browser.quit()
