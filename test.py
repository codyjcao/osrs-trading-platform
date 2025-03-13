import src.fetch_data as fd
import src.data_processing as dp

import numpy as np
import pandas as pd


if __name__ == '__main__':
    fd.update_price_file_csv('6h')
    
    df_raw = fd.load_raw_price_file('6h')
    
    df = dp.process(df_raw)
    
    print(df.head())