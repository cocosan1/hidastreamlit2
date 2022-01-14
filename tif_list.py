from logging import debug
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.elements import metric
from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析（TIF 一覧）')
st.markdown('#### 売り上げ分析（TIF 一覧）')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 9, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')

# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 9, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])
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

# オリジナル比率（全体）
def original_ratio():
    now_original_sum = df_now[df_now['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
    last_original_sum = df_last[df_last['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()

    o_ratio_now = now_original_sum / df_now_total
    o_ratio_last = last_original_sum / df_last_total
    ratio_diff = f'{(o_ratio_now - o_ratio_last)*100:0.1f} %'

    st.markdown('###### オリジナル比率(全店)')
    col1, col2 = st.columns(2)
    with col1:
        st.metric('今期', value=f'{o_ratio_now*100: 0.1f} %', delta=ratio_diff)

    with col2:
        st.metric('前期', value=f'{o_ratio_last*100: 0.1f} %')

    st.markdown('###### オリジナル金額(全店)')

    diff = int(now_original_sum - last_original_sum)
    diff2 = '{:,}'.format(diff)
    ratio = f'{now_original_sum / last_original_sum*100:0.1f} %'
    df_original_sum = pd.DataFrame(list([now_original_sum, last_original_sum, ratio, diff]), index=['今期', '前期', '対前年比', '対前年差'])
    df_original_sum2 = pd.DataFrame(list([now_original_sum, last_original_sum]), index=['今期', '前期'], columns=['金額'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df_original_sum2, width=300, height=350, use_container_width=False)
    with col2:
        st.metric('対前年比', ratio, delta=diff2)    

    # # グラフ　シリーズ別売り上げ
    # st.write('オリジナル売上')
    # fig_original = go.Figure()
    # fig_original.add_trace(
    #     go.Bar(
    #         x=df_original_sum2.index,
    #         y=df_original_sum,
    #         )
    # )
    # fig_original.update_layout(
    #     height=500,
    #     width=2000,
    # )        
    
    # st.plotly_chart(fig_original, use_container_width=True)

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
        
        original_now.append(original_now_culc)
        original_last.append(original_last_culc)
        original_rate_now.append(original_rate_now_culc)
        original_rate_last.append(original_rate_last_culc)
        original_rate__diff.append(original_rate_diff_culc)
        
    original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
    st.markdown('###### オリジナル比率(店毎）')   
    st.dataframe(original_rate_list)

# オリジナル比率（D）
def original_ratio_d():
    series_list = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
    #ダイニング　全体売上
    sum_now_d = df_now[df_now['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
    sum_last_d = df_last[df_last['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
    #ダイニング　オリジナルdf
    df_now_d = df_now[df_now['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
    df_last_d = df_last[df_last['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
    #ダイニング　オリジナル売上
    now_original_d_sum = df_now_d[df_now_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
    last_original_d_sum = df_last_d[df_last_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
    #ダイニング　オリジナル比率
    ratio_now_d = f'{now_original_d_sum / sum_now_d*100:0.1f} %'
    ratio_last_d = f'{last_original_d_sum / sum_last_d*100:0.1f} %'
    
    diff_d = f'{((now_original_d_sum / sum_now_d)-(last_original_d_sum / sum_last_d))*100:0.1f} %'

    col1, col2 = st.columns(2)
    with col1:
        st.metric('オリジナル比率 ダイニング （今期）', ratio_now_d, delta=diff_d )

    with col2:
        st.metric('オリジナル比率 ダイニング （前期）', ratio_last_d)    

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
        df_now_cust_d = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
        df_last_cust_d = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
        now_cust_d_sum = df_now_cust_d['金額'].sum()
        last_cust_d_sum = df_last_cust_d['金額'].sum()
        original_now_d_culc = df_now_cust_d[df_now_cust_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        original_last_d_culc = df_last_cust_d[df_last_cust_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        original_rate_now_culc = f'{(original_now_d_culc / now_cust_d_sum)*100: 0.1f} %'
        original_rate_last_culc = f'{(original_last_d_culc / last_cust_d_sum)*100: 0.1f} %'
        original_rate_diff_culc = f'{((original_now_d_culc / now_cust_d_sum) - (original_last_d_culc / last_cust_d_sum))*100: 0.1f} %'
        
        original_now.append(original_now_d_culc)
        original_last.append(original_last_d_culc)
        original_rate_now.append(original_rate_now_culc)
        original_rate_last.append(original_rate_last_culc)
        original_rate__diff.append(original_rate_diff_culc)
        
    original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
    st.markdown('###### オリジナル比率(ダイニング/店毎）')   
    st.dataframe(original_rate_list)

# オリジナル比率(L)
def original_ratio_l():
    series_list = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
    #リニング　全体売上
    sum_now_l = df_now[df_now['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
    sum_last_l = df_last[df_last['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
    #リビング　オリジナルdf
    df_now_l = df_now[df_now['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
    df_last_l = df_last[df_last['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
    #リビング　オリジナル売上
    now_original_l_sum = df_now_l[df_now_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
    last_original_l_sum = df_last_l[df_last_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
    
    #リビング　オリジナル比率
    ratio_now_l = f'{now_original_l_sum / sum_now_l*100:0.1f} %'
    ratio_last_l = f'{last_original_l_sum / sum_last_l*100:0.1f} %'
    
    diff_l = f'{((now_original_l_sum / sum_now_l) - (last_original_l_sum / sum_last_l))*100:0.1f} %'

    col1, col2 = st.columns(2)
    with col1:
        st.metric('オリジナル比率 リビング （今期）', ratio_now_l, delta=diff_l )

    with col2:
        st.metric('オリジナル比率 リビング （前期）', ratio_last_l)

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
        df_now_cust_l = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        df_last_cust_l = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        now_cust_l_sum = df_now_cust_l['金額'].sum()
        last_cust_l_sum = df_last_cust_l['金額'].sum()
        original_now_l_culc = df_now_cust_l[df_now_cust_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        original_last_l_culc = df_last_cust_l[df_last_cust_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        original_rate_now_culc = f'{(original_now_l_culc / now_cust_l_sum)*100: 0.1f} %'
        original_rate_last_culc = f'{(original_last_l_culc / last_cust_l_sum)*100: 0.1f} %'
        original_rate_diff_culc = f'{((original_now_l_culc / now_cust_l_sum) - (original_last_l_culc / last_cust_l_sum))*100: 0.1f} %'
        
        original_now.append(original_now_l_culc)
        original_last.append(original_last_l_culc)
        original_rate_now.append(original_rate_now_culc)
        original_rate_last.append(original_rate_last_culc)
        original_rate__diff.append(original_rate_diff_culc)
        
    original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
    st.markdown('###### オリジナル比率(リビング/店毎）')   
    st.dataframe(original_rate_list)    

def original_sum_ld():
    
    series_list = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
    sum_now_d_list = []
    sum_last_d_list = []
    sum_now_l_list = []
    sum_last_l_list = []
    ratio_d_list = []
    ratio_l_list = []
    diff_d_list = []
    diff_l_list = []

    for series in series_list:
        df_now_series = df_now[df_now['シリーズ名']==series]
        df_last_series = df_last[df_last['シリーズ名']==series]
        sum_now_d = df_now_series[df_now_series['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        sum_last_d = df_last_series[df_last_series['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        sum_now_l = df_now_series[df_now_series['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        sum_last_l = df_last_series[df_last_series['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        ratio_d = f'{sum_now_d / sum_last_d*100:0.1f} %'
        ratio_l = f'{sum_now_l / sum_last_l*100:0.1f} %'
        diff_d = sum_now_d - sum_last_d
        diff_l = sum_now_l - sum_last_l
        sum_now_d_list.append(sum_now_d)
        sum_last_d_list.append(sum_last_d)
        sum_now_l_list.append(sum_now_l)
        sum_last_l_list.append(sum_last_l)
        ratio_d_list.append(ratio_d)
        ratio_l_list.append(ratio_l)
        diff_d_list.append(diff_d)
        diff_l_list.append(diff_l)
       
    columns =['今期', '前期', '前年比', '対前年差']
    df_d = pd.DataFrame(list(zip(sum_now_d_list, sum_last_d_list, ratio_d_list, diff_d_list)), index=series_list, columns=columns)   
    df_l = pd.DataFrame(list(zip(sum_now_l_list, sum_last_l_list, ratio_l_list, diff_l_list)), index=series_list, columns=columns)

    col1, col2 = st.columns(2)

    with col1:
        # グラフ dining
        def graph_layout(fig, x_title, y_title):
            return fig.update_layout(
                xaxis_title='シリーズ',
                yaxis_title='金額',
            
                
            )
        title = 'オリジナル売上　ダイニング'

        fig = go.Figure(data=[
            go.Bar(name='今期', x=df_d.index, y=df_d['今期'] ),
            go.Bar(name='前期', x=df_d.index, y=df_d['前期']),
        ])
        fig = graph_layout(fig, x_title='シリーズ', y_title=title)
        fig.update_layout(barmode='group', title=title, width=370)

        st.write(fig)
    with col2:
        # グラフ living
        def graph_layout(fig, x_title, y_title):
            return fig.update_layout(
                xaxis_title='シリーズ',
                yaxis_title='金額',
            
            )
        title = 'オリジナル売上　リビング'

        fig = go.Figure(data=[
            go.Bar(name='今期', x=df_l.index, y=df_l['今期'] ),
            go.Bar(name='前期', x=df_l.index, y=df_l['前期']),
        ])
        fig = graph_layout(fig, x_title='シリーズ', y_title=title)
        fig.update_layout(barmode='group', title=title, width=370)

        st.write(fig) 
        
    st.markdown('###### dining')
    st.dataframe(df_d)

    st.markdown('###### living')
    st.dataframe(df_l)
    
#累計　シリーズベース
def original_series_category_earnings_sum():

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
    df_now_series = df_now[df_now['シリーズ名']==option_series]
    df_now_series_cate = df_now_series[df_now_series['商品分類名2']==option_category]

    customer_list = df_last['得意先名'].unique()
    df_last_series = df_last[df_last['シリーズ名']==option_series]
    df_last_series_cate = df_last_series[df_last_series['商品分類名2']==option_category]

    sum_now = df_now_series_cate['金額'].sum()
    sum_last = df_last_series_cate['金額'].sum()
    sum_diff = '{:,}'.format(sum_now - sum_last)
    sum_ratio = f'{(sum_now / sum_last)*100:0.1f} %'

    st.markdown('###### オリジナル売上(全店)')
    col1, col2, col3 = st.columns(3)
    with col1:
        df_earn = pd.DataFrame(list([sum_now, sum_last]), index=['今期', '前期'], columns=['金額'])
        st.bar_chart(df_earn, width=200, height=350, use_container_width=False)
        
    with col2:
        st.metric('今期', value='{:,}'.format(sum_now), delta=sum_diff)
        st.write(sum_ratio)
        
    with col3:
        st.metric('前期', value='{:,}'.format(sum_last))
        
    sum_now = []
    sum_last = []
    sum_ratio = []
    sum_diff = []

    df_result = pd.DataFrame(index=customer_list)

    for customer in customer_list:
        df_now_series_cate_cust = df_now_series_cate[df_now_series_cate['得意先名']==customer]
        df_last_series_cate_cust = df_last_series_cate[df_last_series_cate['得意先名']==customer]
        sum_now_culc = df_now_series_cate_cust['金額'].sum()
        sum_last_culc = df_last_series_cate_cust['金額'].sum()
        sum_ratio_culc = f'{(sum_now_culc/sum_last_culc)*100:0.1f} %'
        sum_diff_culc = sum_now_culc - sum_last_culc

        sum_now.append(sum_now_culc)
        sum_last.append(sum_last_culc)
        sum_ratio.append(sum_ratio_culc)
        sum_diff.append(sum_diff_culc)
    df_result['今期'] = sum_now
    df_result['前期'] = sum_last
    df_result['対前年比'] = sum_ratio
    df_result['対前年差'] = sum_diff
    st.caption('店舗別一覧')
    st.dataframe(df_result)


#累計　カテゴリーベース
def original_category_seriesearnings_sum():

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
    df_now_cate = df_now[df_now['商品分類名2']==option_category]
    df_now_cate_seri = df_now_cate[df_now_cate['シリーズ名']==option_series]

    customer_list = df_last['得意先名'].unique()
    df_last_cate = df_last[df_last['商品分類名2']==option_category]
    df_last_cate_seri = df_last_cate[df_last_cate['シリーズ名']==option_series]

    sum_now = df_now_cate_seri['金額'].sum()
    sum_last = df_last_cate_seri['金額'].sum()
    sum_diff = '{:,}'.format(sum_now - sum_last)
    sum_ratio = f'{(sum_now / sum_last)*100:0.1f} %'

    st.markdown('###### オリジナル売上(全店)')
    col1, col2, col3 = st.columns(3)
    with col1:
        df_earn = pd.DataFrame(list([sum_now, sum_last]), index=['今期', '前期'], columns=['金額'])
        st.bar_chart(df_earn, width=200, height=350, use_container_width=False)
        
    with col2:
        st.metric('今期', value='{:,}'.format(sum_now), delta=sum_diff)
        st.write(sum_ratio)
        
    with col3:
        st.metric('前期', value='{:,}'.format(sum_last))
        
    sum_now = []
    sum_last = []
    sum_ratio = []
    sum_diff = []

    df_result = pd.DataFrame(index=customer_list)

    for customer in customer_list:
        df_now_cate_seri_cust = df_now_cate_seri[df_now_cate_seri['得意先名']==customer]
        df_last_cate_seri_cust = df_last_cate_seri[df_last_cate_seri['得意先名']==customer]
        sum_now_culc = df_now_cate_seri_cust['金額'].sum()
        sum_last_culc = df_last_cate_seri_cust['金額'].sum()
        sum_ratio_culc = f'{(sum_now_culc/sum_last_culc)*100:0.1f} %'
        sum_diff_culc = sum_now_culc - sum_last_culc

        sum_now.append(sum_now_culc)
        sum_last.append(sum_last_culc)
        sum_ratio.append(sum_ratio_culc)
        sum_diff.append(sum_diff_culc)
    df_result['今期'] = sum_now
    df_result['前期'] = sum_last
    df_result['対前年比'] = sum_ratio
    df_result['対前年差'] = sum_diff
    st.caption('店舗別一覧')
    st.dataframe(df_result)
    


#月毎　シリーズベース
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

# 月毎　カテゴリーベース
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

#品番別数量（全体）       
def hinban_count():
    # *** selectbox シリーズ***
    series = df_now['シリーズ名'].unique()
    option_series = st.selectbox(
        'series:',
        series,   
    )
    df_now_series = df_now[df_now['シリーズ名']==option_series]
    df_last_series = df_last[df_last['シリーズ名']==option_series]
    
    hinban_list = df_now_series['商品コード2'].unique()
    index = []
    hinban_count_now_list = []
    hinabn_count_last_list = []
    diff = []
    ratio = []

    for hinban in hinban_list:
        index.append(hinban)
        hinabn_count_now = df_now_series[df_now_series['商品コード2']==hinban]['数量'].sum()
        hinabn_count_last = df_last_series[df_last_series['商品コード2']==hinban]['数量'].sum()
        hinban_count_now_list.append(hinabn_count_now)
        hinabn_count_last_list.append(hinabn_count_last)
        diff_culc = hinabn_count_now - hinabn_count_last
        diff.append(diff_culc)
        ratio_culc = f'{(hinabn_count_now / hinabn_count_last)*100:0.1f} %'
        ratio.append(ratio_culc)

    df_result = pd.DataFrame(list(zip(hinban_count_now_list, hinabn_count_last_list, ratio, diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])
    st.dataframe(df_result)

# 品番別売上（全体）
def hinban_sum():
    # *** selectbox シリーズ***
    series = df_now['シリーズ名'].unique()
    option_series = st.selectbox(
        'series:',
        series,   
    )
    df_now_series = df_now[df_now['シリーズ名']==option_series]
    df_last_series = df_last[df_last['シリーズ名']==option_series]
    
    hinban_list = df_now_series['商品コード2'].unique()
    index = []
    hinban_sum_now_list = []
    hinabn_sum_last_list = []
    diff = []
    ratio = []

    for hinban in hinban_list:
        index.append(hinban)
        hinabn_sum_now = df_now_series[df_now_series['商品コード2']==hinban]['金額'].sum()
        hinabn_sum_last = df_last_series[df_last_series['商品コード2']==hinban]['金額'].sum()
        hinban_sum_now_list.append(hinabn_sum_now)
        hinabn_sum_last_list.append(hinabn_sum_last)
        diff_culc = hinabn_sum_now - hinabn_sum_last
        diff.append(diff_culc)
        ratio_culc = f'{(hinabn_sum_now / hinabn_sum_last)*100:0.1f} %'
        ratio.append(ratio_culc)

    df_result = pd.DataFrame(list(zip(hinban_sum_now_list, hinabn_sum_last_list, ratio, diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])
    st.dataframe(df_result)

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'オリジナル比率（全体）●': original_ratio,
        'オリジナル比率（ダイニング）●': original_ratio_d,
        'オリジナル比率（リビング）●': original_ratio_l,
        'オリジナル売上 シリーズ/LD別●': original_sum_ld,
        'オリ売上累計 店別/シリーズ/分類': original_series_category_earnings_sum,
        'オリ売上累計 店別/分類/シリーズ':original_category_seriesearnings_sum,
        'オリ売上月毎 店別/シリーズ/分類': original_series_category_earnings,
        'オリ売上月毎 店別/分類/シリーズ': original_category_series_earnings,
        '品番別数量 全体': hinban_count,
        '品番別金額 全体': hinban_sum,
        
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