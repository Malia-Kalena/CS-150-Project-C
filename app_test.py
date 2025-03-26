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
df_gas_price = pd.read_csv("assets/Gasoline_Retail_Prices_Weekly_Average_by_Region__Beginning_2007.csv")

# change 'observation_date' column to 'Year'
df_income['Year'] = pd.to_datetime(df_income['observation_date']).dt.year
df_housing['Year'] = pd.to_datetime(df_housing['observation_date']).dt.year
df_unemployment['Year'] = pd.to_datetime(df_unemployment['observation_date']).dt.year

# remove 'observation_date' column
df_income = df_income.drop(columns=['observation_date'])
df_housing = df_housing.drop(columns=['observation_date'])
df_unemployment = df_unemployment.drop(columns=['observation_date'])

# cleaning gas price data
df_gas_price["Date"] = pd.to_datetime(df_gas_price["Date"])
df_gas_price["Year"] = df_gas_price["Date"].dt.year
df_yearly_avg_gas_price = df_gas_price.groupby("Year")["New York State Average ($/gal)"].mean().reset_index()
df_yearly_avg_gas_price = df_yearly_avg_gas_price.rename(columns={"New York State Average ($/gal)": "Average Gas Price"})
df_yearly_avg_gas_price["Average Gas Price"] = df_yearly_avg_gas_price["Average Gas Price"].round(2)


# rename other info columns
df_income = df_income.rename(columns={"MEHOINUSNYA672N": "Median Household Income"})
df_housing = df_housing.rename(columns={"MEDLISPRINY": "Median Housing Price"})
df_unemployment = df_unemployment.rename(columns={"NYUR": "Unemployment Rate"})

# merge all 3 dataframes + drop NaN values
merged_df = df_income.merge(df_housing, on='Year', how='outer') \
                     .merge(df_unemployment, on='Year', how='outer') \
                     .merge(df_yearly_avg_gas_price, on='Year', how='outer')
df = merged_df.dropna()

MIN_YR = df['Year'].min()
MAX_YR = df['Year'].max()

COLORS = {
    "Median Household Income": "#3cb521",
    "Median Housing Price": "#fd7e14",
    "Unemployment Rate": "#446e9b",
    "Average Gas Price" : "#fcba03",
    "background": "whitesmoke",
}



"""
==========================================================================
Markdown Text
"""

asset_allocation_text = dcc.Markdown(
    """
> Explore how changes in the cost of living and housing market dynamics affect household income over time. 

> Adjust the year range and compare trends in median household income, unemployment rates, and housing prices.
  Select an indicator to see how it evolves between the years.
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
Tables
"""
results_table = dash_table.DataTable(
    id="results_table",
    columns=[
        {"name": "Year", "id": "Year", "type": "numeric"},
        {"name": "Change", "id": "Change", "type": "text"},
        {"name": "Median Household Income", "id": "Median Household Income", "type": "numeric", "format": {"specifier": "$,.0f"}},
        {"name": "Unemployment Rate", "id": "Unemployment Rate", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Median Housing Price", "id": "Median Housing Price", "type": "numeric", "format": {"specifier": "$,.0f"}},
        {"name": "Average Gas Price", "id": "Average Gas Price", "type": "numeric", "format": {"specifier": "$,.2f"}},
    ],
    page_size=15,
    data=df.to_dict("records"),
    style_table={"height": "300px", "overflowY": "auto"},
    style_header={
        'whiteSpace': 'normal',
        'height': 'auto',
        'lineHeight': '1.5',
        'textAlign': 'center',
    },
)



"""
==========================================================================
Figures
"""

def make_line_chart(dff, selected_indicator):
    start = int(dff.iloc[0]["Year"])  # start year
    end = int(dff.iloc[-1]["Year"])  # end year
    yrs = len(dff["Year"]) - 1
    dtick = 1 if yrs < 16 else 2 if yrs in range(16, 30) else 5

    fig = go.Figure()

    dff = dff.copy()

    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["Median Household Income"],
            name="Median Household Income",
            marker_color=COLORS["Median Household Income"],
            yaxis="y",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff[selected_indicator],
            name=selected_indicator,
            marker_color=COLORS.get(selected_indicator),
            yaxis="y2",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial",
                align="left",
                namelength=-1
            )
        )
    )

    indicator_ranges = {
        "Median Housing Price": {"yaxis2": {"range": [350000, 650000], "tickprefix": "$"}},
        "Unemployment Rate": {"yaxis2": {"range": [3.0, 9.0], "ticksuffix": "%", "tickformat": ".1f"}},
        "Average Gas Price": {"yaxis2": {"range": [2.00, 4.50], "tickprefix": "$", "tickformat": ".2f"}},
    }

    indicator_range = indicator_ranges[selected_indicator]

    fig.update_layout(
        title=f"Median Household Income vs. {selected_indicator} Trends ({start} - {end})",
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
            range=[75000, 87000],
            title_standoff=10,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial",
            align="left",
            namelength=-1
        ),
        yaxis2=dict(
            title=f"{selected_indicator}",
            overlaying="y",
            side="right",
            fixedrange=True,
            title_standoff=15,
            range=indicator_range['yaxis2']['range'],
            tickprefix=indicator_range['yaxis2'].get('tickprefix', ''),
            ticksuffix=indicator_range['yaxis2'].get('ticksuffix', ''),
            tickformat = indicator_range['yaxis2'].get('tickformat', ''),
        ),
        xaxis=dict(title="Years", fixedrange=True, dtick=dtick),
    )

    return fig


