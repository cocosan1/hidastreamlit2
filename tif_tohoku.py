from logging import debug
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.elements import metric
# from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析（TIF 一覧）')
st.markdown('#### 売り上げ分析（TIF 東北）')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[1, 3, 6, 9, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')

# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[1, 3, 6, 9, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])
else:
    st.info('前期のファイルを選択してください。')
    st.stop()

# *** 出荷月、受注月列の追加***
df_now['出荷月'] = df_now['出荷日'].dt.month
df_now['受注月'] = df_now['受注日'].dt.month
df_last['出荷月'] = df_last['出荷日'].dt.month
df_last['受注月'] = df_last['受注日'].dt.month
df_now['商品コード2'] = df_now['商品コード'].map(lambda x: x.split()[0])
df_last['商品コード2'] = df_last['商品コード'].map(lambda x: x.split()[0])

# ***INT型への変更***
df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

df_now_total = df_now['金額'].sum()
df_last_total = df_last['金額'].sum()

def earnings_comparison():
    customer_list = ['㈱東京ｲﾝﾃﾘｱ 下田店', '㈱東京ｲﾝﾃﾘｱ 郡山店', '㈱東京ｲﾝﾃﾘｱ 山形店', '㈱東京ｲﾝﾃﾘｱ 秋田店', '㈱東京ｲﾝﾃﾘｱ 盛岡店',\
        '㈱東京ｲﾝﾃﾘｱ 仙台港本店', '㈱東京ｲﾝﾃﾘｱ 仙台泉店', '㈱東京ｲﾝﾃﾘｱ 仙台南店', '㈱東京ｲﾝﾃﾘｱ 福島店']

    index = []
    earnings_now = []
    earnings_last = []
    comparison_rate = []
    comparison_diff = []

    for customer in customer_list:
        index.append(customer)
        cust_earnings_total_now = df_now[df_now['得意先名']==customer]['金額'].sum()
        cust_earnings_total_last = df_last[df_last['得意先名']==customer]['金額'].sum()
        earnings_rate_culc = f'{cust_earnings_total_now/cust_earnings_total_last*100: 0.1f} %'
        comaparison_diff_culc = cust_earnings_total_now - cust_earnings_total_last

        earnings_now.append(cust_earnings_total_now)
        earnings_last.append(cust_earnings_total_last)
        comparison_rate.append(earnings_rate_culc)
        comparison_diff.append(comaparison_diff_culc)
    earnings_comparison_list = pd.DataFrame(list(zip(earnings_now, earnings_last, comparison_rate, comparison_diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])    
    st.dataframe(earnings_comparison_list)










def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '売上: 累計': earnings_comparison,
 
    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    link = '[home](http://linkpagetest.s3-website-ap-northeast-1.amazonaws.com/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.caption('homeに戻る')    

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

if __name__ == '__main__':
    main()