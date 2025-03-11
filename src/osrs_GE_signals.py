import pandas as pd
import numpy as np

import osrs_GE_data
from typing import Optional




'''
Technical Analysis indicator computation
'''

def VWAP(lowPrice,highPrice,lowVolume,highVolume):
    # Compute volume weighter average price
    num = lowPrice*lowVolume + highPrice*highVolume
    den = lowVolume + highVolume
    return num/den


