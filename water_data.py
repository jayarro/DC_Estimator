

def generate_water_cost(capacity_str):
    """
    Calculate the annual water cost (in USD) for a given datacenter capacity.

    This function uses predefined daily water usage and pipe-size data for three
    standard datacenter capacities ("5MW", "20MW", "100MW"), along with fixed
    2025 Denver water rates (raw water cost per 1,000 gallons and monthly pipe
    charges). It computes:
      1. Annual raw water usage cost based on daily gallons used.
      2. Annual fixed pipe charge based on pipe size.
      3. Sum of raw water cost and pipe charge, rounded to the nearest dollar.

    Parameters:
        capacity_str (str):
            One of "5MW", "20MW", or "100MW". Determines:
              • Daily water usage (gallons per day) for the datacenter capacity.
              • Corresponding pipe size (in inches) for the monthly pipe charge.

    Returns:
        float:
            The total annual water cost (in USD), rounded to the nearest whole dollar.

    Raises:
        ValueError:
            If `capacity_str` is not one of the supported keys ("5MW", "20MW", "100MW").

    Example:
        >>> generate_water_cost("20MW")
        15400.0
    """
    dc_water = {
        "5MW": {"water_usage_gpd": 2500, "pipe_size_in": 2},
        "20MW": {"water_usage_gpd": 10000, "pipe_size_in": 3},
        "100MW": {"water_usage_gpd": 50000, "pipe_size_in": 8}
    }

    # 2025 Denver water rates
    water_rates_2025 = {
        "pipe_rates": {
            "2in": 91,    # monthly
            "3in": 196,
            "8in": 1355
        },
        "raw_water_cost_per_1000_gallons": 1.04
    }

    # Validate input
    if capacity_str not in dc_water:
        raise ValueError(f"Unsupported capacity: {capacity_str}. Choose from {list(dc_water.keys())}")

    usage_info = dc_water[capacity_str]
    gpd = usage_info["water_usage_gpd"]
    pipe_key = f"{usage_info['pipe_size_in']}in"

    # Compute raw water usage cost
    annual_gallons = gpd * 365
    raw_water_cost = (annual_gallons / 1000) * water_rates_2025["raw_water_cost_per_1000_gallons"]

    # Compute fixed pipe charge
    pipe_charge = water_rates_2025["pipe_rates"][pipe_key] * 12  # 12 months

    # Total annual water cost
    total_annual_cost = raw_water_cost + pipe_charge

    return round(total_annual_cost, 0)