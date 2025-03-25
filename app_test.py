# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd



app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME],
)

# make dataframe from assets

df_income = pd.read_csv("assets/real-median-household-income-NY.csv")
df_housing = pd.read_csv("assets/median-listing-price-NY.csv")
df_unemployment = pd.read_csv("assets/unemployment-rate-NY.csv")

# change 'observation_date' column to 'Year'
df_income['Year'] = pd.to_datetime(df_income['observation_date']).dt.year
df_housing['Year'] = pd.to_datetime(df_housing['observation_date']).dt.year
df_unemployment['Year'] = pd.to_datetime(df_unemployment['observation_date']).dt.year

# remove 'observation_date' column
df_income = df_income.drop(columns=['observation_date'])
df_housing = df_housing.drop(columns=['observation_date'])
df_unemployment = df_unemployment.drop(columns=['observation_date'])

# rename other info columns
df_income = df_income.rename(columns={"MEHOINUSNYA672N": "Median Household Income"})
df_housing = df_housing.rename(columns={"MEDLISPRINY": "Median Housing Price"})
df_unemployment = df_unemployment.rename(columns={"NYUR": "Unemployment Rate"})

# merge all 3 dataframes + drop NaN values
merged_df = df_income.merge(df_housing, on='Year', how='outer') \
                     .merge(df_unemployment, on='Year', how='outer')
df = merged_df.dropna()


MIN_YR = df['Year'].min()
MAX_YR = df['Year'].max()

COLORS = {
    "income": "#3cb521",
    "housing": "#fd7e14",
    "unemployment": "#446e9b",
    "inflation": "#cd0200",
    "background": "whitesmoke",
}



"""
==========================================================================
Markdown Text
"""

datasource_text = dcc.Markdown(
    """
    [Data source:](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html)
    Historical Returns on Stocks, Bonds and Bills from NYU Stern School of
    Business
    """
)

asset_allocation_text = dcc.Markdown(
    """
> Explore how changes in the cost of living and housing market dynamics affect household income over time. 

> Adjust the year range and compare trends in median household income, unemployment rates, and housing prices.
  Select two years to see how these key factors evolve between them.
    """
)

