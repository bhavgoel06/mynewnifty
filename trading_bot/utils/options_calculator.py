import pandas as pd
import numpy as np
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.greeks.numerical import delta, gamma, theta, vega, rho
from scipy.optimize import brentq
from datetime import datetime

# Note: The 'breeze' object (BreezeAPIWrapper instance) is expected to be passed from the main script.

def _calculate_implied_volatility(row, spot_price, risk_free_rate):
    """Helper function to calculate implied volatility for a single option."""
    S = spot_price
    K = row['strike_price']
    T = (pd.to_datetime(row['expiry_date']) - datetime.now()).days / 365.0
    r = risk_free_rate
    option_price = row['ltp']
    flag = 'c' if row['right'].lower() == 'call' else 'p'

    if T <= 0: # Cannot calculate for expired options
        return np.nan

    def objective_function(sigma):
        return black_scholes(flag, S, K, T, r, sigma) - option_price

    try:
        # Use brentq to find the root of the objective function (i.e., the IV)
        return brentq(objective_function, 0.01, 5.0) # Search between 1% and 500% vol
    except (ValueError, RuntimeError):
        # ValueError if objective_function has the same sign at bounds, RuntimeError if max iterations reached
        return np.nan

def _calculate_greeks_for_row(row, spot_price, risk_free_rate):
    """Helper function to calculate all greeks for a single option row."""
    S = spot_price
    K = row['strike_price']
    T = (pd.to_datetime(row['expiry_date']) - datetime.now()).days / 365.0
    r = risk_free_rate
    sigma = row['implied_volatility']
    flag = 'c' if row['right'].lower() == 'call' else 'p'

    if pd.isna(sigma) or T <= 0:
        return pd.Series([np.nan] * 5, index=['delta', 'gamma', 'theta', 'vega', 'rho'])

    delta_val = delta(flag, S, K, T, r, sigma)
    gamma_val = gamma(flag, S, K, T, r, sigma)
    theta_val = theta(flag, S, K, T, r, sigma)
    vega_val = vega(flag, S, K, T, r, sigma)
    rho_val = rho(flag, S, K, T, r, sigma)

    return pd.Series([delta_val, gamma_val, theta_val, vega_val, rho_val],
                     index=['delta', 'gamma', 'theta', 'vega', 'rho'])


def get_greeks_for_option_chain(breeze, stock_code, expiry_date, risk_free_rate=0.10, range_size=5):
    """
    Fetches the option chain for a stock, calculates implied volatility and greeks.

    Args:
        breeze (BreezeAPIWrapper): An instance of the Breeze API wrapper.
        stock_code (str): The stock code (e.g., "NIFTY").
        expiry_date (str): The expiry date in "YYYY-MM-DD" format.
        risk_free_rate (float): The risk-free interest rate.
        range_size (int): The number of strikes to fetch above and below ATM.

    Returns:
        (pd.DataFrame, pd.DataFrame): A tuple containing DataFrames for calls and puts with greeks.
    """
    try:
        # 1. Get Spot Price and determine ATM strike
        spot_quote = breeze.get_quotes(stock_code=stock_code, exchange_code="NSE", product_type="cash")
        if not spot_quote or not spot_quote.get("Success"):
            print(f"Could not fetch spot price for {stock_code}")
            return None, None
        spot_price = spot_quote["Success"][0]["ltp"]
        atm_strike = round(spot_price / 50) * 50
        print(f"Spot Price: {spot_price}, ATM Strike: {atm_strike}")

        # 2. Define a helper to process the chain for a given right (call/put)
        def process_chain(right):
            option_chain = breeze.get_option_chain_quotes(
                stock_code=stock_code,
                exchange_code="NFO",
                product_type="options",
                expiry_date=f"{expiry_date}T06:00:00.000Z",
                right=right
            )
            if not option_chain or not option_chain.get("Success"):
                print(f"Could not fetch option chain for {right.capitalize()}s")
                return pd.DataFrame()

            df = pd.DataFrame(option_chain["Success"])
            df['strike_price'] = df['strike_price'].astype(float)
            df['ltp'] = df['ltp'].astype(float)

            # Filter for strikes around ATM
            strike_increment = 50
            lower_bound = atm_strike - range_size * strike_increment
            upper_bound = atm_strike + range_size * strike_increment

            filtered_df = df[(df['strike_price'] >= lower_bound) & (df['strike_price'] <= upper_bound)]
            if filtered_df.empty:
                return pd.DataFrame()

            # 3. Calculate IV
            filtered_df['implied_volatility'] = filtered_df.apply(
                _calculate_implied_volatility, axis=1, spot_price=spot_price, risk_free_rate=risk_free_rate
            )

            # 4. Calculate Greeks
            greeks_df = filtered_df.apply(
                _calculate_greeks_for_row, axis=1, spot_price=spot_price, risk_free_rate=risk_free_rate
            )

            result_df = pd.concat([filtered_df, greeks_df], axis=1)

            # Select and reorder columns for clarity
            cols = ['expiry_date', 'right', 'strike_price', 'ltp', 'implied_volatility', 'delta', 'gamma', 'theta', 'vega', 'rho']
            return result_df[cols].sort_values('strike_price').reset_index(drop=True)

        # 5. Process for both Calls and Puts
        calls_df = process_chain("call")
        puts_df = process_chain("put")

        return calls_df, puts_df

    except Exception as e:
        print(f"An error occurred while calculating greeks: {e}")
        return None, None
