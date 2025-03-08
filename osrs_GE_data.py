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


def call_http_historical_prices(item_id = 1,interval = '24h'):
    headers = {
        'User-Agent': 'Trading Strategy Platform - @funkeryiffic on Discord',
        'From': 'email@gmail.com'
    }
    response = requests.get(f'https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep={interval}&id={item_id}',headers=headers)
    stats = json.loads(response.text)
    return stats


def create_price_df(item_id,interval='6h'):
    jsonData = call_http_historical_prices(item_id,interval)
    data = pd.DataFrame(jsonData)
    if data.shape[0] == 0:
        raise HistoricalDataNotFound('This item id has no historical data available')

    if data.shape[0] < 365:
        print(f'DataFrame has fewer than 365 rows; some data may be missing: {item_id}')

    data['index_id'] = np.arange(len(data))
    temp = data['data']
    res = pd.json_normalize(temp)
    
    res['id'] = item_id
    return res


def read_master_file_csv(time_interval: str = '6h', filepath: Optional[str] = None) -> Optional[pd.DataFrame]:
    # Define file path if not provided
    if filepath is None:
        filepath = Path(f'Master Files/master_file_{time_interval}.csv')

    # Attempt to read the CSV
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return None
    except pd.errors.ParserError:
        print(f"[ERROR] Unable to parse CSV file: {filepath}")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return None

    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Set MultiIndex on ['id', 'date']
    df.set_index(['id', 'date'], inplace=True)

    # Ensure datetime index has frequency only if inferred
    inferred_freq = df.index.levels[1].inferred_freq
    if inferred_freq:
        df.index = df.index.set_levels(pd.DatetimeIndex(df.index.levels[1].values, freq=inferred_freq), level=1)

    # Fill missing values
    df.fillna(0, inplace=True)

    # Return sorted DataFrame
    return df.sort_index()
    


