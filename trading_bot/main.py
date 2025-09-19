import configparser
import os
from datetime import datetime

# Import the modules we've created
from auth.icici_login import get_session_token
from api.breeze_api import BreezeAPIWrapper
from utils.options_calculator import get_greeks_for_option_chain

def main():
    """
    Main function to run the trading bot.
    """
    print("Starting the trading bot...")

    # --- 1. Load Configuration ---
    # Construct the path to the config file relative to this script's location
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.ini')
    config = configparser.ConfigParser()

    # Check if config file exists before trying to read
    if not os.path.exists(config_path):
        print("="*80)
        print("!!! CONFIGURATION FILE MISSING !!!")
        print(f"The configuration file was not found at: {config_path}")
        print("Please ensure the 'config/settings.ini' file exists.")
        print("="*80)
        return

    config.read(config_path)

    try:
        breeze_config = config['breeze']
        icici_config = config['icici']

        api_key = breeze_config['api_key']
        api_secret = breeze_config['api_secret']
        user_id = icici_config['user_id']
        password = icici_config['password']
        totp_key = icici_config['totp_key']

        if 'YOUR_' in api_key or 'YOUR_' in user_id:
            print("="*80)
            print("!!! CONFIGURATION INCOMPLETE !!!")
            print(f"Please fill in your credentials in the config file located at: {config_path}")
            print("="*80)
            return

    except KeyError as e:
        print(f"Error: Missing section or key in configuration file: {e}")
        print("Please ensure 'config/settings.ini' has '[breeze]' and '[icici]' sections with all required keys.")
        return

    # --- 2. Automated Login to get Session Token ---
    print("\nAttempting to log in to ICICI Direct to get a session token...")
    session_token = get_session_token(user_id, password, totp_key, api_key)

    if not session_token:
        print("Could not retrieve session token. Exiting.")
        return

    print(f"Successfully obtained session token.")

    # --- 3. Initialize and Connect to Breeze API ---
    print("\nInitializing Breeze API Wrapper...")
    breeze = BreezeAPIWrapper(api_key=api_key, api_secret=api_secret)

    if not breeze.connect(session_token):
        print("Failed to connect to Breeze API. Exiting.")
        return

    # --- 4. Demonstrate Functionality: Get Option Chain Greeks ---
    print("\nFetching option chain and calculating greeks for NIFTY...")

    # For demonstration, we'll use a hardcoded future expiry date.
    # A real implementation should have a more robust way to determine the current expiry.
    expiry_date = "2025-10-02" # IMPORTANT: User should update this to a valid, near-term expiry date.
    print(f"Using expiry date: {expiry_date}")

    calls_df, puts_df = get_greeks_for_option_chain(
        breeze=breeze,
        stock_code="NIFTY",
        expiry_date=expiry_date
    )

    if calls_df is not None and not calls_df.empty:
        print("\n--- Call Options ---")
        print(calls_df.to_string())

    if puts_df is not None and not puts_df.empty:
        print("\n--- Put Options ---")
        print(puts_df.to_string())

    print("\nBot has finished its task.")


if __name__ == "__main__":
    main()
