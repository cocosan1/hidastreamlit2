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

st.set_page_config(page_title='売り上げ分析（星川）')
st.markdown('#### 売り上げ分析（星川)')

# ***ファイルアップロード 今期出荷***
uploaded_file_snow = st.sidebar.file_uploader('今期出荷', type='xlsx', key='snow')
df_snow = DataFrame()
if uploaded_file_snow:
    df_snow = pd.read_excel(
    uploaded_file_snow, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 15, 16, 45]) #index　ナンバー不要　index_col=0
else:
    st.info('今期の出荷ファイルを選択してください。')

# ***ファイル読み込み 前期出荷***
df_slast = pd.read_excel(\
    '79期出荷ALL星川.xlsx', sheet_name='受注委託移動在庫生産照会', \
        usecols=[3, 6, 15, 16, 45]) #index　ナンバー不要　index_col=0

# ***ファイルアップロード 今期***
uploaded_file_jnow = st.sidebar.file_uploader('今期受注', type='xlsx', key='jnow')
df_jnow = DataFrame()
if uploaded_file_jnow:
    df_jnow = pd.read_excel(
    uploaded_file_jnow, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 15, 16, 45]) #index　ナンバー不要　index_col=0
else:
    st.info('今期の受注ファイルを選択してください。')

# ***ファイルアップロード　前期***
uploaded_file_jlast = st.sidebar.file_uploader('前期受注', type='xlsx', key='jlast')
df_jlast = DataFrame()
if uploaded_file_jlast:
    df_jlast = pd.read_excel(
    uploaded_file_jlast, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 15, 16, 45])
else:
    st.info('前期の受注ファイルを選択してください。')
    st.stop()

# *** 出荷月、受注月列の追加***
df_snow['出荷月'] = df_snow['出荷日'].dt.month
df_snow['受注月'] = df_snow['受注日'].dt.month
df_slast['出荷月'] = df_slast['出荷日'].dt.month
df_slast['受注月'] = df_slast['受注日'].dt.month
df_jnow['出荷月'] = df_jnow['出荷日'].dt.month
df_jnow['受注月'] = df_jnow['受注日'].dt.month
df_jlast['出荷月'] = df_jlast['出荷日'].dt.month
df_jlast['受注月'] = df_jlast['受注日'].dt.month

