from urllib.request import urlopen
import pandas as pd
import json
import dash
from dash import html, dcc
from datetime import datetime
from dateutil.relativedelta import relativedelta 
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go

now = datetime.now()
last_month_date = now + relativedelta(months=-12)
date_format = "%m/%d/%Y"
startDate = last_month_date.strftime(date_format)
endDate = datetime.today().strftime(date_format)
startDate, endDate = str(startDate), str(endDate)


url = f"https://www.treasurydirect.gov/TA_WS/securities/search?format=json&startDate={startDate}&endDate={endDate}&dateFieldName=auctionDate"

response = urlopen(url)
datajson = json.dumps(json.loads(response.read()))
data = pd.read_json(url)

# formatting date such that it is pickabe by dcc.datepicker_blabla
for column_name in ["issueDate","maturityDate","announcementDate","auctionDate"]:
    c = column_name.lower()
    if "date" in c:  
        data[column_name] = pd.to_datetime(data[column_name], format="%Y-%m-%dT%H:%M:%S")

bill_data = data.query("pricePer100 != '' and securityType == 'Bill'")
bill_data.sort_values("auctionDate", inplace=True)

bond_data = data.query("securityType == 'Bond'")
bond_data.sort_values("auctionDate", inplace=True)

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
                # menu filters for bill-chart
                html.Div(
                    children=[
                        html.Div(children="Bill Security Term", className="menu-title"),
                        dcc.Dropdown(
                            id="bill-security-term-filter",
                            options=[
                                {"label": bill_security_term, "value": bill_security_term}
                                for bill_security_term in np.sort(bill_data.securityTerm.unique())
                            ],
                            value="4-Week",
                            searchable=True,
                            clearable=False,
                            className="dropdown",
                        ),
                        html.Div(
                            children="Bill Issue Date",
                            className="menu-title",
                        ),
                        dcc.DatePickerRange(
                            id="bill-chart-issue-date-range",
                            min_date_allowed=bill_data.issueDate.min().date(),
                            max_date_allowed=bill_data.issueDate.max().date(),
                            start_date=bill_data.issueDate.min().date(),
                            end_date=bill_data.issueDate.max().date(),
                        ),
                        html.Div(
                            children="Auction Date",
                            className="menu-title",
                        ),
                        dcc.DatePickerRange(
                            id="bill-chart-auction-date-range",
                            min_date_allowed=bill_data.auctionDate.min().date(),
                            max_date_allowed=bill_data.auctionDate.max().date(),
                            start_date=bill_data.auctionDate.min().date(),
                            end_date=bill_data.auctionDate.max().date(),
                        ),
                        html.Div(
                            children="Maturity Date",
                            className="menu-title",
                        ),
                        dcc.DatePickerRange(
                            id="bill-chart-maturity-date-range",
                            min_date_allowed=bill_data.maturityDate.min().date(),
                            max_date_allowed=bill_data.maturityDate.max().date(),
                            start_date=bill_data.maturityDate.min().date(),
                            end_date=bill_data.maturityDate.max().date(),
                        ),
                    ],
                    className="menu",
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
                                            "hovertemplate": "$%{y:.6f}"
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
            ],
            className="wrapper",
        ),
        html.Div(
            children=[
                    html.Div(
                        children=[
                            html.Div(
                                children="Bond Issue Date",
                                className="menu-title",
                            ),
                            dcc.DatePickerRange(
                                id="bond-chart-issue-date-range",
                                min_date_allowed=bond_data.issueDate.min().date(),
                                max_date_allowed=bond_data.issueDate.max().date(),
                                start_date=bond_data.issueDate.min().date(),
                                end_date=bond_data.issueDate.max().date(),
                            ),
                            html.Div(
                                children="Bond Auction Date",
                                className="menu-title",
                            ),
                            dcc.DatePickerRange(
                                id="bond-chart-auction-date-range",
                                min_date_allowed=bond_data.auctionDate.min().date(),
                                max_date_allowed=bond_data.auctionDate.max().date(),
                                start_date=bond_data.auctionDate.min().date(),
                                end_date=bond_data.auctionDate.max().date(),
                            ),
                            html.Div(
                                children="Bond Maturity Date",
                                className="menu-title",
                            ),
                            dcc.DatePickerRange(
                                id="bond-chart-maturity-date-range",
                                min_date_allowed=bond_data.maturityDate.min().date(),
                                max_date_allowed=bond_data.maturityDate.max().date(),
                                start_date=bond_data.maturityDate.min().date(),
                                end_date=bond_data.maturityDate.max().date(),
                            ),
                        ],
                        className="menu",
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
                                            "type": "scatter",
                                            "hovertemplate": "$%{y:.2f} "
                                                            "<extra></extra>"
                                                            " matures on %{x} "
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
                     
            ],
            className="wrapper",
        ),
    ],
    className="jumbotron jumbotron-fluid",
)

