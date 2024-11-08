from urllib.request import urlopen
import urllib.request
import pandas as pd
import json
import dash
from dash import html, dcc
from datetime import datetime
from dateutil.relativedelta import relativedelta 
from dash.dependencies import Output, Input
import random
from functions import *


now = datetime.now()
last_month_date = now + relativedelta(weeks=-8)
date_format = "%m/%d/%Y"
startDate = last_month_date.strftime(date_format)
endDate = (datetime.now() + relativedelta(weeks=6)).strftime(date_format)
startDate, endDate = str(startDate), str(endDate)


url = f"https://www.treasurydirect.gov/TA_WS/securities/search?format=json&startDate={startDate}&endDate={endDate}&dateFieldName=issueDate"
req = urllib.request.Request(url)
# Customize the default User-Agent header value:

u = str(random.randint(50000,100000))
req.add_header("ngrok-skip-browser-warning",  u)
response = urlopen(req)

datajson = json.dumps(json.loads(response.read()))
data = pd.read_json(url)

# formatting date such that it is pickabe by dcc.datepicker_blabla
for column_name in ["issueDate","maturityDate","announcementDate","auctionDate"]:
    c = column_name.lower()
    if "date" in c:  
        data[column_name] = pd.to_datetime(data[column_name], format="%Y-%m-%dT%H:%M:%S")

bill_data = data.query("pricePer100 != '' and securityType == 'Bill'")
bill_fig = get_bill_figure(bill_data)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
# bill_fig.update_layout(clickmode='event+select')



bond_data = data.query("securityType == 'Bond'")
bond_data.sort_values("auctionDate", inplace=True)
bond_data_figure = get_bond_figure(bond_data=bond_data)
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Treasury Securities Analytics: A Decision Tool in the Purhcase of Treasury Bill Secrities"

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
                                figure=bill_fig,
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
                                figure=bond_data_figure
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
        # Input("bill-security-term-filter", "value"),

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
    # bill_term_filter, 
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
        

    
    
    filtered_bill_data = filtered_bill_data.sort_values("securityTerm")

    filtered_bill_fig = get_bill_figure(filtered_bill_data)
   
    
    bondmask = (
        
        (bond_data.issueDate >= bond_issue_start_date)
        & ((bond_data.issueDate <= bond_issue_end_date))
        & (bond_data.auctionDate >= bond_auction_start_date)
        & ((bond_data.auctionDate <= bond_auction_end_date))
        & (bond_data.maturityDate >= bond_maturity_start_date)
        & ((bond_data.maturityDate <= bond_maturity_end_date))
    )
    
    filtered_bond_data = bond_data.loc[bondmask, :]
    bond_chart_figure = get_bond_figure(bond_data=filtered_bond_data)
    return filtered_bill_fig, bond_chart_figure

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8050, debug=True)