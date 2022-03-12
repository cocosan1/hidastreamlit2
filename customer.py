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
st.markdown('#### 売り上げ分析（得意先別)')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')

# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])
else:
    st.info('前期のファイルを選択してください。')
    st.stop()

# *** 出荷月、受注月列の追加***
df_now['出荷月'] = df_now['出荷日'].dt.month
df_now['受注月'] = df_now['受注日'].dt.month
df_now['張地'] = df_now['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
df_last['出荷月'] = df_last['出荷日'].dt.month
df_last['受注月'] = df_last['受注日'].dt.month
df_last['張地'] = df_last['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')

# ***INT型への変更***
df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

df_now_total = df_now['金額'].sum()
df_last_total = df_last['金額'].sum()

# *** selectbox 得意先名***
customer = df_now['得意先名'].unique()
option_customer = st.selectbox(
    '得意先名:',
    customer,   
) 

df_now_cust =df_now[df_now['得意先名']==option_customer]
df_last_cust =df_last[df_last['得意先名']==option_customer]
df_now_cust_total = df_now_cust['金額'].sum()
df_last_cust_total = df_last_cust['金額'].sum()

def earnings_comparison_year():
    total_cust_now = df_now[df_now['得意先名']==option_customer]['金額'].sum()
    total_cust_last = df_last[df_last['得意先名']==option_customer]['金額'].sum()
    total_comparison = f'{total_cust_now / total_cust_last * 100: 0.1f} %'
    diff = '{:,}'.format(total_cust_now - total_cust_last)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('今期売上', value= '{:,}'.format(total_cust_now), delta=diff)
    with col2:
        st.metric('前期売上', value= '{:,}'.format(total_cust_last))
    with col3:
        st.metric('対前年比', value= total_comparison)    

def earnings_comparison_month():
    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    columns_list = ['今期', '前期', '対前年差', '対前年比']
    df_now_cust = df_now[df_now['得意先名']==option_customer]
    df_last_cust = df_last[df_last['得意先名']==option_customer]

    earnings_now = []
    earnings_last = []
    earnings_diff = []
    earnings_rate = []

    for month in month_list:
        earnings_month_now = df_now_cust[df_now_cust['受注月'].isin([month])]['金額'].sum()
        earnings_month_last = df_last_cust[df_last_cust['受注月'].isin([month])]['金額'].sum()
        earnings_diff_culc = earnings_month_now - earnings_month_last
        earnings_rate_culc = f'{earnings_month_now / earnings_month_last * 100: 0.1f} %'

        earnings_now.append('{:,}'.format(earnings_month_now))
        earnings_last.append('{:,}'.format(earnings_month_last))
        earnings_diff.append('{:,}'.format(earnings_diff_culc))
        earnings_rate.append(earnings_rate_culc)

    df_earnings_month = pd.DataFrame(list(zip(earnings_now, earnings_last, earnings_diff, earnings_rate)), columns=columns_list, index=month_list)
    st.caption('受注月ベース')
    st.table(df_earnings_month)
    
def living_dining_comparison():
    st.markdown('##### LD 前年比/構成比')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('###### リビング')
        living_now = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_last = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()

        l_diff = living_now-living_last
        l_ratio = f'{living_now/living_last*100:0.1f} %'

        l_list = [living_now, living_last]
        l_columns = ['金額']
        l_index = ['今期', '前期']
        df_living = pd.DataFrame(l_list, columns=l_columns, index=l_index)
        
        st.bar_chart(df_living)
        st.caption(f'対前年差 {l_diff}')
        st.caption(f'対前年比 {l_ratio}')
        st.caption('クッション/リビングチェア/リビングテーブル')

    with col2:
        st.markdown('###### ダイニング')
        dining_now = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_last = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()

        d_diff = dining_now-dining_last
        d_ratio = f'{dining_now/dining_last*100:0.1f} %'

        d_list = [dining_now, dining_last]
        d_columns = ['金額']
        d_index = ['今期', '前期']
        df_dining = pd.DataFrame(d_list, columns=d_columns, index=d_index)
        
        st.bar_chart(df_dining)
        st.caption(f'対前年差 {d_diff}')
        st.caption(f'対前年比 {d_ratio}')
        st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')
    

    else_now = df_now_cust[df_now_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子','デスク', '小物・その他'])]['金額'].sum()
    else_last = df_last_cust[df_last_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子','デスク', '小物・その他'])]['金額'].sum()

    with col1:
        comp_now_list = [living_now, dining_now, else_now]
        comp_now_index = ['リビング', 'ダイニング', 'その他']
        comp_now_columns = ['分類']
        df_comp_now = pd.DataFrame(comp_now_index, columns=comp_now_columns)
        df_comp_now['金額'] = comp_now_list

        # グラフ
        st.markdown('###### LD比率(今期)')
        fig_ld_ratio_now = go.Figure(
            data=[
                go.Pie(
                    labels=df_comp_now['分類'],
                    values=df_comp_now['金額']
                    )])
        fig_ld_ratio_now.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_ld_ratio_now.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_ld_ratio_now, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col2:
        comp_last_list = [living_last, dining_last, else_last]
        comp_last_index = ['リビング', 'ダイニング', 'その他']
        comp_last_columns = ['分類']
        df_comp_last = pd.DataFrame(comp_last_index, columns=comp_last_columns)
        df_comp_last['金額'] = comp_last_list

        # グラフ
        st.markdown('###### LD比率(前期)')
        fig_ld_ratio_last = go.Figure(
            data=[
                go.Pie(
                    labels=df_comp_last['分類'],
                    values=df_comp_last['金額']
                    )])
        fig_ld_ratio_last.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_ld_ratio_last.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_ld_ratio_last, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

def living_dining_comparison_ld():

    # *** selectbox LD***
    category = ['リビング', 'ダイニング']
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    if option_category == 'リビング':
        df_now_cust_cate = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        df_last_cust_cate = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
    elif option_category == 'ダイニング':
        df_now_cust_cate = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
        df_last_cust_cate = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]

    index = []
    now_result = []
    last_result = []
    diff = []
    ratio = []
    series_list = df_now_cust_cate['シリーズ名'].unique()
    
    for series in series_list:
        index.append(series)
        now_culc = df_now_cust_cate[df_now_cust_cate['シリーズ名']==series]['金額'].sum()
        last_culc = df_last_cust_cate[df_last_cust_cate['シリーズ名']==series]['金額'].sum()
        now_result.append(now_culc)
        last_result.append(last_culc)
        diff_culc = '{:,}'.format(now_culc - last_culc)
        diff.append(diff_culc)
        ratio_culc = f'{now_culc/last_culc*100:0.1f} %'
        ratio.append(ratio_culc)
    df_result = pd.DataFrame(list(zip(now_result, last_result, ratio, diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])
    st.write(df_result)
    
    col1, col2 = st.columns(2)

    with col1:
        # グラフ
        st.write(f'{option_category} 構成比(今期)')
        fig_ld_ratio_now = go.Figure(
            data=[
                go.Pie(
                    labels=df_result.index,
                    values=df_result['今期']
                    )])
        fig_ld_ratio_now.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_ld_ratio_now.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_ld_ratio_now, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col2:
        # グラフ
        st.write(f'{option_category} 構成比(前期)')
        fig_ld_ratio_last = go.Figure(
            data=[
                go.Pie(
                    labels=df_result.index,
                    values=df_result['前期']
                    )])
        fig_ld_ratio_last.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_ld_ratio_last.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_ld_ratio_last, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

def series():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.caption('構成比は下段')
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]
    categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
    categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # ***シリーズ別売り上げ ***
        series_now = categorybase_cust_now.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(12) #降順
        series_now2 = series_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        # グラフ　シリーズ別売り上げ
        st.markdown('###### シリーズ別売上(今期)')
        fig_series_now = go.Figure()
        fig_series_now.add_trace(
            go.Bar(
                x=series_now.index,
                y=series_now,
                )
        )
        fig_series_now.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_series_now, use_container_width=True)

    with col2:
        # ***シリーズ別売り上げ ***
        series_last = categorybase_cust_last.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(12) #降順
        series_last2 = series_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        # グラフ　シリーズ別売り上げ
        st.markdown('###### シリーズ別売上(前期)')
        fig_series_last = go.Figure()
        fig_series_last.add_trace(
            go.Bar(
                x=series_last.index,
                y=series_last,
                )
        )
        fig_series_last.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_series_last, use_container_width=True)


    with col1:
        # グラフ　シリーズ別売り上げ構成比
        st.markdown('###### シリーズ別売り上げ構成比(今期)')
        fig_series_ratio_now = go.Figure(
            data=[
                go.Pie(
                    labels=series_now.index,
                    values=series_now
                    )])
        fig_series_ratio_now.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_series_ratio_now.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_series_ratio_now, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col2:
        # グラフ　シリーズ別売り上げ構成比
        st.markdown('###### シリーズ別売り上げ構成比(前期)')
        fig_series_ratio_last = go.Figure(
            data=[
                go.Pie(
                    labels=series_last.index,
                    values=series_last
                    )])
        fig_series_ratio_last.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_series_ratio_last.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_series_ratio_last, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

