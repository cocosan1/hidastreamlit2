from logging import debug
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
# from streamlit.state.session_state import Value
import math

st.set_page_config(page_title='売り上げ分析（エリア別）')
st.markdown('#### 売り上げ分析（エリア別)')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[1, 3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')

# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[1, 3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])
else:
    st.info('前期のファイルを選択してください。')
    st.stop()

# *** 出荷月、受注月列の追加***
df_now['出荷月'] = df_now['出荷日'].dt.month
df_now['受注月'] = df_now['受注日'].dt.month
df_now['商品コード2'] = df_now['商　品　名'].map(lambda x: x.split()[0]) #品番
df_now['商品コード3'] = df_now['商　品　名'].map(lambda x: str(x)[0:2]) #頭品番
df_now['張地'] = df_now['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
df_last['出荷月'] = df_last['出荷日'].dt.month
df_last['受注月'] = df_last['受注日'].dt.month
df_last['商品コード2'] = df_last['商　品　名'].map(lambda x: x.split()[0])
df_last['商品コード3'] = df_last['商　品　名'].map(lambda x: str(x)[0:2]) #頭品番
df_last['張地'] = df_last['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')

# ***INT型への変更***
df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

area_list = st.multiselect(
        '得意先を選択(複数)',
        df_now['得意先名'].unique())

def sales():
    
    sum_list = []    
    for cust in area_list:
        now_cust_sum = df_now[df_now['得意先名']==cust]['金額'].sum()
        last_cust_sum = df_last[df_last['得意先名']==cust]['金額'].sum()
        temp_list = [last_cust_sum, now_cust_sum]
        sum_list.append(temp_list)

    df_results = pd.DataFrame(sum_list, columns=['前期', '今期'], index=area_list)
    df_results.loc['合計'] = df_results.sum()
    df_results['対前年比'] = df_results['今期'] / df_results['前期']
    df_results['対前年差'] = df_results['今期'] - df_results['前期']
    df_results = df_results.T

    ratio = '{:.2f}'.format(df_results.loc['対前年比', '合計'])
    diff = '{:,}'.format(int(df_results.loc['対前年差', '合計']))
    st.metric(label='対前年比', value=ratio, delta=diff)

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in df_results.columns:
        fig.add_trace(
            go.Scatter(
                x=df_results.index[:2],
                y=df_results[col][:2],
                mode = 'lines+markers+text', #値表示
                text=round(df_results[col][:2]/10000),
                textposition="top center",
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='エリア別売上（累計）',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def sales_month():
    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    df_now_cust = df_now[df_now['得意先名'].isin(area_list)]
    df_last_cust = df_last[df_last['得意先名'].isin(area_list)]

    sum_list = []
    for month in month_list:
        df_now_month = df_now_cust[df_now_cust['受注月']==month]['金額'].sum()
        df_last_month = df_last_cust[df_last_cust['受注月']==month]['金額'].sum()
        temp_list = [df_now_month, df_last_month]
        sum_list.append(temp_list)

    df_results = pd.DataFrame(sum_list, index=month_list, columns=['今期', '前期']) 

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in df_results.columns:
        fig.add_trace(
            go.Scatter(
                x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                y=df_results[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_results[col]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='エリア別売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def ld_comp():

    df_now_cust = df_now[df_now['得意先名'].isin(area_list)]
    df_last_cust = df_last[df_last['得意先名'].isin(area_list)]

    now_cust_sum_l = df_now_cust[df_now_cust['商品分類名2'].isin(\
        ['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()

    now_cust_sum_d = df_now_cust[df_now_cust['商品分類名2'].isin(\
        ['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum() 

    last_cust_sum_l = df_last_cust[df_last_cust['商品分類名2'].isin(\
        ['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()

    last_cust_sum_d = df_last_cust[df_last_cust['商品分類名2'].isin(\
        ['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum() 
    temp_list = [[last_cust_sum_l, last_cust_sum_d], [now_cust_sum_l, now_cust_sum_d]] 

    df_results = pd.DataFrame(temp_list, index=['前期', '今期'], columns=['Living', 'Dining'])
    df_results.loc['対前年比'] = df_results.loc['今期'] / df_results.loc['前期']
    df_results.loc['対前年差'] = df_results.loc['今期'] - df_results.loc['前期']

    col1, col2 = st.columns(2)
    with col1:
        st.write('Living')
        ratio = '{:.2f}'.format(df_results.loc['対前年比', 'Living'])
        diff = '{:,}'.format(int(df_results.loc['対前年差', 'Living']))
        st.metric(label='対前年比', value=ratio, delta=diff)

    with col2:
        st.write('Dining')
        ratio = '{:.2f}'.format(df_results.loc['対前年比', 'Dining'])
        diff = '{:,}'.format(int(df_results.loc['対前年差', 'Dining']))
        st.metric(label='対前年比', value=ratio, delta=diff)    


    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in df_results.columns:
        fig.add_trace(
            go.Scatter(
                x=df_results.index[:2], #対前年比,対前年差を拾わないように[:2]
                y=df_results[col][:2],
                mode = 'lines+markers+text', #値表示
                text=round(df_results[col][:2]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='LD別売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True)         



def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '売上: 累計': sales,
        '売上: 月別': sales_month,
        'LD別売上: 累計': ld_comp

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