@app.callback(
    [Output("bill-chart","figure"), Output("bond-chart","figure")],
    [
        # bills
        Input("bill-security-term-filter", "value"),

        Input("bill-chart-issue-date-range", "start_date"),
        Input("bill-chart-issue-date-range", "end_date"),

        Input("bill-chart-auction-date-range", "start_date"),
        Input("bill-chart-auction-date-range", "end_date"),
        
        Input("bill-chart-maturity-date-range", "start_date"),
        Input("bill-chart-maturity-date-range", "end_date"),

        # bonds

        Input("bond-chart-issue-date-range", "start_date"),
        Input("bond-chart-issue-date-range", "end_date"),

        Input("bond-chart-auction-date-range", "start_date"),
        Input("bond-chart-auction-date-range", "end_date"),
        
        Input("bond-chart-maturity-date-range", "start_date"),
        Input("bond-chart-maturity-date-range", "end_date"),

    ],
)
def update_charts(
    # bill
    bill_term_filter, 
    bill_issue_start_date, bill_issue_end_date, 
    bill_auction_start_date, bill_auction_end_date,
    bill_maturity_start_date, bill_maturity_end_date,

    # bond
    
    bond_issue_start_date, bond_issue_end_date,
    bond_auction_start_date, bond_auction_end_date,
    bond_maturity_start_date, bond_maturity_end_date
    ):
    billmask = (
        ( bill_data.securityTerm == bill_term_filter)
        & (bill_data.issueDate >= bill_issue_start_date)
        & ((bill_data.issueDate <= bill_issue_end_date))
        & (bill_data.auctionDate >= bill_auction_start_date)
        & ((bill_data.auctionDate <= bill_auction_end_date))
        & (bill_data.maturityDate >= bill_maturity_start_date)
        & ((bill_data.maturityDate <= bill_maturity_end_date))
    )
    filtered_bill_data = bill_data.loc[billmask, :]
    bill_chart_figure = {
                        "data": [
                            {
                                "x": filtered_bill_data["issueDate"],
                                "y": filtered_bill_data["pricePer100"],
                                "type": "lines",
                                "hovertemplate": "$%{y:.6f}"
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
        }
    
    bondmask = (
        
        (bond_data.issueDate >= bond_issue_start_date)
        & ((bond_data.issueDate <= bond_issue_end_date))
        & (bond_data.auctionDate >= bond_auction_start_date)
        & ((bond_data.auctionDate <= bond_auction_end_date))
        & (bond_data.maturityDate >= bond_maturity_start_date)
        & ((bond_data.maturityDate <= bond_maturity_end_date))
    )
    
    filtered_bond_data = bond_data.loc[bondmask, :]
    bond_chart_figure = {
                        "data": [
                            { 
                                "x": filtered_bond_data["securityTerm"],
                                "y": filtered_bond_data["interestRate"],
                                "type": "scatter",
                                "hovertemplate": "$%{y:.2f} "
                                                 "<extra></extra>"
                                                 " matures on %{x} "
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
    return bill_chart_figure, bond_chart_figure

if __name__ == "__main__":
    app.run_server(debug=True)