def item_count_category():
    # *** selectbox 得意先名***
    categories = df_now_cust['商品分類名2'].unique()
    option_categories = st.selectbox(
    '商品分類名2:',
    categories,   
    )    

    index = []
    count_now = []
    count_last = []
    diff = []

    df_now_cust_categories = df_now_cust[df_now_cust['商品分類名2']==option_categories]
    df_last_cust_categories = df_last_cust[df_last_cust['商品分類名2']==option_categories]
    series_list = df_now_cust[df_now_cust['商品分類名2']==option_categories]['シリーズ名'].unique()
    for series in series_list:
        index.append(series)
        month_len = len(df_now['受注月'].unique())
        df_now_cust_categories_count_culc = df_now_cust_categories[df_now_cust_categories['シリーズ名']==series]['数量'].sum()
        df_last_cust_categories_count_culc = df_last_cust_categories[df_last_cust_categories['シリーズ名']==series]['数量'].sum()
        count_now.append(f'{df_now_cust_categories_count_culc/month_len: 0.1f}')
        count_last.append(f'{df_last_cust_categories_count_culc/month_len: 0.1f}')
        diff.append(f'{(df_now_cust_categories_count_culc/month_len) - (df_last_cust_categories_count_culc/month_len):0.1f}')

    st.write('回転数/月平均')
    df_item_count = pd.DataFrame(list(zip(count_now, count_last, diff)), index=index, columns=['今期', '前期', '対前年差'])
    st.table(df_item_count) #列幅問題未解決   

