import time 
import streamlit as st
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import datetime
import random
import matplotlib.pyplot as plt
import numpy as np

today = datetime.datetime(2023,12,1)
#today = datetime.datetime.now()
start =  today - datetime.timedelta(weeks=24)
end = today

yf.pdr_override()

def main():
    status_area = st.empty()

    count_down_sec = 3
    for i in range(count_down_sec):
        status_area.write(f"{count_down_sec -i}sec left")

        time.sleep(1)
    
    status_area.write("Done!"+f"{end}")
    
    st.balloons()

if __name__ == "__main__":
    main()
