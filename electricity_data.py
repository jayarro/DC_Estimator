import pandas as pd
import os
from datetime import datetime

DATA_DIR = "data"
OUTPUT_FILE = "electricity_prices.csv"
os.makedirs(DATA_DIR, exist_ok=True)

def electricity_price_sheet():
    """
    Generate and save a CSV file containing the current year’s electricity rates
    for three standard datacenter sizes: 5MW, 20MW, and 100MW.

    This function performs the following steps:
      1. Defines hard‐coded rate values in cents per kilowatt-hour for 5MW, 20MW, and 100MW.
      2. Retrieves the current calendar year.
      3. Builds a pandas DataFrame with these columns:
           • year            (int): The current year.
           • datacenter_size (str): One of "5MW", "20MW", or "100MW".
           • rate_cents_kwh  (float): The electricity rate in cents per kWh, rounded to two decimals.
           • rate_dollars_MW (float): The rate expressed in dollars per MW (cents_per_kWh × 10), rounded to two decimals.
           • source          (str): A constant label "Current Year Rates".
      4. Writes the DataFrame to “data/electricity_prices.csv” (creating the “data” directory if needed).
      5. Prints a confirmation message with the full output file path.

    Side Effects:
        - Ensures that a local “data” directory exists.
        - Overwrites (or creates) the file “data/electricity_prices.csv” with the new data.

    Returns:
        None
    """
    current_rates = {
        '5MW': 12.5,   # cents per kWh
        '20MW': 8.8,   # cents per kWh
        '100MW': 6.5   # cents per kWh
    }
    current_year = datetime.now().year

    records = []
    for size, cents_kwh in current_rates.items():
        records.append({
            'year': current_year,
            'datacenter_size': size,
            'rate_cents_kwh': round(cents_kwh, 2),
            'rate_dollars_MW': round(cents_kwh * 10, 2),
            'source': 'Current Year Rates'
        })

    df = pd.DataFrame(records)
    output_path = os.path.join(DATA_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)
    print(f"Current year rates saved to {output_path}")

if __name__ == "__main__":
    electricity_price_sheet()
