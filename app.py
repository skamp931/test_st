import time 
import streamlit as st
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import datetime
import random
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

def get_stock_price(stock_code):
  url = "https://minkabu.jp/stock/" + str(stock_code)
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")
  price = soup.find("div", class_="md_target_box_price").text
  return price

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')

today = datetime.datetime.now(JST)
#today = datetime.datetime.now()
start =  today - datetime.timedelta(weeks=24)
end = today

st.set_option('deprecation.showPyplotGlobalUse', False)

yf.pdr_override()

df_code = pd.read_csv("data_j.csv")
code_list = []
code_list_only = []

st.title("銘柄抽出ツール")
st.text("以下の条件の銘柄を抽出する。番号とチャート図を表示する。最後にコード一覧を表示する。\n １．移動平均21日曲線が1割以上上昇傾向 \n ２．500円以下")

st.write(f"解析日：{today.date().strftime('%Y/%m/%d')}（現在日曜日はできない）")

def main():

    if st.button("解析スタート") == True:
        overwrite = st.empty()
        overwrite_2 = st.empty()
        overwrite_3 = st.empty()
        
        for code in df_code["コード"]:
            with overwrite.container():
                st.write("code",code)
            if (code > 100 and code < 2000):
                #print(df_code.query('コード == @code')["銘柄名"])
                code_name = df_code.query('コード == @code')["銘柄名"]
                print(str(code)+".T:",code_name)
    
                df = pdr.get_data_yahoo(str(code)+".T",start,end)
        
                df["SMA7"] = df["Close"].rolling(window=7).mean()
                df["SMA14"] = df["Close"].rolling(window=14).mean()
                df["SMA21"] = df["Close"].rolling(window=21).mean()
                sdiff = np.diff(df["Close"])
                sdiff_sign = ((sdiff[:-1] * sdiff[1:]) < 0) & (sdiff[:-1] > 0)
                #print(round(df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0],3),"\n")

                if len(df["SMA21"].tail(21)) >= 21:

                    if df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0] > 1.1:
            
                        if df["Close"].tail(1)[0] < 500:
                            st.write(str(code)+".T:",code_name)

                            plt.plot(df["SMA7"],label="SMA7")
                            plt.plot(df["SMA14"],label="SMA14")
                            plt.plot(df["SMA21"],label="SMA21")
                            plt.plot(df["Close"],label="Close")
                            plt.plot(df["Close"][1:-1][sdiff_sign],"o")
            
                            plt.legend()
                            plt.savefig(f"{code}_{code_name.values[0]}.jpg")
                            st.pyplot(plt.show())
                            code_list.append([str(code)+".T:",code_name])
                            code_list_only.append(code)
    
        st.write(code_list)
        dic_co = {}
        for cd in code_list_only:
            dic_co[cd]=get_stock_price(cd)
        with overwrite_2.container():
            st.write(code_list_only)
        with overwrite_3.container():
            st.write(dic_co)
            

if __name__ == "__main__":
    main()
