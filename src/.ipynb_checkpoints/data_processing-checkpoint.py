import numpy as np
import pandas as pd
from typing import Optional

def process(df):
    # forward fill price data if any values are missing
    df["price"] = df["price"].fillna(method="ffill")
    
    # fill NA volume data with 0's
    df['highPriceVolume'] = df['highPriceVolume'].fillna(0)
    df['lowPriceVolume'] = df['lowPriceVolume'].fillna(0)
    
    # convert timestamp to datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'],unit='s')
    
    # compute VWAP
    df['VWAP'] = compute_VWAP(df['avgLowPrice'],df['avgHighPrice'],
                              df['lowPriceVolume'],df['highPriceVolume'])
    
    # compute 1 day forward returns
    df['return_1df'] = compute_returns(df['VWAP'],4,True)

    
    # compute 1 week forward returns
    df['return_1wf'] = compute_returns(df['VWAP'],4*7,True)
    


def compute_VWAP(lowPrice,highPrice,lowVolume,highVolume):
    # Compute volume weighter average price
    num = lowPrice*lowVolume + highPrice*highVolume
    den = lowVolume + highVolume
    return num/den


def compute_returns(VWAP,period_offset:int,forward:bool=False):
    # forward - computes the forward returns (to be used for training)
    if forward:
        return (VWAP.shift(-period_offset)/VWAP) - 1
    return (VWAP/VWAP.shift(period_offset)) - 1


def compute_SMA(price,window):
    return pd.Series(price).rolling(window=window).mean()


def compute_EMA(price,span):
    return pd.Series(price).ewm(span=span,adjust=False).mean()


def _helper_RSI(x):
    if x[x>0].shape[0]:
        avgU = x[x>0].mean()
    else:
        avgU = 0

    if x[x<0].shape[0]:
        avgD = abs(x[x<0].mean())
    else:
        return 100
    RS = avgU/avgD
    return 100 - ( 100 / (1 + RS) )


def compute_RSI(price:pd.Series,window:int):
    diff = price.diff()
    return diff.rolling(window=window).apply(_helper_RSI)

def compute_spread(low,high,VWAP):
    return (high-low)/VWAP
