from logging import debug
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析（得意先別一覧）')
st.markdown('#### 売り上げ分析（得意先別一覧）')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')


# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])
else:
    st.info('前期のファイルを選択してください。')
    st.stop()

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

def earnings_comparison():
    customer_list = df_now['得意先名'].unique()

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

def earnings_comparison_month():
    # *** selectbox 得意先名***
    month = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    option_month = st.selectbox(
    '受注月:',
    month,   
) 
    customer_list = df_now['得意先名'].unique()

    index = []
    earnings_now = []
    earnings_last = []
    comparison_rate = []
    comparison_diff = []

    df_now_month = df_now[df_now['受注月']==option_month]
    df_last_month = df_last[df_last['受注月']==option_month]

    for customer in customer_list:
        index.append(customer)
        cust_earnings_total_now_month = df_now_month[df_now_month['得意先名']==customer]['金額'].sum()
        cust_earnings_total_last_month = df_last_month[df_last_month['得意先名']==customer]['金額'].sum()
        earnings_rate_culc = f'{cust_earnings_total_now_month/cust_earnings_total_last_month *100: 0.1f} %'
        comaparison_diff_culc = cust_earnings_total_now_month - cust_earnings_total_last_month

        earnings_now.append(cust_earnings_total_now_month)
        earnings_last.append(cust_earnings_total_last_month)
        comparison_rate.append(earnings_rate_culc)
        comparison_diff.append(comaparison_diff_culc)
    earnings_comparison_list = pd.DataFrame(list(zip(earnings_now, earnings_last, comparison_rate, comparison_diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])    
    st.dataframe(earnings_comparison_list)


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

    st.write('構成比')
    df_earnings_list = pd.DataFrame(list(zip(l_comp, d_comp, o_comp)), index=index, columns=['L', 'D', 'その他'])
    st.dataframe(df_earnings_list)

def hokkaido_fiushi_kokusan_comp(): #作成中
    customer_list = df_now['得意先名'].unique()

    index = []
    hokkaido = [] #北海道売り上げ
    hokkaido_comp = [] #北海道比率

    fushi = [] #節売り上げ
    fushi_comp = [] #節比率

    kokusan = [] #国産売り上げ
    kokusan_comp = [] #国産比率

    for customer in customer_list:
        index.append(customer)

        df_now_cust = df_now[df_now['得意先名']==customer]

        df_now_cust_sum = df_now_cust['金額'].sum() #得意先売り上げ合計

        now_cust_sum_h = df_now_cust[df_now_cust['出荷倉庫']==510]['金額'].sum()
        hokkaido.append('{:,}'.format(now_cust_sum_h))
        hokkaido_comp_culc = f'{now_cust_sum_h/df_now_cust_sum*100:0.1f} %'
        hokkaido_comp.append(hokkaido_comp_culc)

        now_cust_sum_fushi = df_now_cust[df_now_cust['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        fushi.append('{:,}'.format(now_cust_sum_fushi))
        fushi_comp_culc = f'{now_cust_sum_fushi/df_now_cust_sum*100:0.1f} %'
        fushi_comp.append(fushi_comp_culc)

        now_cust_sum_kokusan = df_now_cust[df_now_cust['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum()
        kokusan.append('{:,}'.format(now_cust_sum_kokusan))
        kokusan_comp_culc = f'{now_cust_sum_kokusan/df_now_cust_sum*100:0.1f} %'
        kokusan_comp.append(kokusan_comp_culc)

    st.write('構成比')
    df_comp_list = pd.DataFrame(list(zip(hokkaido_comp, fushi_comp, kokusan_comp)), index=index, columns=['北海道工場', '節材', '国産材'])
    st.dataframe(df_comp_list, width=2000)

def profit_aroma():
    customer_list = df_now['得意先名'].unique()

    index = []
    profit = [] #粗利
    profit_ratio = [] #粗利率

    aroma = [] #アロマ売り上げ

    for customer in customer_list:
        index.append(customer)

        df_now_cust = df_now[df_now['得意先名']==customer]

        df_now_cust_sum = df_now_cust['金額'].sum() #得意先売り上げ合計

        now_cust_sum_profit = df_now_cust['原価金額'].sum()
        profit_ratio_culc = f'{(df_now_cust_sum - now_cust_sum_profit)/df_now_cust_sum*100:0.1f} %'
        profit_ratio.append(profit_ratio_culc)

        now_cust_sum_aroma = df_now_cust[df_now_cust['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        aroma.append('{:,}'.format(now_cust_sum_aroma))

    df_comp_list = pd.DataFrame(list(zip(profit_ratio, aroma)), index=index, columns=['粗利率', 'きつつきの森研究所'])
    st.dataframe(df_comp_list)
            

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '売上/前年比(累計)●': earnings_comparison,
        '売上/前年比(月毎)●': earnings_comparison_month,
        '構成比 LD●': ld_earnings_comp,
        '構成比 北海道/節/国産●': hokkaido_fiushi_kokusan_comp,
        '比率 粗利/アロマ関連●': profit_aroma,
        
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