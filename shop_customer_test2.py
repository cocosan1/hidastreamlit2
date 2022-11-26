import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value
import datetime

from gsheetsdb import connect
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title='顧客管理')
st.markdown('#### 顧客管理')

SP_CREDENTIAL_FILE = '/content/drive/MyDrive/Colab Notebooks/shop/customer-test-369800-4dea3886b081.json'
SP_COPE = [
    'https://www.googleapis.com/auth/drive',
    'https://spreadsheets.google.com/feeds'  
]
SP_SHHET_KEY = '1jHgWlYF1sEoyFuY2ogV8BYltOiFJPO-YHf9deK5manI' #gssheetsのid URLのdの後
SP_SHEET = 'フォームの回答 1'

# Credentials 情報を取得
credentials = service_account.Credentials.from_service_account_info( \
        st.secrets["gcp_service_account"], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ],
)
conn = connect(credentials=credentials)
def run_query(query): 
    rows = conn.execute(query, headers=1) 
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
# データフレームに変換し表示する
row_list = []
for row in rows: row_list.append(row)
df_now=pd.DataFrame(row_list)

# ***ファイルアップロード 過去実績***
uploaded_file_past = st.sidebar.file_uploader('実績', type='xlsx', key='now')
df_past = DataFrame()
if uploaded_file_past:
    df_past = pd.read_excel(
        uploaded_file_past, sheet_name='受注委託移動在庫生産照会', usecols=[1, 3, 7, 8, 10, 14, 15, 16, 43, 44],\
            index_col=0)  # index　ナンバー不要　index_col=0
else:
    st.info('実績のファイルを選択してください。')
    st.stop()

#int化
df_past[['数量', '単価', '金額']] = df_past[['数量', '単価', '金額']].fillna(0).astype('int')

# 氏名からスペースの削除
df_now['氏名2'] = df_now['氏名'].map(lambda x: x.replace('\u3000', '')) #全角スペース削除
df_now['氏名2'] = df_now['氏名'].map(lambda x: x.replace(' ', ''))    

# 氏名からスペースの削除
df_past['得意先名2'] = df_past['得意先名'].map(lambda x: x.replace('\u3000', '')) #全角スペース削除
df_past['得意先名2'] = df_past['得意先名'].map(lambda x: x.replace(' ', '')) #半角スペース削除

def select_customer():
    name = st.text_input('氏名 ※スペースなし')
    df_now2 = df_now[df_now['氏名2']==name]
    df_past2 =df_past[df_past['得意先名2']==name]
    df_past2 = df_past2.sort_values('受注日')

    col1, col2, col3 = st.columns(3)
    with col1:
        total_sum = str(df_past2['金額'].sum())
        st.metric('購入金額', value=total_sum) 
    with col2:
        buy_count= df_past2['受注日'].nunique()
        st.metric('購入回数', value=buy_count) 
    with col3:
        min_date = str(df_past2['受注日'].min())
        min_date = min_date.split(' ')[0]
        st.write('初回購入日') 
        st.write(min_date)

    st.caption('来店情報')
    st.table(df_now2)
    st.caption('購入履歴')
    st.table(df_past2)







def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'お客様情報の抽出': select_customer,
        
    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))
    link = '[home](http://linkpagetest.s3-website-ap-northeast-1.amazonaws.com/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.caption('homeに戻る')                                       

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

if __name__ == '__main__':
    main()