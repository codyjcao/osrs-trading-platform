import numpy as np
import pandas as pd


def preprocess(df):
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

