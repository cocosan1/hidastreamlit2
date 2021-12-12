import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='test')
st.title('得意先別売り上げ分析')

# ***ファイルアップロード 今期***
st.subheader('今期のエクセルファイルを読み込ませてください')

uploaded_file_now = st.file_uploader('Choose a XLSX file', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    st.markdown('---')
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52], index_col=0)

# ***ファイルアップロード　前期***
st.subheader('前期のエクセルファイルを読み込ませてください')

uploaded_file_last = st.file_uploader('Choose a XLSX file', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    st.markdown('---')
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52], index_col=0)

# *** 出荷月、受注月列の追加***
df_now['出荷月'] = df_now['出荷日'].dt.month
df_now['受注月'] = df_now['受注日'].dt.month
df_last['出荷月'] = df_last['出荷日'].dt.month
df_last['受注月'] = df_last['受注日'].dt.month

# ***INT型への変更***
df_now[['数量', '単価', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_now[['数量', '単価', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_last[['数量', '単価', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_last[['数量', '単価', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

def cust_earnings_comparison():
    # *** selectbox 得意先名***
    customer = df_now.index.unique()
    option_customer = st.selectbox(
        '得意先名:',
        customer,   
    ) 
    st.write('選択した得意先名: ', option_customer)

    df_now2 = pd.pivot_table(df_now, values='金額', index='得意先名', columns='受注月', aggfunc='sum')
    df_now2['合計'] = df_now2.sum(axis=1)
    #test
    df_now2 = df_now2.fillna(0).astype('int64')

    df_last2 = pd.pivot_table(df_last, values='金額', index='得意先名', columns='受注月', aggfunc='sum')
    df_last2['合計'] = df_last2.sum(axis=1)
    #test
    df_last2 = df_last2.fillna(0).astype('int64')

    df_now3 = df_now2.loc[option_customer, :]
    # df_last3 = df_last2.loc[option_customer]

    # df_total = pd.concat([df_now3, df_last3], axis=1)
    # df_total.columns = ['今期', '前期']
    # df_total['前年比'] = (df_total['今期']/df_total['前期']).round(4).map('{:.1%}'.format)

    st.dataframe(df_now3)



def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '得意先別売り上げ　対前年比': cust_earnings_comparison,
        
    }
    selected_app_name = st.sidebar.selectbox(label='得意先の選択',
                                             options=list(apps.keys()))

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

if __name__ == '__main__':
    main()