import pandas as pd
import os
from electricity_data import electricity_price_sheet
from water_data import generate_water_cost
"""
data_manager.py

This module handles data initialization and retrieval for the Colorado datacenter cost estimator.
It ensures that required CSV files are present (scraping raw electricity price data if needed),
and provides simple “getter” functions for:

  • Construction cost data
  • Operations & maintenance cost data
  • Electricity price data
  • Water cost data (generated on-the-fly based on capacity)
  • Land acreage requirements (hard-coded per MW)
  • Land cost per acre (hard-coded)

Functions:
    initialize_data():
        Check if “electricity_prices.csv” exists under the “data” directory.
        If not, invoke electricity_price_sheet().run() to download and save raw electricity pricing.

    get_construction_costs() -> pd.DataFrame:
        Load and return “construction_costs.csv” from the “data” directory as a pandas DataFrame.

    get_operations_costs() -> pd.DataFrame:
        Load and return “operations_costs.csv” from the “data” directory as a pandas DataFrame.

    get_electricity_data() -> pd.DataFrame:
        Load and return “electricity_prices.csv” from the “data” directory as a pandas DataFrame.

    get_water_data(capacity_str: str) -> float:
        Compute and return the annual water cost (in USD) for a given datacenter capacity string
        (e.g., “5MW”, “20MW”) by delegating to generate_water_cost(capacity_str).

    get_land_requirements() -> dict[str, int]:
        Return a dictionary mapping capacity keys (“5mw”, “20mw”, “100mw”) to required acreage.

    get_land_cost_per_acre() -> int:
        Return the fixed cost per acre (in USD) for land acquisition.

Usage:
    - Import initialize_data() at application startup to ensure electricity data is available.
    - Call the various get_...() functions from calculations.py (or elsewhere) to retrieve
      DataFrames or static data needed for cost computations.

Example:
    from data_manager import initialize_data, get_construction_costs

    initialize_data()  # scrapes electricity prices if missing
    df = get_construction_costs()
    # … proceed to compute costs …

"""

# Define paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Run data scraping/generation if files not present
def initialize_data():
    if not os.path.exists(os.path.join(DATA_DIR, 'electricity_prices.csv')):
        electricity_price_sheet().run()

# Getter functions for use by calculations.py
def get_construction_costs():
    return pd.read_csv(os.path.join(DATA_DIR, 'construction_costs.csv'))

def get_operations_costs():
    return pd.read_csv(os.path.join(DATA_DIR, 'operations_costs.csv'))

def get_electricity_data():
    return pd.read_csv(os.path.join(DATA_DIR, 'electricity_prices.csv'))

def get_water_data(capacity_str):
    return generate_water_cost(capacity_str)

def get_land_requirements():
    return {
        '5mw': 4,
        '20mw': 15,
        '100mw': 35
    }

def get_land_cost_per_acre():
    return 1_000_000  # USD


def main():
    pass
main()