def make_bar_graph(dff, selected_indicator, year_range):
    start_year = year_range[0]
    end_year = year_range[1]

    df_start = dff[dff["Year"] == start_year]
    df_end = dff[dff["Year"] == end_year]

    indicator_start = df_start[selected_indicator].iloc[0] if not df_start.empty else None
    indicator_end = df_end[selected_indicator].iloc[0] if not df_end.empty else None

    fig = go.Figure(
        go.Bar(
            x=[f"{start_year}", f"{end_year}"],
            y=[indicator_start, indicator_end],
            name=f"{selected_indicator}",
            marker_color=COLORS.get(selected_indicator),
        )
    )

    indicator_ranges = {
        "Median Housing Price": {"yaxis": {"range": [0, 650000], "tickprefix": "$"}},
        "Unemployment Rate": {"yaxis": {"range": [0.0, 9.0], "ticksuffix": "%"}},
        "Average Gas Price": {"yaxis": {"range": [0.00, 5.00], "tickprefix": "$", "tickformat": ".2f"}},
    }

    indicator_range = indicator_ranges[selected_indicator]

    fig.update_layout(
        title=f"{selected_indicator} at {start_year} vs. {end_year}",
        template="none",
        showlegend=True,
        legend=dict(
            x=0.5,
            y=1.1,
            xanchor="center",
            yanchor="top",
            orientation="h",
        ),
        height=400,
        margin=dict(l=80, r=90, t=80, b=55),
        xaxis=dict(
            title="Year",
            tickvals=[start_year, end_year],
        ),
        yaxis=dict(
            title=selected_indicator,
            range = indicator_range['yaxis']['range'],
            tickprefix = indicator_range['yaxis'].get('tickprefix', ''),
            ticksuffix = indicator_range['yaxis'].get('ticksuffix', ''),
            tickformat = indicator_range['yaxis'].get('tickformat', ''),
        ),
        bargap=0.45,
        plot_bgcolor=COLORS["background"],

    )

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
            id="year_range_slider",
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

indicator_dropdown_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Select Indicator", className="card-title"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="indicator_dropdown",
                            options=[
                                {'label': 'Median Housing Price', 'value': 'Median Housing Price'},
                                {'label': 'Unemployment Rate', 'value': 'Unemployment Rate'},
                                {'label': 'Average Gas Price', 'value': 'Average Gas Price'}
                            ],
                            value="Median Housing Price",
                            style={"width": "100%"},
                        ),
                    ),
                ]
            )
        ]
    ),
    style={"width": "100%", "margin": "0 auto"}
)

results_card = dbc.Card(
    [
        dbc.CardHeader("Results"),
        html.Div(results_table),
    ],
    className="mt-4",
)

# ========= Build tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(
            [asset_allocation_card, slider_card, indicator_dropdown_card],
            id="tab-1",
            label="Play",
        ),
        dbc.Tab(
            [results_card],
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

app.layout = (
    dcc.Store("stored_data"),
    dbc.Container(
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
                        dcc.Graph(id="line_chart", className="mb-2"),
                        dcc.Graph(
                            id="bar_graph",
                            className="mb-2",
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center',
                                'width': '80%',
                                'margin': 'auto',
                            }
                        ),
                        html.Hr(),
                        dcc.Store(id="change_statement_store"),
                        html.Div([
                            html.B(id="change_statement"),
                            html.P("Note: There may have been fluctuations between these years.")
                        ], className="change-statement-container"),
                        html.Hr(),
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
))



"""
==========================================================================
Callbacks
"""