footer = html.Div(
    dcc.Markdown(
        """
         The data presented in this analysis is based on publicly available sources and is
        intended for general informational purposes only. It is not meant to replace
        professional financial, economic, or policy advice. The trends and visualizations
        presented here should not be interpreted as financial recommendations and should be
        considered alongside other resources and expert guidance when making financial or
        investment decisions. 
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)



"""
==========================================================================
Figures
"""

def make_line_chart_unemployment(dff):
    start = int(dff.iloc[1]["Year"])  # start year
    end = int(dff.iloc[-1]["Year"])  # end year
    yrs = len(dff["Year"]) - 1
    dtick = 1 if yrs < 16 else 2 if yrs in range(16, 30) else 5

    fig = go.Figure()

    dff["Unemployment Rate"] = dff["Unemployment Rate"]

    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["Median Household Income"],
            name="Median Household Income",
            marker_color=COLORS["income"],
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["Unemployment Rate"],
            name="Unemployment Rate",
            marker_color=COLORS["unemployment"],
            yaxis="y2",
            hoverlabel=dict(
                bgcolor="white",  # Background color for the hover label
                font_size=12,  # Font size for hover text
                font_family="Arial",  # Font family for hover text
                align="left",  # Align the hover text to the left
                namelength=-1  # Prevent truncation of the name (no max length)
            )
        )
    )
    fig.update_layout(
        title=f"Median Household Income vs. Unemployment Rate Trends ({start} - {end})",
        template="none",
        showlegend=True,
        legend=dict(
            x=0.5,
            y=1.1,
            xanchor="right",
            yanchor="top",
            orientation="h",
        ),
        height=400,
        margin=dict(l=80, r=90, t=80, b=55),
        yaxis=dict(
            title="Median Household Income ($)",
            tickprefix="$",
            fixedrange=True,
            title_standoff=10,
        ),
        hoverlabel=dict(
            bgcolor="white",  # Background color for the hover label
            font_size=12,  # Font size for hover text
            font_family="Arial",  # Font family for hover text
            align="left",  # Align the hover text to the left
            namelength=-1  # Prevent truncation of the name (no max length)
        ),
        yaxis2=dict(
            title="Unemployment Rate (%)",
            overlaying="y",
            side="right",
            range=[0, 15],
            fixedrange=True,
            ticksuffix="%",
            title_standoff=15,
        ),
        xaxis=dict(title="Years", fixedrange=True, dtick=dtick),
    )

    return fig


def make_line_chart_housing(dff):
   start = int(dff.iloc[1]["Year"])
   end = int(dff.iloc[-1]["Year"])
   yrs = len(dff["Year"]) - 1
   dtick = 1 if yrs < 16 else 2 if yrs in range(16, 30) else 5


   fig = go.Figure()


   fig.add_trace(
       go.Scatter(
           x=dff["Year"],
           y=dff["Median Household Income"],
           name="Median Household Income",
           marker_color=COLORS["income"],
           hoverlabel=dict(
               bgcolor="white",  # Background color for the hover label
               font_size=12,  # Font size for hover text
               font_family="Arial",  # Font family for hover text
               align="left",  # Align the hover text to the left
               namelength=-1  # Prevent truncation of the name (no max length)
           )
       ),
   )
   fig.add_trace(
       go.Scatter(
           x=dff["Year"],
           y=dff["Median Housing Price"],
           name="Median Housing Price",
           marker_color=COLORS["housing"],
           yaxis="y2",
       ),
   )
   fig.update_layout(
       title=dict(
           text=f"Median Household Income and Median Housing Price ({start} - {end})"
             "<br><span style='font-size: 12px; color:gray;'>"
             "Note: The y-axes are independent and do not imply a direct correlation.</span>",
           x=0.5,  # Centers the title
           y=0.95,  # Positions title slightly lower to fit subtitle
           xanchor="center",
           yanchor="top",
       ),
       template="none",
       showlegend=True,
       legend=dict(
           x=0.5,
           y=1.1,
           xanchor="right",
           yanchor="top",
           orientation="h",
       ),
       height=400,
       margin=dict(l=80, r=90, t=80, b=55),
       xaxis=dict(title="Years", fixedrange=True, dtick=dtick, linecolor="black"),


       yaxis=dict(
           title="Median Household Income ($)",
           tickprefix="$",
           side="left",
           fixedrange=True,
           title_standoff=10,
       ),


       hoverlabel=dict(
           bgcolor="white",  # Background color for the hover label
           font_size=12,  # Font size for hover text
           font_family="Arial",  # Font family for hover text
           align="left",  # Align the hover text to the left
           namelength=-1  # Prevent truncation of the name (no max length)
       ),


       yaxis2=dict(
           title="Median Housing Price ($)",
           tickprefix="$",
           overlaying="y",
           side="right",
           fixedrange=True,
           title_standoff = 15,
       ),
   )
   return fig


def make_slope_chart_unemployment(dff, year_1, year_2):
    # Filter data for the two selected years
    unemployment_1 = dff[dff["Year"] == year_1]["Unemployment Rate"].values[0]
    unemployment_2 = dff[dff["Year"] == year_2]["Unemployment Rate"].values[0]

    # Create a slope graph (just two points with a line)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[year_1, year_2],
                             y=[unemployment_1, unemployment_2],
                             mode='lines+markers+text',
                             text=[f"{year_1}: {unemployment_1}", f"{year_2}: {unemployment_2}"],
                             line=dict(color='blue', width=3),
                             marker=dict(size=10, color='blue'),
                             textposition="top center"))
    fig.update_layout(title="Unemployment Rate Change",
                      xaxis_title="Year",
                      yaxis_title="Unemployment Rate",
                      showlegend=False)
    return fig

def make_slope_chart_housing(dff, year_1, year_2):
    # Filter data for the two selected years
    housing_1 = dff[dff["Year"] == year_1]["Housing Price"].values[0]
    housing_2 = dff[dff["Year"] == year_2]["Housing Price"].values[0]

    # Create a slope graph (just two points with a line)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[year_1, year_2],
                             y=[housing_1, housing_2],
                             mode='lines+markers+text',
                             text=[f"{year_1}: {housing_1}", f"{year_2}: {housing_2}"],
                             line=dict(color='green', width=3),
                             marker=dict(size=10, color='green'),
                             textposition="top center"))
    fig.update_layout(title="Housing Price Change",
                      xaxis_title="Year",
                      yaxis_title="Housing Price",
                      showlegend=False)
    return fig

def make_empty_chart():
    # Placeholder chart when input is invalid or non-consecutive years
    fig = go.Figure()
    fig.update_layout(title="Please select two consecutive years.",
                      xaxis_title="Year",
                      yaxis_title="Value",
                      showlegend=False)
    return fig


"""
==========================================================================
Make Tabs
"""

# =======Play tab components

asset_allocation_card = dbc.Card(asset_allocation_text, className="mt-2")

slider_card = dbc.Card(
    [
        html.H4("Select Year Range...", className="card-title"),
        dcc.RangeSlider(
            id="year_range",
            marks={year: str(year) for year in range(MIN_YR, MAX_YR + 1)},
            min=MIN_YR,
            max=MAX_YR,
            step=1,
            value=[MIN_YR, MAX_YR],
            included=True,
        ),
    ],
    body=True,
    className="mt-4",
    style={"margin-bottom": "10px"},
)

year_select_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Or select two years to compare", className="card-title"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="year_dropdown_1",
                            options=[{"label": str(year), "value": year} for year in range (2017, 2022)],
                            value=2019,
                            style={"width": "100%"},
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="year_dropdown_2",
                            options=[{"label": str(year), "value": year} for year in range(2017, 2023)],
                            value=2021,
                            style={"width": "100%"},
                        ),
                        width=6,
                    ),
                ]
            )
        ]
    ),
    style={"width": "100%", "margin": "0 auto"}
)

# ========= Build tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(
            [asset_allocation_card, slider_card, year_select_card],
            id="tab-1",
            label="Play",
        ),
        dbc.Tab(
            id="tab-2",
            label="Results",
        )
    ],
    id="tabs",
    active_tab="tab-0",
    className="mt-2",
)

"""
===========================================================================
Main Layout
"""

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2(
                            "Cost of Living in New York Analysis",
                            className="text-center text-white p-2",
                        ),
                        html.H6(
                            "Malia de Jesus, CS-150: Community Action Computing",
                            className="text-center text-white",
                        ),
                    ],
                    className="bg-primary p-2",
                )
            )
        ),
        dbc.Row(
            [
                dbc.Col(tabs, width=12, lg=5, className="mt-4 border"),
                dbc.Col(
                    [
                        dcc.Graph(id="line_chart_unemployment", className="mb-2"),
                        dcc.Graph(id="line_chart_housing", className="mb-2"),
                        html.Hr(),
                        html.H6(datasource_text, className="my-2")
                    ],
                    width=12,
                    lg=7,
                    className="pt-4",
                ),
            ],
            className="ms-1",
        ),
        dbc.Row(dbc.Col(footer)),
    ],
    fluid=True,
)



"""
==========================================================================
Callbacks
"""

@app.callback(
    [Output("line_chart_unemployment", "figure"),
     Output("line_chart_housing", "figure")],
    [Input("year_range", "value"),
     Input("year_dropdown_1", "value"),
     Input("year_dropdown_2", "value")],
)
def update_line_charts(selected_range, selected_year_1, selected_year_2):
    ctx = callback_context  # Get context of what triggered callback
    triggered_input = ctx.triggered[0]["prop_id"].split('.')[0] if ctx.triggered[0] else None

    # Case 1: If the year range slider is being used
    if triggered_input == "year_range":
        min_year, max_year = selected_range
        filtered_df = df[(df["Year"] >= min_year) & (df["Year"] <= max_year)]

        # Regular line charts for selected range
        unemployment_fig = make_line_chart_unemployment(filtered_df)
        housing_fig = make_line_chart_housing(filtered_df)

    # Case 2: If the year dropdowns are being used
    elif triggered_input in ["year_dropdown_1", "year_dropdown_2"]:
        # Ensure the years selected are consecutive
        if abs(selected_year_1 - selected_year_2) == 1:
            # If the years are consecutive, generate a slope graph
            if selected_year_1 > selected_year_2:
                selected_year_1, selected_year_2 = selected_year_2, selected_year_1

            # Filter data for the two selected consecutive years
            filtered_df = df[(df["Year"] == selected_year_1) | (df["Year"] == selected_year_2)]

            # Create slope charts for unemployment and housing with selected years
            unemployment_fig = make_slope_chart_unemployment(filtered_df, selected_year_1, selected_year_2)
            housing_fig = make_slope_chart_housing(filtered_df, selected_year_1, selected_year_2)
        else:
            # Handle non-consecutive year selection (optional)
            unemployment_fig = make_empty_chart()  # Placeholder for invalid input
            housing_fig = make_empty_chart()  # Placeholder for invalid input

    else:
        # Default case when no input is given or undefined behavior
        unemployment_fig = make_line_chart_unemployment(df)
        housing_fig = make_line_chart_housing(df)

    return unemployment_fig, housing_fig


@app.callback(
    Output("year_dropdown_2", "options"),
    Output("year_dropdown_2", "value"),
    Input("year_dropdown_1", "value"),
)
def update_dropdown_2_options(selected_year_1):
    filtered_options = [{"label": str(year), "value": year} for year in range(selected_year_1 + 1, 2023)]

    if filtered_options:
        return filtered_options, filtered_options[0]["value"]
    else:
        return filtered_options, None

if __name__ == '__main__':
    app.run(debug=True)

## TODO: update create fig methods (for slider & dropdown)
## TODO: data tables in Results tab
## TODO: README
## TODO: data source





