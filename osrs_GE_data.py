import requests
import json

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


'''
data:
    item database - items_api library every week
    market data - osrs grand exchange api every week? month?
'''


def call_http_historical_prices(item_id = 1,interval = '24h'):
    headers = {
        'User-Agent': 'Trading Strategy Platform - @funkeryiffic on Discord',
        'From': 'email@gmail.com'
    }
    response = requests.get('https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep={1}&id={0}'.format(item_id,interval),headers=headers)
    stats = json.loads(response.text)
    return stats


def create_price_df(item_id,interval='24h'):
    jsonData = call_http_historical_prices(item_id,interval)
    data = pd.DataFrame(jsonData)
    if data.shape[0] == 0:
        raise HistoricalDataNotFound('This item id has no historical data available')

    if data.shape[0] < 365:
        print("DataFrame has fewer than 365 rows; some data may be missing: ", item_id)

    data['index_id'] = np.arange(len(data))
    temp = data['data']
    res = pd.json_normalize(temp)
    
    res['id'] = item_id
    return res
