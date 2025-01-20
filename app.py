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

st.sidebar.header('パラメータ設定')

# 銘柄番号の範囲設定
start_code = st.sidebar.number_input('開始銘柄番号', min_value=1000, max_value=9999, value=1000)
end_code = st.sidebar.number_input('終了銘柄番号', min_value=1000, max_value=9999, value=9999)

# 移動平均線の期間設定
ma_periods = st.sidebar.slider(
    '移動平均線の期間（週）',
    min_value=7,
    max_value=56,
    value=21
)

max_perV = st.sidebar.number_input('割合上限', min_value=0.5, max_value=100.0, value=100.0)
min_perV = st.sidebar.number_input('割合下限', min_value=0.5, max_value=100.0, value=1.1)

v_price = st.sidebar.number_input('購入単元株価上限', min_value=1, max_value=1000000, value=500)

def get_stock_price(stock_code):
  url = "https://minkabu.jp/stock/" + str(stock_code)
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")
  price = soup.find("div", class_="md_target_box_price").text
  return price

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')

today = datetime.datetime.now(JST)
start =  today - datetime.timedelta(weeks=24)
end = today

#st.set_option('deprecation.showPyplotGlobalUse', False)

yf.pdr_override()

df_code = pd.read_csv("data_j.csv")
code_list = []
code_list_only = []
dic_co = {}

st.title("銘柄抽出ツール")
st.text(f"以下の条件の銘柄を抽出する。番号とチャート図を表示する。最後にコード一覧を表示する。\n １．移動平均{ma_periods}日曲線が{min_perV}以上上昇傾向 \n ２．{v_price}円以下")

st.write(f"解析日：{today.date().strftime('%Y/%m/%d')}（現在日曜日はできない）")

def main():

    if st.button("解析スタート") == True:
        overwrite = st.empty()
        overwrite_2 = st.empty()
        overwrite_3 = st.empty()
        
        for code in df_code["コード"]:
            with overwrite.container():
                st.write("code",code)
            if (code > start_code and code < end_code):
                #print(df_code.query('コード == @code')["銘柄名"])
                code_name = df_code.query('コード == @code')["銘柄名"]
                #st.write(str(code)+".T:",code_name)
                #st.write(start)
                #st.write(end)
    
                df = pdr.get_data_yahoo(str(code)+".T",start,end)
                #df = yf.download(str(code)+".T",start,end)
                #st.write(">>>>>>>>")
                #st.write(df)
        
                df["SMA7"] = df["Close"].rolling(window=7).mean()
                df["SMA14"] = df["Close"].rolling(window=14).mean()
                df["SMA21"] = df["Close"].rolling(window=ma_periods).mean()
                sdiff = np.diff(df["Close"])
                sdiff_sign = ((sdiff[:-1] * sdiff[1:]) < 0) & (sdiff[:-1] > 0)
                #print(round(df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0],3),"\n")
                #st.write(len(df["SMA21"].tail(21)))
                #st.write(df)
                if len(df["SMA21"].tail(21)) >= 21:
                    #st.write("SMA21_2120>>")
                    #st.write(df["SMA21"].tail(21))
                    #st.write("SMA21_210")
                    #st.write(df["SMA21"].tail(21)[20])
                    #st.write(df["SMA21"].tail(21)[0])
                    #st.write(df["SMA21"].tail(21)[20]/df["SMA21"].tail(21)[0])
                    if (df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0] > min_perV and df["SMA21"].tail(21)[20] / df["SMA21"].tail(21)[0] < max_perV):
                        if df["Close"].tail(1)[0] < v_price:
                            st.write(str(code)+".T:",code_name)

#非推奨の記載のため書き換える。予備用に残す。
#                            plt.plot(df["SMA7"],label="SMA7")
#                            plt.plot(df["SMA14"],label="SMA14")
#                            plt.plot(df["SMA21"],label="SMA21")
#                            plt.plot(df["Close"],label="Close")
#                            plt.plot(df["Close"][1:-1][sdiff_sign],"o")
#                            plt.legend()
#                            plt.savefig(f"{code}_{code_name.values[0]}.jpg")
#                            st.pyplot(plt.show())
                            fig, ax = plt.subplots()
                            ax.plot(df.index, df["SMA7"], label="SMA7")
                            ax.plot(df.index, df["SMA14"], label="SMA14")
                            ax.plot(df.index, df["SMA21"], label=f"SMA{ma_periods}")
                            ax.plot(df.index, df["Close"], label="Close")
                            ax.scatter(df.index[1:-1][sdiff_sign], df["Close"][1:-1][sdiff_sign], label="Tpoint")
                            
                            ax.legend(loc='upper left')
                            plt.savefig(f"{code}_{code_name.values[0]}.jpg")
                            st.pyplot(fig)
                          
                            code_list.append([str(code)+".T:",code_name])
                            code_list_only.append(code)
                            dic_co[code]="株価："+str(df["Close"].tail(1)[0])+"円/"

        st.write(code_list)
        st.write(code_list_only)
        for cd in code_list_only:
            dic_co[cd] += "目標株価："+get_stock_price(cd)
        with overwrite_2.container():
            st.write(code_list_only)
        with overwrite_3.container():
            st.write(dic_co)
            

if __name__ == "__main__":
    main()