def item_count_series():
    # *** selectbox 得意先名***
    series = df_now_cust['シリーズ名'].unique()
    option_series = st.selectbox(
    'シリーズ名:',
    series,   
    )    
    st.write('選択したシリーズ名: ', option_series)

    index = []
    count_now = []
    count_last = []
    diff = []

    df_now_cust_series = df_now_cust[df_now_cust['シリーズ名']==option_series]
    df_last_cust_series = df_last_cust[df_last_cust['シリーズ名']==option_series]
    categories = df_now_cust[df_now_cust['シリーズ名']==option_series]['商品分類名2'].unique()
    for category in categories:
        index.append(category)
        month_len = len(df_now['受注月'].unique())
        df_now_cust_series_count_culc = df_now_cust_series[df_now_cust_series['商品分類名2']==category]['数量'].sum()
        df_last_cust_series_count_culc = df_last_cust_series[df_last_cust_series['商品分類名2']==category]['数量'].sum()

        count_now.append(f'{df_now_cust_series_count_culc/month_len: 0.1f}')
        count_last.append(f'{df_last_cust_series_count_culc/month_len: 0.1f}')
        diff.append(f'{(df_now_cust_series_count_culc/month_len) - (df_last_cust_series_count_culc/month_len):0.1f}')

    st.write('回転数/月平均')
    df_item_count = pd.DataFrame(list(zip(count_now, count_last, diff)), index=index, columns=['今期', '前期', '対前年差'])
    st.table(df_item_count) #列幅問題未解決

