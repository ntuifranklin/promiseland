





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




