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
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 文字列をアルファベットを0に置き換える関数
def replace_alphabets_with_zero(input_string):
    # リスト内包表記で文字ごとにチェックし、条件に応じて置き換え
    result = ''.join(['0' if char.isalpha() else char for char in input_string])
    return result

def get_stock_price(stock_code):
  url = "https://minkabu.jp/stock/" + str(stock_code)
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")
  price = soup.find("div", class_="md_target_box_price").text
  return price

def save_to_google_sheet(data):
    # Google APIの認証情報を設定
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    st.write("Google API認証に成功しました。")
    
    # スプレッドシートを開く
    spreadsheet = client.open_by_key("1ygFHusEfP5st8SzQVcfs_F4kO8xXupiSh6oVYdX-JWk")
    st.write("スプレッドシートを開きました。")
    
    # 今日の日付と時分秒を含むシートを追加
    sheet_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
    st.write(f"新しいシート '{sheet_name}' を追加しました。")
    
    # ヘッダー行を追加
    header = ["銘柄コード", "株価", "目標株価（みんかぶ）"]
    worksheet.append_row(header)
    
    # データを文字列に変換し、数値データは整数に変換
    data_as_strings = [
        [str(item) if isinstance(item, str) else str(int(float(item))) for item in row]
        for row in data
    ]
    # データを保存
    worksheet.append_rows(data_as_strings)
    st.write("データを保存しました。")

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


t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')

today = datetime.datetime.now(JST)
start =  today - datetime.timedelta(weeks=24)
end = today

#st.set_option('deprecation.showPyplotGlobalUse', False)

yf.pdr_override()

df_code = pd.read_csv("meigara/data_j_20250120.csv")
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
            
            if (int(replace_alphabets_with_zero(code)) > start_code and 
                int(replace_alphabets_with_zero(code)) < end_code):
                #print(df_code.query('コード == @code')["銘柄名"])
                code_name = df_code.query('コード == @code')["銘柄名"]
                #st.write(str(code)+".T:",code_name)
                #st.write(start)
                #st.write(end)
                try:
                    df = pdr.get_data_yahoo(str(code)+".T",start,end)
                except KeyError:
                    st.write(f"Ticker {ticker} not found in the data.")
                except Exception as e:
                    print(f"An error occurred: {e}")
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
        
        st.session_state.data = dic_co


if __name__ == "__main__":
    main()

# 保存ボタン
if st.button("結果を保存"):
    if st.session_state.data:
        for data in st.session_state.data:
            st.write(data)
        st.write("保存を開始します。")
        save_to_google_sheet(st.session_state.data)
        st.success("データがGoogleスプレッドシートに保存されました。")
    else:
        st.error("データがありません。最初にデータを取得してください。")