def category_count_month():
    #　回転数 商品分類別 月毎
    # *** selectbox シリーズ名***
    category_list = df_now_cust['商品分類名2'].unique()
    option_category = st.selectbox(
    '商品分類名:',
    category_list,   
    ) 
    df_now_cust_category = df_now_cust[df_now_cust['商品分類名2']==option_category]
    
    months = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    count_now = []
    series_list = df_now_cust_category['シリーズ名'].unique()
    df_count = pd.DataFrame(index=series_list)
    for month in months:
        for series in series_list:
            df_now_cust_category_ser = df_now_cust_category[df_now_cust_category['シリーズ名']==series]
            count = df_now_cust_category_ser[df_now_cust_category_ser['受注月']==month]['数量'].sum()
            count_now.append(count)
        df_count[month] = count_now
        count_now = []
    st.caption('今期')
    st.table(df_count)



def series_count_month():
    #　回転数 商品分類別 月毎
    # *** selectbox シリーズ名***
    series_list = df_now_cust['シリーズ名'].unique()
    option_series = st.selectbox(
    'シリーズ名:',
    series_list,   
    ) 
    df_now_cust_series = df_now_cust[df_now_cust['シリーズ名']==option_series]
    
    months = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    count_now = []
    df_now_cust_series = df_now_cust[df_now_cust['シリーズ名']==option_series]
    categories = df_now_cust_series['商品分類名2'].unique()
    df_count = pd.DataFrame(index=categories)
    for month in months:
        for category in categories:
            df_now_cust_series_cat = df_now_cust_series[df_now_cust_series['商品分類名2']==category]
            count = df_now_cust_series_cat[df_now_cust_series_cat['受注月']==month]['数量'].sum()
            count_now.append(count)
        df_count[month] = count_now
        count_now = []
    st.caption('今期')
    st.table(df_count)   

