# -*- coding: utf-8 -*-
import io
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context, MATCH
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
)

##Data ingestion

df_all_homes = pd.read_csv("Assets/All_homes.csv")
df_all_items = pd.read_csv("Assets/All_items.csv")
df_apparel = pd.read_csv("Assets/Apparel.csv")
df_food_at_home = pd.read_csv("Assets/Food_at_home.csv")
df_gasoline = pd.read_csv("Assets/Gasoline.csv")
df_median_income = pd.read_csv("Assets/Median_income.csv")
df_medical_care = pd.read_csv("Assets/Medical_care.csv")
df_used_cars = pd.read_csv("Assets/Used_cars.csv")

data_frames = [
    (df_all_homes, "All homes"),
    (df_all_items, "All items"),
    (df_apparel, "Apparel"),
    (df_food_at_home, "Food at home"),
    (df_gasoline, "Gasoline"),
    (df_median_income, "Median income"),
    (df_medical_care, "Medical care"),
    (df_used_cars, "Used Cars"),
]
#merges all csvs- combines all years, new column for each csv "annual" column
#files with multiple values for one year are averaged
processed_dfs = [
    (
        df_object
        .groupby("Year", as_index = False) ["Annual"].mean()
        .assign(Year=lambda d: pd.to_numeric(d["Year"], errors="coerce"))
        .rename(columns = {"Annual": new_column})
        .dropna(subset=["Year"])
        .set_index("Year")
    )
    for df_object, new_column in data_frames
]

df_merged = pd.concat(processed_dfs, axis =1, join="outer")
df_merged.sort_index(inplace=True)
df = df_merged
df.index.name="Year"
records = df.to_dict("records")
df_reset= df.reset_index()
df_reset["Year"]=df_reset["Year"].astype(str)
# print(df_reset.head())


"""
==========================================================================
Markdown Text
"""
#change this
datasource_text = dcc.Markdown(
    """
    Data source: See Learn Tab for Details
    """
)


learn_text = dcc.Markdown(
    """
    This is an investigation of Cost of living in Colorado, specifically the capital, Denver. The average cost of living 
    from 2023 data is approximately 53,000 dollars per person per year. This puts the state about 12% above the average COL in the country. 
    Use the tools to investigate if you have what it takes to live in such a highly desired location!
    
    In the "Change of cost of Goods over time"
    graph, there is a "Consumer Price Index" (price index) specified for the y axis. This value is displaying the percent change in cost of
    goods over time. Since the index is 100 at year 1982, a value of 150 on the y-axis indicates a 50% increase in price since 1982 This is helpful to see
    the effect of inflation over time, as is relevant to climbing costs in our current economy.
    
    The values on the income slider were determined by the difference between the real median value in 2023 and 2023 minimum wage salary. 
    The "in between" values are given by (median - min. wage/2) + previous value. This provides evenly spaced income values to look at.
    The median and min. wage values have not changed dramatically since 2023. 2023 data was used for consistency.
    
    Article Citation
    “What Is the Cost of Living in Colorado?” Unbiased, 
    www.unbiased.com/discover/banking/what-is-the-cost-of-living-in-colorado. Accessed 24 Mar. 2025. 

    Data Sources Used
    
    [Consumer Price Index for All Urban Consumers: Used Cars and Trucks in U.S. City Average from Federal Reserve Bank of St. Louis
    ](https://fred.stlouisfed.org/series/CUSR0000SETA02)
    
    [All-Transactions House Price Index for Colorado from Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/COSTHPI)
    
    [Real Median Household Income in Colorado from Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/series/MEHOINUSCOA672N)
    
    [All items in Denver-Aurora-Lakewood, CO, all urban consumers, not seasonally adjusted from U.S. Bureau of Statistics](https://www.bls.gov/regions/mountain-plains/news-release/consumerpriceindex_denver.htm)
    
    [Gasoline (all types) in Denver-Aurora-Lakewood, CO, all urban consumers, not seasonally adjusted ](https://data.bls.gov/timeseries/CUURS48BSETB01?amp%253bdata_tool=XGtable&output_view=data&include_graphs=true)
    
    [Medical care in Denver-Aurora-Lakewood, CO, all urban consumers, not seasonally adjusted](https://data.bls.gov/timeseries/CUURS48BSAM?amp%253bdata_tool=XGtable&output_view=data&include_graphs=true)
    
    [Food at home in Denver-Aurora-Lakewood, CO, all urban consumers, not seasonally adjusted](https://www.bls.gov/regions/mountain-plains/news-release/consumerpriceindex_denver.htm)
    
    [Apparel in Denver-Aurora-Lakewood, CO, all urban consumers, not seasonally adjusted](https://www.bls.gov/regions/mountain-plains/news-release/consumerpriceindex_denver.htm)
    """
)