# ***INT型への変更***
df_snow[['金額', '出荷月', '受注月']] = df_snow[[\
    '金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_slast[['金額', '出荷月', '受注月']] = df_slast[[\
    '金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

df_jnow[['金額', '出荷月', '受注月']] = df_jnow[[\
    '金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_jlast[['金額', '出荷月', '受注月']] = df_jlast[[\
    '金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

df_jnow = df_jnow[df_jnow['営業担当コード']==952]
df_jlast = df_jlast[df_jlast['営業担当コード']==952]

#目標
target_list = [9000000, 10600000, 10300000, 7900000, 8600000, 9100000, \
          5500000, 6400000, 7100000, 8900000, 7500000,9100000] 

def all():
    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    columns_list = ['目標', '出荷/今期', '出荷/前期', '受注/今期', '受注/前期','対目標差', \
                    '対目標比', '対前年差', '対前年比']

    target_list2 = [] #str化
    snow_list = []
    slast_list = []
    jnow_list = []
    jlast_list = []

    target_diff_list = []
    target_rate_list = []
    sales_diff_list = []
    sales_rate_list = []

    target_num = 0
    for month in month_list:
        target = target_list[target_num]
        snow = df_snow[df_snow['出荷月'].isin([month])]['金額'].sum()
        slast = df_slast[df_slast['出荷月'].isin([month])]['金額'].sum()
        jnow = df_jnow[df_jnow['受注月'].isin([month])]['金額'].sum()
        jlast = df_jlast[df_jlast['受注月'].isin([month])]['金額'].sum()

        target_diff = snow - target
        target_rate = f'{snow / target*100: 0.1f} %'
        
        sales_diff = jnow - jlast
        sales_rate = f'{jnow / jlast * 100: 0.1f} %'

        target_list2.append('{:,}'.format(target))
        snow_list.append('{:,}'.format(snow))
        slast_list.append('{:,}'.format(slast))
        jnow_list.append('{:,}'.format(jnow))
        jlast_list.append('{:,}'.format(jlast))

        target_diff_list.append('{:,}'.format(target_diff))
        target_rate_list.append(target_rate)

        sales_diff_list.append('{:,}'.format(sales_diff))
        sales_rate_list.append(sales_rate)

        target_num += 1

    df_month = pd.DataFrame(list(zip(\
        target_list2, snow_list, slast_list, jnow_list, jlast_list, target_diff_list, target_rate_list,\
            sales_diff_list, sales_rate_list)), columns=columns_list, index=month_list)
    
    with st.expander('詳細', expanded=False):
        st.table(df_month)


    #***********************************出荷ベース可視化
    #グラフ用にintのデータを用意
    df_month2 = df_month.copy()
    df_month2['目標2'] = df_month2['目標'].apply(lambda x: int(x.replace(',', '')))
    df_month2['出荷/今期2'] = df_month2['出荷/今期'].apply(lambda x: int(x.replace(',', '')))

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in df_month2.columns[9:11]:
        fig.add_trace(
            go.Scatter(
                x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                y=df_month2[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_month2[col]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='月別目標/売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

    #***********************************累計　出荷ベース可視化
    #グラフ用にintのデータを用意

    df_month2['累計/目標2'] = df_month2['目標2'].cumsum()
    df_month2['累計/出荷/今期2'] = df_month2['出荷/今期2'].cumsum()

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig2 = go.Figure()
    #今期のグラフの追加
    for col in df_month2.columns[11:13]:
        fig2.add_trace(
            go.Scatter(
                x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                y=df_month2[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_month2[col]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig2.update_layout(
        title='累計/目標/売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig2, use_container_width=True) 

    #*****受注ベース可視化
    #グラフ用にint化
    df_month2['受注/今期2'] = df_month2['受注/今期'].apply(lambda x: int(x.replace(',', '')))
    df_month2['受注/前期2'] = df_month2['受注/前期'].apply(lambda x: int(x.replace(',', '')))

    #グラフを描くときの土台となるオブジェクト
    fig3 = go.Figure()
    #今期のグラフの追加
    for col in df_month2.columns[13:15]:
        fig3.add_trace(
            go.Scatter(
                x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                y=df_month2[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_month2[col]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig3.update_layout(
        title='受注ベース/売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig3, use_container_width=True)

    #*****受注ベース可視化
    #グラフ用にint化
    df_month2['受注/今期2'] = df_month2['受注/今期'].apply(lambda x: int(x.replace(',', '')))
    df_month2['受注/前期2'] = df_month2['受注/前期'].apply(lambda x: int(x.replace(',', '')))

    #グラフを描くときの土台となるオブジェクト
    fig3 = go.Figure()
    #今期のグラフの追加
    for col in df_month2.columns[13:15]:
        fig3.add_trace(
            go.Scatter(
                x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                y=df_month2[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_month2[col]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig3.update_layout(
        title='受注ベース/売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig3, use_container_width=True)

    #*****累計 受注ベース可視化
    #グラフ用にint化
    df_month2['累計/受注/今期2'] = df_month2['受注/今期2'].cumsum()
    df_month2['累計/受注/前期2'] = df_month2['受注/前期2'].cumsum()

    #グラフを描くときの土台となるオブジェクト
    fig4 = go.Figure()
    #今期のグラフの追加
    for col in df_month2.columns[15:17]:
        fig4.add_trace(
            go.Scatter(
                x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                y=df_month2[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_month2[col]/10000),
                textposition="top center", 
                name=col)
        )

    #レイアウト設定     
    fig4.update_layout(
        title='累計/受注ベース/売上',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig4, use_container_width=True)   

        

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '全体': all,


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