@app.callback(
    Output("line_chart", "figure"),
    [
        Input("indicator_dropdown", "value"),
        Input("year_range_slider", "value")
    ]
)
def update_line_graph(selected_indicator, year_range):
    df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_filtered["Year"],
            y=df_filtered["Median Household Income"],
            name="Median Household Income",
            marker_color=COLORS["Median Household Income"],
            yaxis="y",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_filtered["Year"],
            y=df_filtered[selected_indicator],
            name=selected_indicator,
            marker_color=COLORS.get(selected_indicator),
            yaxis="y2",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial",
                align="left",
                namelength=-1
            )
        )
    )

    indicator_ranges = {
        "Median Housing Price": {"yaxis2": {"range": [350000, 650000], "tickprefix": "$"}},
        "Unemployment Rate": {"yaxis2": {"range": [3.0, 9.0], "ticksuffix": "%"}},
        "Average Gas Price": {"yaxis2": {"range": [2.00, 4.50], "tickprefix": "$", "tickformat": ".2f"}},
    }

    indicator_range = indicator_ranges[selected_indicator]

    print(f"selected_indicator: {selected_indicator}")
    print(f"indicator_range: {indicator_range}")

    fig.update_layout(
        title=f"Median Household Income vs. {selected_indicator} Trends ({year_range[0]} - {year_range[1]})",
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
            range=[75000, 87000],
            title_standoff=10,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial",
            align="left",
            namelength=-1
        ),
        yaxis2=dict(
            title=f"{selected_indicator}",
            overlaying="y",
            side="right",
            fixedrange=True,
            title_standoff=15,
            range=indicator_range['yaxis2']['range'],
            tickprefix=indicator_range['yaxis2'].get('tickprefix', ''),
            ticksuffix=indicator_range['yaxis2'].get('ticksuffix', ''),
            tickformat=indicator_range['yaxis2'].get('tickformat', ''),
        ),
        xaxis=dict(title="Years", fixedrange=True, dtick=1),
        plot_bgcolor=COLORS["background"]
    )

    return fig


@app.callback(
    [
        Output("bar_graph", "figure"),
        Output("change_statement", "children")
    ],
    [
        Input("indicator_dropdown", "value"),
        Input("year_range_slider", "value")
    ]
)
def update_bar_graph(selected_indicator, year_range):
    df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

    start_value = df_filtered[df_filtered["Year"] == year_range[0]][selected_indicator].iloc[0]
    end_value = df_filtered[df_filtered["Year"] == year_range[1]][selected_indicator].iloc[0]

    fig = make_bar_graph(df, selected_indicator, year_range)

    change = end_value - start_value
    change_direction = "increased" if change > 0 else "decreased"
    change_value = abs(change)

    change_statement = (
        f"From {year_range[0]} to {year_range[1]}, {selected_indicator.lower()} {change_direction} by ${change_value:,.0f}."
        if selected_indicator == "Median Housing Price"
        else f"From {year_range[0]} to {year_range[1]}, {selected_indicator.lower()} {change_direction} by {change_value:.1f}%."
        if selected_indicator == "Unemployment Rate"
        else f"From {year_range[0]} to {year_range[1]}, {selected_indicator.lower()} {change_direction} by ${change_value:,.2f}."
        if selected_indicator == "Average Gas Price"
        else f"From {year_range[0]} to {year_range[1]}, {selected_indicator.lower()} {change_direction} by ${change_value:,.2f}."
    )

    return fig, change_statement


@app.callback(
    Output("results_table", "data"),
    Output("stored_data", "data"),
    [Input("year_range_slider", "value"),
     Input("indicator_dropdown", "value")],
    [State("stored_data", "data")]
)
def update_results_table(selected_range, selected_indicator, stored_data):
    min_year, max_year = selected_range
    df_filtered = df[(df["Year"] >= min_year) & (df["Year"] <= max_year)]

    start_value = df_filtered[df_filtered["Year"] == min_year][selected_indicator].values[0]
    end_value = df_filtered[df_filtered["Year"] == max_year][selected_indicator].values[0]

    change_value = end_value - start_value

    new_data = df_filtered.to_dict("records")

    for row in new_data:
        # format Change column based on selected indicator
        if selected_indicator == "Median Housing Price":
            row["Change"] = f"${change_value:,.0f}"
        elif selected_indicator == "Average Gas Price":
            row["Change"] = f"${change_value:,.2f}"
        elif selected_indicator == "Unemployment Rate":
            row["Change"] = f"{change_value:.1f}%"
            row["Unemployment Rate"] = f"{row['Unemployment Rate']:.1f}%"
        else:
            row["Change"] = f"{change_value:,.2f}"

        # always format Unemployment Rate as percentage, even if not the current indicator
        if row["Unemployment Rate"] and selected_indicator != "Unemployment Rate":
            row["Unemployment Rate"] = f"{row['Unemployment Rate']:.1f}%"

    if stored_data is None:
        stored_data = []

    combined_data = new_data + stored_data

    return combined_data, combined_data

if __name__ == '__main__':
    app.run(debug=True)






