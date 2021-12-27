from logging import debug
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析（TIF 一覧）')
st.markdown('#### 売り上げ分析（TIF 一覧）')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0

# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])

# *** 出荷月、受注月列の追加***
df_now['出荷月'] = df_now['出荷日'].dt.month
df_now['受注月'] = df_now['受注日'].dt.month
df_last['出荷月'] = df_last['出荷日'].dt.month
df_last['受注月'] = df_last['受注日'].dt.month

# ***INT型への変更***
df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

df_now_total = df_now['金額'].sum()
df_last_total = df_last['金額'].sum()

def original_ratio():
    customer_list = df_now['得意先名'].unique()

    index = []
    original_now = []
    original_last = []
    original_rate_now = []
    original_rate_last = []
    original_rate__diff = []

    for customer in customer_list:
        index.append(customer)
        df_now_cust = df_now[df_now['得意先名']==customer]
        df_last_cust = df_last[df_last['得意先名']==customer]
        cust_total_now = df_now_cust['金額'].sum()
        cust_total_last = df_last_cust['金額'].sum()
        original_now_culc = df_now_cust[df_now_cust['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        original_last_culc = df_last_cust[df_last_cust['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        original_rate_now_culc = f'{(original_now_culc / cust_total_now)*100: 0.1f} %'
        original_rate_last_culc = f'{(original_last_culc / cust_total_last)*100: 0.1f} %'
        original_rate_diff_culc = f'{((original_now_culc / cust_total_now) - (original_last_culc / cust_total_last))*100: 0.1f} %'
        
        original_now.append('{:,}'.format(original_now_culc))
        original_last.append('{:,}'.format(original_last_culc))
        original_rate_now.append(original_rate_now_culc)
        original_rate_last.append(original_rate_last_culc)
        original_rate__diff.append(original_rate_diff_culc)
        
    original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
    st.markdown('###### オリジナル比率')   
    st.dataframe(original_rate_list)

def original_series_category_earnings():
    # *** selectbox シリーズ***
    series = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
    option_series = st.selectbox(
        'series:',
        series,   
    ) 
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    )
    customer_list = df_now['得意先名'].unique()
    months = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    df_now_series = df_now[df_now['シリーズ名']==option_series]
    df_now_series_cate = df_now_series[df_now_series['商品分類名2']==option_category]
    
    sum_now = []
    df_result = pd.DataFrame(index=customer_list)

    for month in months:
        for customer in customer_list:
            df_now_series_cate_cust = df_now_series_cate[df_now_series_cate['得意先名']==customer]
            sum_month = df_now_series_cate_cust[df_now_series_cate_cust['受注月']==month]['金額'].sum()
            sum_now.append('{:,}'.format(sum_month))
        df_result[month] = sum_now
        sum_now = []
    st.caption('今期売上')
    st.table(df_result)

def original_category_series_earnings():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    )
    # *** selectbox シリーズ***
    series = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
    option_series = st.selectbox(
        'series:',
        series,   
    ) 
    customer_list = df_now['得意先名'].unique()
    months = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    df_now_cate = df_now[df_now['商品分類名2']==option_category]
    df_now_cate_series = df_now_cate[df_now_cate['シリーズ名']==option_series]
    
    sum_now = []
    df_result = pd.DataFrame(index=customer_list)

    for month in months:
        for customer in customer_list:
            df_now_cate_series_cust = df_now_cate_series[df_now_cate_series['得意先名']==customer]
            sum_month = df_now_cate_series_cust[df_now_cate_series_cust['受注月']==month]['金額'].sum()
            sum_now.append('{:,}'.format(sum_month))
        df_result[month] = sum_now
        sum_now = []
    st.caption('今期売上')
    st.table(df_result)






            

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'オリジナル比率●': original_ratio,
        'オリジナル売上 店舗別/シリーズベース': original_series_category_earnings,
        'オリジナル売上 店舗別/商品分類ベース': original_category_series_earnings,

        
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