def living_dining_latio():
    col1, col2, col3 = st.columns(3)
    cust_now = df_now[df_now['得意先名']== option_customer]
    cust_last = df_last[df_last['得意先名']== option_customer]
    total_now = cust_now['金額'].sum()
    total_last = cust_last['金額'].sum()

    with col1:
        living_now = cust_now[cust_now['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_last = cust_last[cust_last['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_diff = f'{(living_now/total_now*100) - (living_last/total_last*100):0.1f} %'
        st.metric('リビング比率', value=f'{living_now/total_now*100: 0.1f} %', delta=living_diff)
        st.caption(f'前年 {living_last/total_last*100: 0.1f} %')
        st.caption('クッション/リビングチェア/リビングテーブル')
    with col2:  
        dining_now = cust_now[cust_now['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_last = cust_last[cust_last['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_diff = f'{(dining_now/total_now*100) - (dining_last/total_last*100):0.1f} %'
        st.metric('ダイニング比率', value=f'{dining_now/total_now*100: 0.1f} %', delta=dining_diff)
        st.caption(f'前年 {dining_last/total_last*100: 0.1f} %')  
        st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')
    with col3:
        sonota_now = cust_now[cust_now['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子', 'デスク', '小物・その他'])]['金額'].sum()
        sonota_last = cust_last[cust_last['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子', 'デスク', '小物・その他'])]['金額'].sum()
        sonota_diff =  f'{(sonota_now/total_now*100) - (sonota_last/total_last*100):0.1f} %'
        st.metric('その他比率', value=f'{sonota_now/total_now*100: 0.1f} %', delta=sonota_diff) 
        st.caption(f'前年 {sonota_last/total_last*100: 0.1f} 円')  
        st.caption('キャビネット類/その他テーブル/雑品・特注品/その他椅子/デスク/小物・その他')

def hokkaido_fushi_kokusanzai():
    # *** 北海道比率　節材比率　国産材比率 ***
    col1, col2, col3 = st.columns(3)
    cust_now = df_now[df_now['得意先名']== option_customer]
    cust_last = df_last[df_last['得意先名']== option_customer]
    total_now = cust_now['金額'].sum()
    total_last = cust_last['金額'].sum()
    with col1:
        hokkaido_now = cust_now[cust_now['出荷倉庫']==510]['金額'].sum()
        hokkaido_last = cust_last[cust_last['出荷倉庫']==510]['金額'].sum()
        hokkaido_diff = f'{(hokkaido_now/total_now*100) - (hokkaido_last/total_last*100):0.1f} %'

        st.metric('北海道工場比率', value=f'{hokkaido_now/total_now*100: 0.1f} %', delta=hokkaido_diff) #小数点以下1ケタ
        st.caption(f'前年 {hokkaido_last/total_last*100: 0.1f} %')

    with col2:
        fushi_now = cust_now[cust_now['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        fushi_last = cust_last[cust_last['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        # sdソファ拾えていない isin その値を含む行　true
        fushi_diff = f'{(fushi_now/total_now*100) - (fushi_last/total_last*100):0.1f} %'
        st.metric('節材比率', value=f'{fushi_now/total_now*100: 0.1f} %', delta=fushi_diff) #小数点以下1ケタ
        st.caption(f'前年 {fushi_last/total_last*100:0.1f} %')
        st.caption('森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
    with col3:
        kokusanzai_now = cust_now[cust_now['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum() #SHSカバ拾えていない
        kokusanzai_last = cust_last[cust_last['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum() #SHSカバ拾えていない
        kokusanzai_diff = f'{(kokusanzai_now/total_now*100) - (kokusanzai_last/total_last*100):0.1f} %'
        st.metric('国産材比率', value=f'{kokusanzai_now/total_now*100: 0.1f} %', delta=kokusanzai_diff) #小数点以下1ケタ
        st.caption(f'前年 {kokusanzai_last/total_last*100: 0.1f} %')
        st.caption('北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた/Kinoe')

def profit_aroma():
    col1, col2 = st.columns(2)
    cust_now = df_now[df_now['得意先名']== option_customer]
    cust_last = df_last[df_last['得意先名']== option_customer]
    total_now = cust_now['金額'].sum()
    total_last = cust_last['金額'].sum()
    cost_now = cust_now['原価金額'].sum()
    cost_last = cust_last['原価金額'].sum()
    cost_last2 = f'{(total_last-cost_last)/total_last*100: 0.1f} %'
    diff = f'{((total_now-cost_now)/total_now*100) - ((total_last-cost_last)/total_last*100): 0.1f} %'
    with col1:
        st.metric('粗利率', value=f'{(total_now-cost_now)/total_now*100: 0.1f} %', delta=diff)
        st.caption(f'前年 {cost_last2}')
    with col2:
        aroma_now = cust_now[cust_now['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        aroma_last = cust_last[cust_last['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        aroma_last2 = '{:,}'.format(aroma_last)
        aroma_diff = '{:,}'.format(aroma_now- aroma_last)
        st.metric('きつつき森の研究所関連', value=('{:,}'.format(aroma_now)), delta=aroma_diff)
        st.caption(f'前年 {aroma_last2}')

def color():
    df_now_cust = df_now[df_now['得意先名']==option_customer]
    df_last_cust = df_last[df_last['得意先名']==option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # ***塗色別売り上げ ***
        color_now = df_now_cust.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        #color_now2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 塗色別売上(今期)')

        # グラフ
        fig_color_now = go.Figure()
        fig_color_now.add_trace(
            go.Bar(
                x=color_now.index,
                y=color_now,
                )
        )
        fig_color_now.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_color_now, use_container_width=True)

    with col2:
        # ***塗色別売り上げ ***
        color_last = df_last_cust.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        #color_last2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 塗色別売上(前期)')

        # グラフ
        fig_color_last = go.Figure()
        fig_color_last.add_trace(
            go.Bar(
                x=color_last.index,
                y=color_last,
                )
        )
        fig_color_last.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_color_last, use_container_width=True)    

    with col1:    
        # グラフ　塗色別売り上げ
        st.markdown('###### 塗色別売上構成比(今期)')
        fig_color_now2 = go.Figure(
            data=[
                go.Pie(
                    labels=color_now.index,
                    values=color_now
                    )])
        fig_color_now2.update_layout(
            showlegend=True, #凡例表示
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_color_now2.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_color_now2, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col2:    
        # グラフ　塗色別売り上げ
        st.markdown('###### 塗色別売上構成比(前期)')
        fig_color_last2 = go.Figure(
            data=[
                go.Pie(
                    labels=color_last.index,
                    values=color_last
                    )])
        fig_color_last2.update_layout(
            showlegend=True, #凡例表示
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_color_last2.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_color_last2, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

def category_color():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]
    categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
    categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # ***塗色別売り上げ ***
        color_now = categorybase_cust_now.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        #color_now2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 塗色別売上(今期)')

        # グラフ
        fig_color_now = go.Figure()
        fig_color_now.add_trace(
            go.Bar(
                x=color_now.index,
                y=color_now,
                )
        )
        fig_color_now.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_color_now, use_container_width=True)

    with col2:
        # ***塗色別売り上げ ***
        color_last = categorybase_cust_last.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        #color_last2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 塗色別売上(前期)')

        # グラフ
        fig_color_last = go.Figure()
        fig_color_last.add_trace(
            go.Bar(
                x=color_last.index,
                y=color_last,
                )
        )
        fig_color_last.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_color_last, use_container_width=True)    

    with col1:    
        # グラフ　塗色別売り上げ
        st.markdown('###### 塗色別売上構成比(今期)')
        fig_color_now2 = go.Figure(
            data=[
                go.Pie(
                    labels=color_now.index,
                    values=color_now
                    )])
        fig_color_now2.update_layout(
            showlegend=True, #凡例表示
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_color_now2.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_color_now2, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col2:    
        # グラフ　塗色別売り上げ
        st.markdown('###### 塗色別売上構成比(前期)')
        fig_color_last2 = go.Figure(
            data=[
                go.Pie(
                    labels=color_last.index,
                    values=color_last
                    )])
        fig_color_last2.update_layout(
            showlegend=True, #凡例表示
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_color_last2.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_color_last2, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            
def category_fabric():
     # *** selectbox***
    category = ['ダイニングチェア', 'リビングチェア']
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]
    categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
    categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]
    categorybase_cust_now = categorybase_cust_now[categorybase_cust_now['張地'] != ''] #空欄を抜いたdf作成
    categorybase_cust_last = categorybase_cust_last[categorybase_cust_last['張地'] != '']

    col1, col2 = st.columns(2)
    with col1:
        # ***張地別売り上げ ***
        fabric_now = categorybase_cust_now.groupby('張地')['金額'].sum().sort_values(ascending=False).head(12) #降順
        #fabric2 = fabric_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 張地別売上(今期)')

        # グラフ
        fig_fabric_now = go.Figure()
        fig_fabric_now.add_trace(
            go.Bar(
                x=fabric_now.index,
                y=fabric_now,
                )
        )
        fig_fabric_now.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_fabric_now, use_container_width=True)

    with col2:
        # ***張地別売り上げ ***
        fabric_last = categorybase_cust_last.groupby('張地')['金額'].sum().sort_values(ascending=False).head(12) #降順
        #fabric2 = fabric_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 張地別売上(前期)')

        # グラフ
        fig_fabric_last = go.Figure()
        fig_fabric_last.add_trace(
            go.Bar(
                x=fabric_last.index,
                y=fabric_last,
                )
        )
        fig_fabric_last.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_fabric_last, use_container_width=True)    

    with col1:
        # グラフ　張地別売り上げ
        st.markdown('張地別売上構成比(今期)')
        fig_fabric_now2 = go.Figure(
            data=[
                go.Pie(
                    labels=fabric_now.index,
                    values=fabric_now
                    )])
        fig_fabric_now2.update_layout(
            legend=dict(
                x=-1, #x座標　グラフの左下(0, 0) グラフの右上(1, 1)
                y=0.99, #y座標
                xanchor='left', #x座標が凡例のどの位置を指すか
                yanchor='top', #y座標が凡例のどの位置を指すか
                ),
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_fabric_now2.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_fabric_now2, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col2:
        # グラフ　張地別売り上げ
        st.markdown('張地別売上構成比(前期)')
        fig_fabric_last2 = go.Figure(
            data=[
                go.Pie(
                    labels=fabric_last.index,
                    values=fabric_last
                    )])
        fig_fabric_last2.update_layout(
            legend=dict(
                x=-1, #x座標　グラフの左下(0, 0) グラフの右上(1, 1)
                y=0.99, #y座標
                xanchor='left', #x座標が凡例のどの位置を指すか
                yanchor='top', #y座標が凡例のどの位置を指すか
                ),
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_fabric_last2.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_fabric_last2, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅    

def series_col_fab():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]
    categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
    categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # *** シリース別塗色別売上 ***
        series_color_now = categorybase_cust_now.groupby(['シリーズ名', '塗色CD', '張地'])['金額'].sum().sort_values(ascending=False).head(20) #降順
        series_color_now2 = series_color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 売れ筋ランキング 商品分類別(今期)')
        st.table(series_color_now2)

    with col2:
        # **シリーズ別塗色別売上 ***
        series_color_last = categorybase_cust_last.groupby(['シリーズ名', '塗色CD', '張地'])['金額'].sum().sort_values(ascending=False).head(20) #降順
        series_color_last2 = series_color_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('###### 売れ筋ランキング 商品分類別(前期)')
        st.table(series_color_last2)

def remarks():
    st.markdown('##### 備考')
    st.write('12/27 回転数 リビングチェアにスツールがカウントされている')


def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '★売上 対前年比(累計)●': earnings_comparison_year,
        '★売上 対前年比(月毎)●': earnings_comparison_month,
        '★LD 前年比/構成比●': living_dining_comparison,
        '★LD シリーズ別/売上構成比●': living_dining_comparison_ld,
        'シリーズ別 売上/構成比●': series,
        '★回転数 商品分類別●': item_count_category,
        '回転数 シリーズ別●': item_count_series,
        '★回転数 商品分類別 月毎●': category_count_month,
        '回転数 シリーズ別 月毎●': series_count_month,
        '比率 リビング/ダイニング●': living_dining_latio,
        '★比率 北海道工場/節あり材/国産材●': hokkaido_fushi_kokusanzai, 
        '★比率 粗利/アロマ関連●': profit_aroma,
        '塗色別　売上構成比': color,
        '塗色別 売上/構成比/商品分類別●': category_color,
        '張地別 売上/構成比●': category_fabric,
        '売れ筋ランキング 商品分類別/塗色/張地●': series_col_fab,
        '備考': remarks,
  
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