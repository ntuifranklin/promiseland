from urllib.request import urlopen
import urllib.request
import pandas as pd
import json
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta 
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import random
from functions import *

now = datetime.now()
past_date = now + relativedelta(days=-14)
next_week = now + relativedelta(days=56)
date_format = "%m/%d/%Y"
next_week = next_week.strftime(date_format)
today = now.strftime(date_format)
today, next_week  = str(today) , str(next_week)
startDate = past_date.strftime(date_format)
endDate = datetime.today().strftime(date_format)
startDate, endDate = str(startDate), str(endDate)

url = f"https://www.treasurydirect.gov/TA_WS/securities/search?format=json&startDate={startDate}&endDate={next_week}&dateFieldName=issueDate"
bill_url = f"https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&type=Bill"
req = urllib.request.Request(url)
bill_request = urllib.request.Request(bill_url)
# Customize the default User-Agent header value:

u = str(random.randint(50000,100000))
req.add_header("ngrok-skip-browser-warning",  u)
response = urlopen(req)
# bill_response = urlopen(bill_request)
datajson = json.dumps(json.loads(response.read()))
# bill_data_json = json.dumps(json.loads(bill_response.read()))
# bill_data = pd.read_json(bill_data_json)
data = pd.read_json(url)
data['daysInYear'] = data['securityTerm'].map(multi_term_to_days)
bill_data = data.query("securityType == 'Bill' and pricePer100 != '' ")
# bill_data['daysInYear'] = bill_data['securityTerm'].map(multi_term_to_days)
# formatting date such that it is pickabe by dcc.datepicker_blabla
for column_name in ["issueDate","maturityDate","announcementDate","auctionDate"]:
    c = column_name.lower()
    if "date" in c:  
        data[column_name] = pd.to_datetime(data[column_name], format="%Y-%m-%dT%H:%M:%S")
        bill_data[column_name] = pd.to_datetime(bill_data[column_name], format="%Y-%m-%dT%H:%M:%S")

bill_data.sort_values("auctionDate", inplace=True)

bond_data = data.query("securityType == 'Bond'")
bond_data.sort_values("auctionDate", inplace=True)
bill_data['term_apr'] = bill_data['pricePer100'].map(lambda x: (100.0-float(x))/float(x))
bill_data['terms_per_year'] = bill_data['daysInYear'].map(lambda x: 365.0 / float(x))
bill_data['multiplier'] = (1.0 + bill_data['term_apr'].astype(float) )
bill_data['final_annual_multiplier'] = bill_data['multiplier'].pow( bill_data['terms_per_year'] )
bill_data['annual_revenue'] = bill_data['final_annual_multiplier'].astype(float) * bill_data['pricePer100'].astype(float)
bill_fig = px.bar(bill_data, x="securityTerm", y="annual_revenue", color="pricePer100", barmode="group")
external_stylesheets=[dbc.themes.LUX]

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
                        f" this will mainly include treasury bills and bonds "
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
                        
                        html.Div(
                            children="Issue Date",
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
                                            "x": bill_data["securityTerm"],
                                            "y": bill_data["annual_revenue"],
                                            "type": "bar",
                                            "hovertemplate": "%{y}"
                                                                "<extra></extra>"
                                        },

                                    ],
                                    "layout": {
                                        "title": {
                                            "text": "Treasury Bills Price",
                                            "x": 0.5,
                                            "xanchor": "left",
                                        },
                                        "xaxis": {"fixedrange": True},
                                        "yaxis": {
                                            #"tickprefix": "",
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
                                            "x": 0.005,
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
        #Input("bill-security-term-filter", "value"),

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
    #bill_term_filter, 
    bill_issue_start_date, bill_issue_end_date, 
    bill_auction_start_date, bill_auction_end_date,
    bill_maturity_start_date, bill_maturity_end_date,

    # bond
    
    bond_issue_start_date, bond_issue_end_date,
    bond_auction_start_date, bond_auction_end_date,
    bond_maturity_start_date, bond_maturity_end_date
    ):
    billmask = (
        # ( bill_data.securityTerm == bill_term_filter) &
        (bill_data.issueDate >= bill_issue_start_date)
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
                                "x": filtered_bill_data["securityTerm"],
                                "y": filtered_bill_data["annual_revenue"],
                                "type": "bar",
                                "hovertemplate": "%{y}"
                                                    "<extra></extra>"
                            },

                        ],
                        "layout": {
                            "title": {
                                "text": "Treasury Bills Price",
                                "x": 0.5,
                                "xanchor": "left",
                            },
                            "xaxis": {"fixedrange": True},
                            "yaxis": {
                                #"tickprefix": "$",
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
    # if on production do 
    # app.run_server(host='0.0.0.0', port=9090, debug=True)
    app.run_server(port=8899, debug=True)