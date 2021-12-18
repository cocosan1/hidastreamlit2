from logging import debug
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析（得意先別）')
st.title('売り上げ分析（得意先別一覧）')

# ***ファイルアップロード 今期***
st.subheader('今期のエクセルファイルを読み込ませてください')

uploaded_file_now = st.file_uploader('Choose a XLSX file', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    st.markdown('---')
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0

# ***ファイルアップロード　前期***
st.subheader('前期のエクセルファイルを読み込ませてください')

uploaded_file_last = st.file_uploader('Choose a XLSX file', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    st.markdown('---')
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

def ld_earnings_comp():
    customer_list = df_now['得意先名'].unique()

    index = []
    l_earnings = [] #リニング売り上げ
    l_comp = [] #リビング比率

    d_earnings = [] #ダイニング売り上げ
    d_comp = [] #ダイニング比率

    o_earnings = [] #その他売り上げ
    o_comp = [] #その他比率

    for customer in customer_list:
        index.append(customer)

        df_now_cust = df_now[df_now['得意先名']==customer]

        df_now_cust_sum = df_now_cust['金額'].sum() #得意先売り上げ合計

        df_now_cust_sum_l = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        l_earnings.append('{:,}'.format(df_now_cust_sum_l))
        l_comp_culc = f'{df_now_cust_sum_l/df_now_cust_sum*100:0.1f} %'
        l_comp.append(l_comp_culc)

        df_now_cust_sum_d = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        d_earnings.append('{:,}'.format(df_now_cust_sum_d))
        d_comp_culc = f'{df_now_cust_sum_d/df_now_cust_sum*100:0.1f} %'
        d_comp.append(d_comp_culc)

        df_now_cust_sum_o = df_now_cust[df_now_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子', 'デスク', '小物・その他'])]['金額'].sum()
        o_earnings.append('{:,}'.format(df_now_cust_sum_o))
        o_comp_culc = f'{df_now_cust_sum_o/df_now_cust_sum*100:0.1f} %'
        o_comp.append(o_comp_culc)

    df_earnings_list = pd.DataFrame(list(zip(l_earnings, l_comp, d_earnings, d_comp, o_earnings, o_comp)), index=index, columns=['金額(L)', '構成比(L)', '金額(D)', '構成比(D)', '金額(その他)', '構成比（その他）'])
    st.dataframe(df_earnings_list)

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'LD　売り上げ/構成比': ld_earnings_comp,
        
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