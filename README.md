# Colorado Datacenter Cost Estimator

A Dash-based web application that estimates construction and 10-year operations & maintenance (O&M) costs for hypothetical datacenters in Colorado.
This project ties together cost‐modeling logic, data ingestion, and interactive Plotly visualizations to provide a simple “what‐if” tool for capacity, tier rating, and inflation assumptions.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Usage](#usage)
   - [Generate Current Electricity Rates](#generate-current-electricity-rates)
   - [Launch the Dash App](#launch-the-dash-app)
6. [File Structure & Descriptions](#file-structure--descriptions)
7. [Contributing](#contributing)
8. [License](#license)

---

## Project Overview

This repository contains code to:

- **Processes** raw electricity pricing and water‐cost data for three standard datacenter sizes (5 MW, 20 MW, 100 MW).
- **Compute** a detailed breakdown of construction costs based on Tier III vs. Tier IV ratings and per‐MW scale.
- **Forecast** annual O&M costs (electricity, water, and other line items) over a 10-year horizon, applying inflation.
- **Visualize** results in an interactive Dash app with horizontal bar charts, area plots, and a donut chart for cumulative costs.

By adjusting capacity, tier rating, project name, and inflation rate, users can see how key cost drivers change over time.

---

## Features

- **Data Manager**:
  - Automatically creates a `data/` directory.
  - Loads or scrapes (if missing) current electricity prices.
  - Provides getters for construction, operations, electricity, water, and land data.

- **Electricity Data Script** (`electricity.py`):
  - Generates a CSV of “current year” electricity rates for 5 MW, 20 MW, and 100 MW.
  - Uses Colorado specific 2025 electricity rates

- **Water Cost Function** (`water_data.py`):
  - Returns an annual water‐cost estimate (USD) based on capacity.
  - Uses Denver-specific 2025 rates and hard-coded daily usage/pipe sizes.

- **Calculation Logic** (`calculations.py`):
  - Scales construction‐cost components by MW and appends a land‐acquisition line item.
  - Builds Plotly figures:
    - Horizontal bar chart of construction cost breakdown.
    - 10-year area chart of O&M costs, with custom hover templates.
    - Donut chart (pie with hole) showing total 10-year cost shares.

- **Dash App** (`app.py`):
  - Presents a form to capture:
    - Project name (string)
    - Datacenter capacity (5 MW, 20 MW, 100 MW)
    - Tier rating (Tier III or Tier IV)
    - Annual inflation rate slider (0%–10%)
  - On “Submit,” calls the `compute_datacenter_costs()` function to retrieve Plotly figures.
  - Renders three charts under a clean Bootstrap‐inspired layout.

---

## Prerequisites

- Python 3.8+
- Recommended virtual environment (venv or conda)

### Python Packages

Install these via `pip install` or in your virtual environment:

- `dash`
- `pandas`
- `plotly`
- `requests`

Example:

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate.bat     # Windows

pip install dash pandas plotly requests

