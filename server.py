from urllib.request import urlopen
import pandas as pd
import json
import dash
from dash import html, dcc
from datetime import datetime
from dateutil.relativedelta import relativedelta 

now = datetime.now()
last_month_date = now + relativedelta(months=-6)
date_format = "%m/%d/%Y"
startDate = last_month_date.strftime(date_format)
endDate = datetime.today().strftime(date_format)
startDate, endDate = str(startDate), str(endDate)


url = f"https://www.treasurydirect.gov/TA_WS/securities/search?format=json&startDate={startDate}&endDate={endDate}&dateFieldName=issueDate"

response = urlopen(url)
datajson = json.dumps(json.loads(response.read()))
data = pd.read_json(url)
bill_data = data.query("pricePer100 != '' and securityType == 'Bill'")
bill_data.sort_values("issueDate", inplace=True)

bond_data = data.query("securityType == 'Bond'")
bond_data.sort_values("securityTerm", inplace=True)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Treasury Analytics: The Promise Land of Treasury Securities !"
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                    html.P(children="💵",className="header-emoji"),
                    html.H1(children="Treasury Security analytics", className="header-title"),
                    html.P(
                        children=f"analysze the behavior of Treasury Securities"
                        f" this will mainly include treasury bills"
                        f" between {startDate} and {endDate}",
                        className="header-description",
                    ),

            ],
            className="header",
        ),
        html.Div(
            children=[
                dcc.Graph(
                        id="bill-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": bill_data["issueDate"],
                                    "y": bill_data["pricePer100"],
                                    "type": "lines",
                                    "hovertemplate": "$%{y:.2f}"
                                                        "<extra></extra>"
                                },

                            ],
                            "layout": {
                                "title": {
                                    "text": "Treasury Bills Price",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True},
                                "yaxis": {
                                    "tickprefix": "$",
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"],
                            },
                        },
                    ),
            ],
            className="card",
        ),
        html.Div(
            children=[
                     dcc.Graph(
                            id="bond-chart",
                            config={"displayModeBar": True},
                            figure={
                                "data": [
                                    {
                                        "x": bond_data["securityTerm"],
                                        "y": bond_data["interestRate"],
                                        "type": "lines",
                                        "hovertemplate": "$%{y:.2f}"
                                                            "<extra></extra>"
                                    },
                                ],
                                "layout": {
                                    "title": {
                                        "text": "Treasury Bonds Price and Interest Rate",
                                        "x": 0.05,
                                        "xanchor": "left",
                                    },
                                    "xaxis" : {"fixedrange": True},
                                    "yaxis": {
                                        "tickprefix": "$",
                                        "fixedrange": True,
                                    },
                                    
                                }
                            }
                        )
            ],
            className="card",
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)