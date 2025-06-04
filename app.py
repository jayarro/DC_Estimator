import warnings
#suppress annoying deprecation warning from Dash
warnings.filterwarnings("ignore", category=DeprecationWarning)
import dash
from dash import html, dcc, Input, Output, State
from calculations import compute_datacenter_costs

"""
Dash application for estimating Colorado datacenter costs.

This module defines a Dash web app that allows users to input:
  - A data center project name
  - Desired capacity (5 MW, 20 MW, or 100 MW)
  - Tier rating (Tier III or Tier IV)
  - An annual inflation rate

Upon clicking “Submit,” it calls `compute_datacenter_costs` (from calculations.py)
to generate three visualizations:
  1. Construction cost breakdown
  2. 10-Year operations & maintenance (O&M) cost forecast
  3. 10-Year cumulative cost sunburst

The resulting charts are rendered under the inputs. If an error occurs during
computation, a red‐colored error message is displayed instead.

Usage:
    $ python this_script.py
    (Launches the Dash server on http://127.0.0.1:8050/ by default.)

Dependencies:
    - dash
    - dash.html, dash.dcc, dash.Input, dash.Output, dash.State
    - compute_datacenter_costs (from calculations.py)
    - plotly (implicitly used by compute_datacenter_costs)
"""

# initialize the Dash app
app = dash.Dash(__name__)
app.title = "Colorado Datacenter Cost Estimator"

# set dash layout
app.layout = html.Div(
    style={
        'fontFamily': 'Inter, sans-serif',
        'maxWidth': '900px',
        'margin': 'auto',
        'padding': '20px',
        'backgroundColor': '#f8f9fa',
        'borderRadius': '8px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
    },
    children=[
        html.H1(
            "Datacenter Resources and Costs in Colorado",
            style={'textAlign': 'center', 'color': '#343a40', 'marginBottom': '30px'}
        ),

        # project name
        html.Div([
            html.Label("Data Center Project Name:", style={'fontWeight': 'bold'}),
            dcc.Input(
                id='project-name-input',
                type='text',
                placeholder="new project",
                value="New Data Center",
                style={'width': '100%', 'marginBottom': '20px', 'padding': '8px'}
            )
        ]),

        # capacity dropdown menu
        html.Div([
            html.Label("Data Center Capacity:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='datacenter-capacity-dropdown',
                options=[
                    {'label': '5 MW', 'value': '5MW'},
                    {'label': '20 MW', 'value': '20MW'},
                    {'label': '100 MW', 'value': '100MW'}
                ],
                placeholder="5 MW",
                value="5MW",
                style={'marginBottom': '20px'}
            )
        ]),

        # data center tier radio buttons
        html.Div([
            html.Label("Data Center Rating:", style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='datacenter-rating-radio',
                options=[
                    {'label': 'Tier III', 'value': 'Tier III'},
                    {'label': 'Tier IV', 'value': 'Tier IV'}
                ],
                value='Tier III',
                inline=True,
                style={'marginBottom': '20px'}
            )
        ]),

        # inflation rate slider bar
        html.Div([
            html.Label("Inflation Rate (%):", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='inflation-rate-slider',
                min=0.0,
                max=0.1,
                step=0.005,
                value=0.03,
                marks={i/100: f"{i}%" for i in range(0, 11)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '30px'}),

        # submit button (centered)
        html.Div(
            html.Button("Submit", id='submit-button', n_clicks=0,
                        style={
                            'padding': '10px 20px',
                            'backgroundColor': '#007bff',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer'
                        }
                        ),
            style={'textAlign': 'center', 'marginBottom': '30px'}
        ),


        html.Hr(),

        # output visualizations
        html.Div(id='output-container', style={'marginTop': '40px'})
    ]
)

# callback
@app.callback(
    Output('output-container', 'children'),
    Input('submit-button', 'n_clicks'),
    State('datacenter-capacity-dropdown', 'value'),
    State('datacenter-rating-radio', 'value'),
    State('project-name-input', 'value'),
    State('inflation-rate-slider', 'value')
)
def update_output(n_clicks, capacity, rating, project_name, inflation_rate):
    if n_clicks == 0:
        return ""

    try:
        charts = compute_datacenter_costs(capacity, rating, project_name, inflation_rate)
        return html.Div([
            html.H3(f"{project_name}: Construction Cost Breakdown"),
            charts["construction_chart"],
            html.H3(f"{project_name}: 10-Year O&M Cost Forecast"),
            charts["operations_line_chart"],
            html.H3(f"{project_name}: 10-Year Cumulative Costs"),
            charts["operations_sunburst"]
        ])
    except Exception as e:
        return html.Div(f"An error occurred: {str(e)}", style={"color": "red"})


# Run the app
if __name__ == '__main__':
    app.run(debug=True)

