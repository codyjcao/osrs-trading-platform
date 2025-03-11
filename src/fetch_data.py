import requests
import json

from pathlib import Path
from typing import Optional

import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

from osrsbox import items_api

items = items_api.load()

col_names = ['name','last_updated','cost']
items_df = pd.DataFrame(columns=col_names)

for item in items:
    if item.tradeable_on_ge and not item.noted:
        items_df.loc[item.id] = (item.name,item.last_updated,item.cost)


common_trade_idx_url = "https://oldschool.runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Common_Trade_Index"

html = requests.get(common_trade_idx_url).content

df_index = pd.DataFrame((pd.read_html(html)[0])['Item.1'])
df_index = df_index.rename({'Item.1':'name'},axis=1)

df_index['id'] = df_index['name'].apply(lambda x:items_df.index[items_df['name'] == x][0])



'''
data:
    item database - items_api library every week
    market data - osrs grand exchange api every week? month?
        parameters:
            - 6h
            - CTI items


functions:
    - read data from csv files (temporary)
    - read data from database
    - update data
        - read in new data (every week)

'''


def call_http_historical_prices(item_id: int = 1,time_interval: str = '24h'):
    headers = {
        'User-Agent': 'Trading Strategy Platform - @funkeryiffic on Discord',
        'From': 'email@gmail.com'
    }
    response = requests.get(f'https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep={time_interval}&id={item_id}',headers=headers)
    stats = json.loads(response.text)
    return stats


def create_price_df(item_id: int,time_interval: str = '6h') -> Optional[pd.DataFrame]:
    # Pull data from the runescape api
    jsonData = call_http_historical_prices(item_id,time_interval)
    
    # Load the data into a dataframe
    data = pd.DataFrame(jsonData)
    
    # No data available
    if data.shape[0] == 0:
        raise HistoricalDataNotFound('This item id has no historical data available')

    # Some missing data
    if data.shape[0] < 365:
        print(f'DataFrame has fewer than 365 rows; some data may be missing: {item_id}')

    data['index_id'] = np.arange(len(data))
    temp = data['data']
    res = pd.json_normalize(temp)
    res['id'] = item_id
    
    return res

def fetch_price_data(time_interval: str, items_list: list) -> Optional[pd.DataFrame]:
    # To store all of the dataframes
    df_list = []
    
    # Loop through the desired items list
    for item_id in items_list:
        try:
            df_list.append(create_price_df(item_id, time_interval))
        except Exception as e:
            print(f"Skipping item {item_id} due to error: {e}")
    
    if not df_list:
        print('No data was collected. Skipping file creation')
        return None
    
    return pd.concat(df_list,ignore_index=True)

def create_new_price_file(time_interval: str = '6h',filepath: Optional[str] = None, items_list: Optional[list] = None, overwrite: bool = False):
    # Set filepath if not specified
    if filepath is None:
        filepath = Path(f'Master Files/price_file_{time_interval}.csv')
    else:
        filepath = Path(filepath)
        
    if items_list is None:
        items_list = df_index['id'].values
    
    # Check that our filepath doesn't already exist, exit if it does
    if filepath.exists():
        print(f'{filepath} already exists')
        if not overwrite:
            print(f'Set `overwrite=True` to overwrite')
            return
        print(f'Overwriting {filepath}')
    else:
        # Create folders if necessary based on the specified filepath
        filepath.parent.mkdir(parents=True, exist_ok=True)

    # Combine all of the dataframes into one large dataframe
    df_combined = fetch_price_data(time_interval,items_list)
    df_combined.to_csv(filepath)
    print(f'New file saved to {filepath}')
        

def update_price_file_csv(time_interval: str,filepath: Optional[str] = None):
    if filepath is None:
        filepath = Path(f'Master Files/price_file_{time_interval}.csv')
    else:
        filepath = Path(filepath)
    
    try:
        df = pd.read_csv(filepath,index_col = 0)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return None
    except pd.errors.ParserError:
        print(f"[ERROR] Unable to parse CSV file: {filepath}")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return None
        
    item_list = list(df['id'].unique())
    
    df_to_add = fetch_price_data(time_interval,item_list)
    
    df_combined = pd.concat([df, df_to_add]).drop_duplicates().sort_values(by=['id','timestamp']).reset_index(drop=True)
    
    
    df_combined.to_csv(filepath)
    print(f'{filepath} has been updated')
    

'''
TODO:

- come up with a default naming convention for file system on hard drive?
    - do away with this once database is fully functioning
    
- write an update file function that writes to database

'''
