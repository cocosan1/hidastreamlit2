import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go

st.set_page_config(page_title='売り上げ分析test2')
st.title('売り上げ分析test2')
st.subheader('Feed me with your Excel File')

# ***ファイルアップロード***
uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')
df = DataFrame()
if uploaded_file:
    st.markdown('---')
    df = pd.read_excel(
    uploaded_file, sheet_name='受注委託移動在庫生産照会', usecols=[10, 14, 15, 42, 50, 51, 52], index_col=0)
    df['金額'] = df['金額'].astype(int)

# *** selectbox 商品分類2***
category = df['商品分類名2'].unique()
option_category = st.selectbox(
    'category:',
    category,   
) 
st.write('You selected: ', option_category)
categorybase = df[df['商品分類名2']==option_category]

# ***塗色別売り上げ ***

color = categorybase.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
st.write('塗色別売上')
st.dataframe(color)

# グラフ　塗色別売り上げ
st.write('グラフ　塗色別売上')
fig_color = go.Figure(
    data=[
        go.Pie(
            labels=color.index,
            values=color
            )])
fig_color.update_layout(
    showlegend=True, #凡例表示
    height=200,
    margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
    )
fig_color.update_traces(textposition='inside', textinfo='label+percent') 
#inside グラフ上にテキスト表示
st.plotly_chart(fig_color, use_container_width=True) 
#plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

# ***張地別売り上げ ***
fabric = categorybase.groupby('張布CD')['金額'].sum().sort_values(ascending=False) #降順
st.write('張地別売上')
st.dataframe(fabric)

# グラフ　張地別売り上げ
st.write('グラフ　張地別売上')
fig_fabric = go.Figure(
    data=[
        go.Pie(
            labels=fabric.index,
            values=fabric
            )])
fig_fabric.update_layout(
    showlegend=True, #凡例表示
    height=200,
    margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
    )
fig_fabric.update_traces(textposition='inside', textinfo='label+percent') 
#inside グラフ上にテキスト表示
st.plotly_chart(fig_fabric, use_container_width=True) 
#plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

# ***シリーズ別売り上げ ***
series = categorybase.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False) #降順

# *** DF シリーズ別売り上げ ***
st.write('シリーズ別売上')
st.dataframe(series)

# グラフ　シリーズ別売り上げ
st.write('グラフ　シリーズ別売上')
fig_series = go.Figure()
fig_series.add_trace(
    go.Bar(
        x=series.index,
        y=series,
        )
)
st.plotly_chart(fig_series, use_container_width=True)

# グラフ　シリーズ別売り上げ構成比
st.write('グラフ　シリーズ別売り上げ構成比')
fig_series_ratio = go.Figure(
    data=[
        go.Pie(
            labels=series.index,
            values=series
            )])
fig_series_ratio.update_layout(
    showlegend=True, #凡例表示
    height=200,
    margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
    )
fig_series_ratio.update_traces(textposition='inside', textinfo='label+percent') 
#inside グラフ上にテキスト表示
st.plotly_chart(fig_series_ratio, use_container_width=True) 
#plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

# *** シリース別塗色別売上 ***
series_color = categorybase.groupby(['シリーズ名', '塗色CD'])['金額'].sum().sort_values(ascending=False) #降順

st.write('シリース別塗色別売上')
st.dataframe(series_color)

# **シリーズ別塗色別売上 ***
series_color_fab = categorybase.groupby(['シリーズ名', '塗色CD', '張布CD'])['金額'].sum().sort_values(ascending=False).head(20) #降順

st.write('シリーズ別塗色別張地別売上')
st.dataframe(series_color_fab)

# ***シリーズベース ***

# *** selectbox 商品分類2***
series_list = df['シリーズ名'].unique()
option_series = st.selectbox(
    'series:',
    series_list,   
) 
st.write('You selected: ', option_series) 

seriesbase = categorybase[categorybase['シリーズ名']==option_series]
series_base_col_fab = seriesbase.groupby(['塗色CD', '張布CD'])['金額'].sum()

st.write('塗色別張地別売上')
st.dataframe(series_base_col_fab)

