import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from datetime import datetime
from data_manager import (
    initialize_data,
    get_construction_costs,
    get_operations_costs,
    get_electricity_data,
    get_water_data,
    get_land_requirements,
    get_land_cost_per_acre
)

initialize_data()  #conducts web scrape of electricity prices if necessary
const_cost_df = get_construction_costs()
ops_cost_df = get_operations_costs()
electricity_price_data = get_electricity_data()
land_required = get_land_requirements()
price_per_acre = get_land_cost_per_acre()

def format_component_label(label):  #used for 'components'
    return label.replace("_", " ").capitalize()

# completes the computations required for a given datacenter costs
def compute_datacenter_costs(capacity, rating, project_name, inflation_rate):
    """
    Calculate and generate visualizations for a Colorado datacenter’s construction and
    10-year operations & maintenance (O&M) costs.

    This function performs the following steps:
      1. Validates and parses the provided `capacity` (e.g., "5MW", "20MW", "100MW").
      2. Determines which tier column to use ("tierIII" or "tierIV") based on the `rating`.
      3. Fetches fresh construction cost data and scales each component’s cost by the
         specified megawatt capacity.
      4. Computes the land acquisition cost (in USD millions) for the given capacity,
         then appends it to the construction cost DataFrame.
      5. Constructs a horizontal bar chart (“construction_chart”) showing each component’s
         cost, sorted descending. The total construction cost is displayed in the chart title.
      6. Fetches base operational costs (per-MW) for each component, scales by capacity,
         then adds electricity and water line items for the current year.
      7. Forecasts annual O&M costs for 10 consecutive years by applying the compounded
         `inflation_rate` each year. Aggregates these into a DataFrame, and computes the
         first-year total.
      8. Builds an area chart (“operations_line_chart”) showing year-by-year O&M costs per
         component, with a custom hovertemplate that displays:
           • Year
           • Component name
           • Cost (formatted to two decimal places, in millions USD)
      9. Aggregates the 10-year cumulative O&M totals per component and combines them with
         the total construction cost to form a pie/donut chart (“operations_sunburst”), which
         displays each component’s share of the total 10-year cost of ownership.

    Parameters:
        capacity (str):
            The desired datacenter capacity, formatted as "<number>MW" (e.g., "5MW", "20MW").
            The integer portion is parsed into megawatts for cost scaling. Leading/trailing
            whitespace is ignored, and the “MW” suffix (case-insensitive) is required.
        rating (str):
            The datacenter tier rating, either "Tier III" or "Tier IV". Determines which
            construction-cost column to use ("tierIII" vs. "tierIV") and which base operational
            rate to fetch.
        project_name (str):
            A human-readable name for the datacenter project. Used only for chart headings.
        inflation_rate (float):
            Annual inflation rate expressed as a decimal (e.g., 0.03 for 3%). Applied
            compounding each year over the 10-year O&M forecast.

    Returns:
        dict:
            A dictionary containing three Dash Graph components (dcc.Graph), keyed as:
              - "construction_chart": Horizontal bar chart of all construction and land costs.
              - "operations_line_chart": 10-year area chart of annual O&M costs per component.
              - "operations_sunburst": Donut-style pie chart showing the breakdown of
                total 10-year costs (construction + O&M).

            Each dcc.Graph is ready to be inserted into a Dash layout. For example:
                {
                    "construction_chart": dcc.Graph(figure=construction_fig),
                    "operations_line_chart": dcc.Graph(figure=operations_line_fig),
                    "operations_sunburst": dcc.Graph(figure=donut_fig)
                }

    Raises:
        ValueError:
            - If `capacity` cannot be parsed into an integer number of megawatts.
              Example: “Invalid capacity format: Could not extract MW from 'XYZ'”.
            - If no electricity pricing data is found for the given `capacity` in the current year.
              Example: “No electricity rate found for 20MW in 2025”.


    """
    capacity_str = str(capacity).strip().upper()
    water_price_data = get_water_data(capacity_str)
    try:
        mw = int(capacity_str.replace("MW", ""))
    except ValueError:
        raise ValueError(f"Invalid capacity format: Could not extract MW from '{capacity}'")

    rating_col = 'tierIII' if rating == 'Tier III' else 'tierIV'

    # ----------CONSTRUCTION COSTS ----------------
    const_cost_df = get_construction_costs().copy()  # Ensures fresh copy each time
    construction_df = const_cost_df.copy()
    construction_df["component"] = construction_df["component"].apply(format_component_label)

    if "totalcost" not in construction_df.columns:
        construction_df["totalcost"] = (construction_df[rating_col] * mw).round(0)

    land_cost = (land_required[capacity_str.lower()] * price_per_acre) / 1_000_000
    land_acquisition_df = pd.DataFrame([{
        "component": "Land acquisition",
        "totalcost": round(land_cost, 2)
    }])

    construction_df = pd.concat([land_acquisition_df, construction_df]).reset_index(drop=True)
    construction_df = construction_df.sort_values(by="totalcost", ascending=False)
    total_construction_cost = construction_df["totalcost"].sum()

    #-----CONSTRUCTION COST HORIZONTAL BAR PLOT-----
    construction_fig = go.Figure()

    bar_labels = [              #extra label handling for 'Server Hardware'
        "" if comp == "Server hardware" else f"${val:.0f}M"
        for comp, val in zip(construction_df["component"], construction_df["totalcost"])
    ]

    construction_fig.add_trace(go.Bar(
        x=construction_df["totalcost"],
        y=construction_df["component"],
        orientation='h',
        marker=dict(
            color='rgba(100, 149, 237, 0.6)',
            line=dict(color='rgba(100, 149, 237, 1)', width=1.5)
        ),
        text=bar_labels,
        textposition='outside'
    ))

    # Add internal annotation only for 'Server hardware'
    if "Server hardware" in construction_df["component"].values:
        row = construction_df[construction_df["component"] == "Server hardware"].iloc[0]
        construction_fig.add_annotation(
            x=row["totalcost"] - (row["totalcost"] * 0.05),
            y="Server hardware",
            text=f"${row['totalcost']:.0f}M",
            showarrow=False,
            font=dict(size=12, color="black"),
            align="right",
            xanchor="right"
        )

    # Layout adjustments
    max_cost = construction_df["totalcost"].max()
    construction_fig.update_layout(
        title=f"Total Construction Cost: ${total_construction_cost:.0f} Million (USD)",
        xaxis_title="Cost (USD Millions)",
        yaxis_title="Component",
        yaxis=dict(autorange="reversed"),
        hovermode="y unified",
        margin=dict(l=150, r=100, t=50, b=130),
        xaxis=dict(automargin=True)
    )

    # ------GENERATE OPERATIONS COST FORECAST-------------
    # Multiply base operational cost per MW by total MW capacity
    base_ops = ops_cost_df[["component", rating_col]].copy()
    base_ops.columns = ["component", "BaseCost"]
    base_ops["BaseCost"] *= mw  # scale by capacity
    base_ops["component"] = base_ops["component"].apply(format_component_label)

    # Add electricity cost based on current year and capacity
    current_year = datetime.now().year
    electricity_row = electricity_price_data[
        (electricity_price_data["year"] == current_year) &
        (electricity_price_data["datacenter_size"] == capacity_str)
        ]

    if electricity_row.empty:
        raise ValueError(f"No electricity rate found for {capacity_str} in {current_year}")

    # Cost = $/MWh × MW × hours/year × utilization
    electricity_cost = electricity_row.iloc[0]["rate_dollars_MW"] * mw * 8760 * 0.90 / 1_000_000  # in millions USD

    # Water cost is already annual and per-MW; convert to millions
    water_cost = (water_price_data * mw) / 1_000_000

    # Add electricity and water to base_ops
    base_ops = pd.concat([
        base_ops,
        pd.DataFrame([
            {"component": "Electricity", "BaseCost": electricity_cost},
            {"component": "Water", "BaseCost": water_cost}
        ])
    ], ignore_index=True)

    # Forecast over 10 years, applying inflation
    forecast_data = []
    for i in range(10):
        forecast_year = current_year + i
        for _, row in base_ops.iterrows():
            inflated = row.BaseCost * ((1 + inflation_rate) ** i)
            forecast_data.append({
                "Year": forecast_year,
                "component": row.component,
                "Annual Cost (USD Millions)": round(inflated, 2)
            })

    forecast_df = pd.DataFrame(forecast_data)

    # Total for the first year
    first_year_total = forecast_df[forecast_df["Year"] == current_year]["Annual Cost (USD Millions)"].sum()

    #-------GENERATE 10YR OPERATIONS LINE CHART-------------
    operations_line_fig = px.area(
        forecast_df,
        x="Year",
        y="Annual Cost (USD Millions)",
        color="component",
        title=f"First Year Operations and Maintenance Cost: ${first_year_total:.0f}M",
        line_group="component",
        color_discrete_sequence=px.colors.qualitative.Set2,
        custom_data=["Annual Cost (USD Millions)", "component"]
    )

    # implement custom tooltip for operations line chart
    operations_line_fig.update_traces(
        hovertemplate=(
                "<b>%{x}</b> <br>" +
                "<b>%{customdata[1]}</b> <br>" +
                "<b>$%{customdata[0]:.2f} M</b>" +
                "<extra></extra>"
        )
    )
    operations_line_fig.update_layout(hovermode="x unified")

    # ----------- DONUT CHART FOR 10YR CUMULATIVE COSTS --------------------
    o_and_m_10yr_totals = forecast_df.groupby("component")["Annual Cost (USD Millions)"].sum().reset_index()
    o_and_m_10yr_totals.columns = ["Component", "Value"]
    o_and_m_10yr_totals["Component"] = o_and_m_10yr_totals["Component"].apply(format_component_label)

    donut_data = pd.concat([
        pd.DataFrame({"Component": ["Construction"], "Value": [total_construction_cost]}),
        o_and_m_10yr_totals
    ], ignore_index=True)

    # Calculate the total 10-year cost including construction and O&M
    total_10yr_cost = donut_data["Value"].sum()

    # Donut Chart Figure with updated title
    donut_fig = px.pie(
        donut_data,
        names="Component",
        values="Value",
        hole=0.5,
        title=f"Total 10 Year Cost of Ownership: ${total_10yr_cost:.0f}M",
        color_discrete_sequence=px.colors.qualitative.G10
    )

    donut_fig.update_traces(
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Total Cost: %{value:.2f}M<extra></extra>',
        showlegend=False
    )

    donut_fig.update_layout(
        height=800,
        width=800,
        margin=dict(t=60, b=60, l=60, r=60)
    )

    return {
        "construction_chart": dcc.Graph(figure=construction_fig),
        "operations_line_chart": dcc.Graph(figure=operations_line_fig),
        "operations_sunburst": dcc.Graph(figure=donut_fig)  # preserved key
    }