footer = html.Div(
    dcc.Markdown(
        """
         This information is intended solely as general information for educational
        and entertainment purposes only and is not a substitute for professional advice and
        services from qualified financial services providers familiar with your financial
        situation.    
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

"""
==========================================================================
Figures
"""

#first addition.
def make_checkbox_graph1(graph1, df, series_options, default_series):
   return html.Div([
       dcc.Checklist(
           id={"type": "data-checklist", "index": graph1},
           options=[{"label": s, "value":s} for s in series_options],
           value=default_series,
           labelStyle={"display": "inline-block", "margin-right": "10px"}
       ),
       dcc.Graph(id={"type": "line-graph", "index": graph1}),
       dcc.Store(id={"type": "data-store", "index": graph1},
            data=df.to_json(date_format="iso", orient="split"))
   ], style={"border": "1px solid #ccc", "padding": "10px", "margin": "10px"})

checkbox_graph_component = make_checkbox_graph1(
    graph1="first_checkbox",
    df=df,
    series_options=df.columns.tolist(),
    default_series=["All homes"]
)

"""
==========================================================================
Make Tabs
"""
# =======Play tab components

income_values = {
    "Minimum Wage (28000)": 28000,
    "In between (62500):": 62500,
    "Median Income (97000)": 97000,
    "In between (131500)": 131500,
    "High Income (166000)": 166000
}


slider_card = dbc.Card(
    [
        html.H4("Choose a general income level", className="card-title"),
        dcc.Slider(
            id="income-slider",
            marks={i: key for i, key in enumerate(income_values.keys())},
            min=0,
            max=4,
            step=1,
            value=2,
            included=False,
            updatemode = "mouseup"
        ),
    ],
    body=True,
    className="mt-4",
)

# ======= InputGroup components

estimated_income = dbc.InputGroup(
    [
        dbc.InputGroupText("Estimated Annual Income $"),
        dbc.Input(
            id="estimated_income",
            placeholder="Enter your income",
            type="number",
            min=10,
            value=50000,
        ),
    ],
    className="mb-3",
)
estimated_expense1 = dbc.InputGroup(
    [
        dbc.InputGroupText("Estimated Groceries Expense"),
        dbc.Input(
            id="estimated_cost1",
            placeholder=f"yearly food cost",
            type="number",
            min=0,
            value=100,
        ),
    ],
)
estimated_expense2 = dbc.InputGroup(
    [
        dbc.InputGroupText("Estimated Gasoline Expense"),
        dbc.Input(
            id="estimated_cost2",
            placeholder=f"yearly food cost",
            type="number",
            min=0,
            value=100,
        ),
    ],
)
estimated_expense3 = dbc.InputGroup(
    [
        dbc.InputGroupText("Estimated Rent/House Payment"),
        dbc.Input(
            id="estimated_cost3",
            placeholder=f"yearly food cost",
            type="number",
            min=0,
            value=100,
        ),
    ],
)
estimated_expense4 = dbc.InputGroup(
    [
        dbc.InputGroupText("Tuition payment"),
        dbc.Input(
            id="estimated_cost4",
            placeholder=f"yearly food cost",
            type="number",
            min=0,
            value=100,
        ),
    ],
)
estimated_expense5 = dbc.InputGroup(
    [
        dbc.InputGroupText("Other Necessary Expenses"),
        dbc.Input(
            id="estimated_cost5",
            placeholder=f"yearly food cost",
            type="number",
            min=0,
            value=100,
        ),
    ],
    className="mb-3",
)

#maybe edit this later so user inputs monthly costs and it computes it for them

input_groups = html.Div(
    [estimated_income, estimated_expense1, estimated_expense2, estimated_expense3, estimated_expense4, estimated_expense5],
    className="mt-4 p-4",
)

# ========= Learn Tab  Components
learn_card = dbc.Card(
    [
        dbc.CardHeader("An Introduction to Asset Allocation"),
        dbc.CardBody(learn_text),
    ],
    className="mt-4",
)

# ======== Raw Data Tab Components
Raw_data = dbc.Card(
    [
        dbc.CardHeader("Here is the aggregated raw data"),
        dbc.CardBody(
            dash_table.DataTable(
                id ="raw-data",
                columns=[{"name": col, "id": col} for col in df_reset.columns],
                data=df_reset.to_dict("records"),
                page_size=20,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "5px", "color": "blue"},
                style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"}
            )
        ),
    ],
    className = "mt-4",
)

# ========= Build tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
        dbc.Tab(
            [slider_card, html.Div("Enter Estimated Monthly Values for Expenses Below",style={"border":"1px solid blue", "display": "block", "minHeight": "40px", "marginTop":"30px !important", "marginBottom":"20px", "fontSize":"24px", "textAlign": "center"
                        }),
                    input_groups],
            tab_id="tab-2",
            label="Play",
            className="pb-4",
        ),
        dbc.Tab( [Raw_data],
            tab_id = "tab-4",
            label = "Data Table"
        ),
    ],
    id="tabs",
    active_tab="tab-2",
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
                    html.H2(
                        "Exploring Cost of Living In Colorado",
                        className="text-center bg-primary text-white p-2",
                    ),
                ),
        ),
        dbc.Row(
            dbc.Col(
                html.H4(
                    "Amelia Ubben - CS150: Community Action Computing",
                    className = "text-center bg-primary text-white p-2",
                ),
            ),
        ),
        dbc.Row(
            [
                dbc.Col(
                    tabs, width=12, lg=5, className="mt-4 border"
                ),
                dbc.Col(
                    [
                        html.Hr(),
                        html.Div(id="summary_table"),
                        html.H6(datasource_text, className="my-2"),

                        dcc.Graph(id="income-bar-graph"),
                        dcc.Graph(id="personal-bar-graph"),

                    ],
                    width=12,
                    lg=7,
                    className="pt-4",
                ),
                dbc.Col(
                    [

                        checkbox_graph_component,
                    ],
                    width=12
                )
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

#for user input
@app.callback(
    Output("personal-bar-graph", "figure"),
    [Input("estimated_income", "value"),
     Input("estimated_cost1", "value"),
     Input("estimated_cost2", "value"),
     Input("estimated_cost3", "value"),
     Input("estimated_cost4", "value"),
     Input("estimated_cost5", "value")]
)
def update_personal_graph(estimated_income, cost1, cost2, cost3, cost4, cost5):

    est_income = (estimated_income if estimated_income is not None else 0) / 12
    total_cost = (
        (cost1 if cost1 is not None else 0) +
        (cost2 if cost2 is not None else 0) +
        (cost3 if cost3 is not None else 0) +
        (cost4 if cost4 is not None else 0) +
        (cost5 if cost5 is not None else 0)
    )

    fig = go.Figure(data=[
        go.Bar(
            x=["Income"],
            y=[est_income],
            name="Estimated Income",
         #   marker_color="blue"
        ),
        go.Bar(
            x=["Cost of Living"],
            y=[total_cost],
            name="Estimated COL",
          #  marker_color="red"
        )
    ])
    fig.update_layout(
        title="Your Monthly Income vs. Monthly Expenses",
        xaxis_title = "Category",
        yaxis_title="Amount ($)",
        barmode= "group",
        title_x=0.5
    )
    return fig

#checkbox graphs
@app.callback(
    Output({"type": "line-graph", "index": MATCH}, "figure"),
    Input({"type": "data-checklist", "index": MATCH}, "value"),
    Input({"type": "data-store", "index": MATCH}, "data")
)

def update_checkbox_graph(selected_series, stored_data):
    if stored_data is None or not selected_series:
        return go.Figure()

    df_from_store = pd.read_json(io.StringIO(stored_data), orient="split")
    traces=[
        go.Scatter(
            x=df_from_store.index,
            y=df_from_store[series],
            mode="lines+markers",
            name=series
        )
        for series in selected_series
    ]
    fig = go.Figure(data=traces)
    fig.update_layout(
        title="Change in Cost of Goods over Time",
        xaxis_title="Year",
        yaxis_title="Index Value (1982-84=100)"
    )
    return fig

#for the slider graphs
@app.callback(
    Output("income-bar-graph", "figure"),
    Input("income-slider", "value")
)
def update_slider_bar(selected_index):
    income_keys = list(income_values.keys())
    selected_key = income_keys[selected_index]
    selected_income = income_values[selected_key]

    median_income = income_values["Median Income (97000)"]

    fig = go.Figure(data=[
        go.Bar(
            x=["Selected Income"],
            y=[selected_income],
            name=selected_key,
          #  marker_color = "blue"
        ),
        go.Bar(
            x=["Median Income"],
            y=[median_income],
            name="Median Income",
           # marker_color= "orange"
        )
    ])

    target_value = 53000
    fig.add_shape(
        type="line",
        xref="paper",
        x0=0,
        x1=1,
        yref="y",
        y0=target_value,
        y1=target_value,
        line=dict(color= "Purple", width=2, dash="dash")
    )

    fig.update_layout(
        annotations=[
            dict(
                x=1,
                y=target_value,
                xref="paper",
                yref="y",
                text="Average Cost of Living in 2023",
                showarrow=False,
                font=dict(color="Purple", size=12),
                xanchor="right",
                yanchor="bottom"
            )
        ],
        title = f"Income Comparison: {selected_key} vs. Median Income",
        xaxis_title = "Category",
        yaxis_title= "Income ($)",
        barmode="group",
        title_x=0.5
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
