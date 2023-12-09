import time 
import streamlit as st
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import datetime
import random
import matplotlib.pyplot as plt
import numpy as np

today = datetime.datetime(2023,12,9)
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

    print("3770.T")
        #print(df_code.query('コード == @code')["銘柄名"])
    #code_name = df_code.query('コード == @code')["銘柄名"]

    df = pdr.get_data_yahoo("3770.T",start,end)

    df["SMA7"] = df["Close"].rolling(window=7).mean()
    df["SMA14"] = df["Close"].rolling(window=14).mean()
    df["SMA21"] = df["Close"].rolling(window=21).mean()
    sdiff = np.diff(df["Close"])
    sdiff_sign = ((sdiff[:-1] * sdiff[1:]) < 0) & (sdiff[:-1] > 0)
    #print(round(df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0],3),"\n")

    if df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0] > 1.1:

        if df["Close"].tail(1)[0] < 500:
            plt.plot(df["SMA7"],label="SMA7")
            plt.plot(df["SMA14"],label="SMA14")
            plt.plot(df["SMA21"],label="SMA21")
            plt.plot(df["Close"],label="Close")
            plt.plot(df["Close"][1:-1][sdiff_sign],"o")

            plt.legend()
            #plt.savefig(f"{code}_{code_name.values[0]}.jpg")
            st.pyplot(plt.show())


    
    st.balloons()

if __name__ == "__main__":
    main()
