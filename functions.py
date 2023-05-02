

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd




def single_term_to_days(term_str: str) -> int:
    """
        Takes a string in the format of XX-TIME that can be seperated by spaces 
        the convert that to days
    """

    if is_valid_security_term(term_str) is False:
        return 0
    
    term_str = term_str.strip()  
    term_str = term_str.lower()
    days = 0
    if ' ' not in term_str:
        t = term_str.split('-')
        n = int(t[0])
        if "week" in t[1]:
            n *= 7
        elif "month" in t[1]:
            n *= (365 // 12)
        elif "year" in t[1]:
            n *= 365
        days += n
    return days

def multi_term_to_days(term_str: str) -> int:
    if ' ' not in term_str:
        return single_term_to_days(term_str)
    days = 0
    for token in term_str.split():
        if is_valid_security_term(token) == False:
            return 0
        else:
            days += single_term_to_days(token)
    return days

def is_valid_security_term(term_str: str) -> bool:
    if term_str is None:
        return False
    x = str(term_str)
    if len(x) == 0:
        return False
    x = term_str.strip()  
    term_str = x.lower()
    if " " in term_str:
        return False
    tokens = term_str.split("-")
    if len(tokens) != 2:
        #print(f"Bad tokens length. Expected 2 but got {len(tokens)} : {tokens}")
        return False
    if tokens[0].isnumeric() == False:
        #print(f"expected numeric at position 0 got {tokens[0]}")
        return False

    if is_day_week_month_year(tokens[1]) == False:
        #print(f"expected day(s), week(s), month(s) or year(s) bt got {tokens[1]}")
        return False
    
    if int(tokens[0]) == 0 :
        #print(f"expected an integer at positon 0 but got {tokens[0]}")
        return False
    
    return True



def is_day_week_month_year(s: str) -> bool:
    if s is None:
        return False
    if len(str(s)) == 0:
        return False
    s = s.lower()
    if s == "day" or s == "days":
        return True
    if s == "week" or s == "weeks":
        return True
    if s == "month" or s == "months":
        return True
    if s == "year" or s == "years":
        return True
    return False



def get_bill_figure(bill_data: pd.DataFrame):
    if bill_data is None :
        return None
    
    bill_data['pricePer100'] = bill_data['pricePer100'].astype(float)
    
    bill_data['profitPer100'] = 100.0 - bill_data['pricePer100'].astype(float)
    
    bill_data['profitPer100'] = bill_data['profitPer100'].round(decimals = 3)
        
    bill_data['daysInYear'] = bill_data['securityTerm'].map(multi_term_to_days)
    bill_data['term_apr'] = bill_data['pricePer100'].map(lambda x: (100-x)/x)
    bill_data['terms_per_year'] = bill_data['daysInYear'].map(lambda x: 365.0 / float(x))
    bill_data['annual_revenue'] = (1.0 + bill_data['terms_per_year'].astype(float)*bill_data['profitPer100'].astype(float) )
    #bill_data['annual_revenue'] = bill_data['multiplier'] * bill_data['profitPer100']
    p = bill_data[['cusip','issueDate','securityTerm','terms_per_year']]
    print("bill data columns \n", p.columns.to_list())
    print("bill data head \n", p.head())
    #df = df.groupby(['securityTerm','issueDate']).count()['profitPer100'].unstack()
    
    bill_data = bill_data.sort_values("annual_revenue")
    
    bill_data['terms_per_year'] = bill_data['terms_per_year'].round(decimals = 3)
    bill_fig = px.scatter(bill_data, x="securityTerm", y="annual_revenue", symbol='terms_per_year')

    return bill_fig
    
    

