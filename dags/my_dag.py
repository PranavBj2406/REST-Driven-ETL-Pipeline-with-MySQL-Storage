import http.client
import json
from airflow import DAG
from datetime import datetime
import pandas as pd
# define the function to create a DAG
# code snippet to extract data provided by Alpha Van tage API
# extraction function to get stock data for Microsoft (MSFT)
def extract_stock_data():
    conn = http.client.HTTPSConnection("alpha-vantage.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "f9a11114fbmsh1cd218885c221b4p133d14jsn6429510f088b",
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
    }
    
    conn.request("GET", "/query?function=TIME_SERIES_DAILY&symbol=MSFT&outputsize=compact&datatype=json", headers=headers)
    
    res = conn.getresponse()
    data = res.read()    
    # Parse JSON instead of just printing
    return json.loads(data.decode("utf-8"))

def transform_stock_data():
    
    pass

def load_stock_data():
    # Placeholder for loading logic
    pass

 