import http.client
import json
from airflow import DAG
from datetime import datetime
import pandas as pd
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine

# define the function to create a DAG
# code snippet to extract data provided by Alpha Van tage API
# extraction function to get stock data for Microsoft (MSFT)
def extract_stock_data():
    conn = http.client.HTTPSConnection("alpha-vantage.p.rapidapi.com")
    headers = {
        'x-rapidapi-key':"rapid_api_key",
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
    }
    conn.request("GET", "/query?function=TIME_SERIES_DAILY&symbol=MSFT&outputsize=compact&datatype=json", headers=headers)
    res = conn.getresponse()
    data = res.read()    
    # Parse JSON instead of just printing
    return json.loads(data.decode("utf-8"))

def transform_stock_data():
    # 1. Get data from extract function
    raw_data = extract_stock_data()
    # 2. Extract time series data
    time_series = raw_data['Time Series (Daily)']
    # 3. Transform to list of records
    transformed_data = []
    for date, values in time_series.items():
        record = {
            'date': date,
            'symbol': 'MSFT',
            'open_price': float(values['1. open']),
            'high_price': float(values['2. high']),
            'low_price': float(values['3. low']),
            'close_price': float(values['4. close']),
            'volume': int(values['5. volume']),
            'price_change': None,  # Calculate later
            'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        transformed_data.append(record)
    
    return transformed_data

def load_stock_data():
    """Load transformed data into MySQL database"""
    # Change localhost to host.docker.internal for Docker on Windows
    connection_string = "mysql+mysqlconnector://root:password@host.docker.internal:3306/stock_data"
    # Rest of your code stays the same
    data = transform_stock_data()
    df = pd.DataFrame(data)
    engine = create_engine(connection_string)
    df.to_sql(
        name='stock_prices',
        con=engine,
        if_exists='append',
        index=False
    )
    print(f"Loaded {len(df)} records to MySQL")
    
# Define the DAG
with DAG("my_dag", start_date=datetime(2025, 6, 16), schedule_interval="@daily", catchup=False) as dag:
        # Define the tasks using PythonOperator
    extract_task = PythonOperator(
        task_id='extract_stock_data',
        python_callable=extract_stock_data
    )
    transform_task = PythonOperator(
        task_id='transform_stock_data',
        python_callable=transform_stock_data
    )
    load_task = PythonOperator(
        task_id='load_stock_data',
        python_callable=load_stock_data
    )

    # Set task dependencies
    extract_task >> transform_task >> load_task


    


    
