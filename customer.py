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
st.title('売り上げ分析（得意先別）')

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

# *** selectbox 得意先名***
customer = df_now['得意先名'].unique()
option_customer = st.selectbox(
    '得意先名:',
    customer,   
) 
st.write('選択した得意先名: ', option_customer)

df_now_cust =df_now[df_now['得意先名']==option_customer]
df_last_cust =df_last[df_last['得意先名']==option_customer]
df_now_cust_total = df_now_cust['金額'].sum()

def earnings_comparison_year():
    total_cust_now = df_now[df_now['得意先名']==option_customer]['金額'].sum()
    total_cust_last = df_last[df_last['得意先名']==option_customer]['金額'].sum()
    total_comparison = f'{total_cust_now / total_cust_last * 100: 0.1f} %'
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('今期売上', value= '{:,}'.format(total_cust_now))
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
        earnings_month_now = df_now_cust[df_now_cust['出荷月'].isin([month])]['金額'].sum()
        earnings_month_last = df_last_cust[df_last_cust['出荷月'].isin([month])]['金額'].sum()
        earnings_diff_culc = earnings_month_now - earnings_month_last
        earnings_rate_culc = f'{earnings_month_now / earnings_month_last * 100: 0.1f} %'

        earnings_now.append('{:,}'.format(earnings_month_now))
        earnings_last.append('{:,}'.format(earnings_month_last))
        earnings_diff.append('{:,}'.format(earnings_diff_culc))
        earnings_rate.append(earnings_rate_culc)

    df_earnings_month = pd.DataFrame(list(zip(earnings_now, earnings_last, earnings_diff, earnings_rate)), columns=columns_list, index=month_list)

    st.dataframe(df_earnings_month)
    
def living_dining_comparison():
    st.subheader('LD　前年比/構成比')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write('リビング')
        living_now = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_last = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        st.metric('売り上げ（今期）', value=('{:,}'.format(living_now)))
        st.metric('売り上げ（前期）', value=('{:,}'.format(living_last)))
        st.metric('対前年差', value=('{:,}'.format(living_now-living_last)))
        st.metric('対前年比', value=f'{living_now/living_last*100:0.1f} %')
        st.caption('クッション/リビングチェア/リビングテーブル')
    with col2:
        st.write('ダイニング')
        dining_now = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_last = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        st.metric('売り上げ（今期）', value=('{:,}'.format(dining_now)))
        st.metric('売り上げ（前期）', value=('{:,}'.format(dining_last)))
        st.metric('対前年差', value=('{:,}'.format(dining_now-dining_last)))
        st.metric('対前年比', value=f'{dining_now/dining_last*100:0.1f} %')
        st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')
    with col3:
        else_now = df_now_cust[df_now_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
         'デスク', '小物・その他'])]['金額'].sum()
        st.write('構成比')
        st.metric('リビング　(今期)',f'{living_now/df_now_cust_total*100:0.1f} %')
        st.metric('ダイニング　(今期)',f'{dining_now/df_now_cust_total*100:0.1f} %')
        st.metric('その他　(今期)',f'{else_now/df_now_cust_total*100:0.1f} %')

def color_fabric():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df_now[df_now['商品分類名2']==option_category]
    categorybase_cust = categorybase[categorybase['得意先名']== option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # ***塗色別売り上げ ***
        color = categorybase_cust.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        color2 = color.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('塗色別売上')
        st.dataframe(color2)

    with col2:    
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
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_color.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_color, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

    with col1:
        # ***張地別売り上げ ***
        fabric = categorybase_cust.groupby('張布CD')['金額'].sum().sort_values(ascending=False).head(25) #降順
        fabric2 = fabric.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('張地別売上')
        st.caption('※ダイニングチェアの場合、空欄は板座')
        st.dataframe(fabric2)

    with col2:
        # グラフ　張地別売り上げ
        st.write('グラフ　張地別売上')
        st.caption('※ダイニングチェアの場合、空欄の凡例をクリックして消してください')
        fig_fabric = go.Figure(
            data=[
                go.Pie(
                    labels=fabric.index,
                    values=fabric
                    )])
        fig_fabric.update_layout(
            legend=dict(
                x=-1, #x座標　グラフの左下(0, 0) グラフの右上(1, 1)
                y=0.99, #y座標
                xanchor='left', #x座標が凡例のどの位置を指すか
                yanchor='top', #y座標が凡例のどの位置を指すか
                ),
            height=290,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_fabric.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_fabric, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅

def series():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df_now[df_now['商品分類名2']==option_category]
    categorybase_cust = categorybase[categorybase['得意先名']== option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # ***シリーズ別売り上げ ***
        series = categorybase_cust.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(25) #降順
        series2 = series.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        # *** DF シリーズ別売り上げ ***
        st.write('シリーズ別売上')
        st.dataframe(series2)

    with col2:
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

    # グラフ　シリーズ別売り上げ
    st.write('グラフ　シリーズ別売上')
    fig_series = go.Figure()
    fig_series.add_trace(
        go.Bar(
            x=series.index,
            y=series,
            )
    )
    fig_series.update_layout(
        height=500,
        width=2000,
    )        
    
    st.plotly_chart(fig_series, use_container_width=True)

def series_col_fab():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df_now[df_now['商品分類名2']==option_category]
    categorybase_cust = categorybase[categorybase['得意先名']== option_customer]

    col1, col2 = st.columns(2)

    with col1:
        # *** シリース別塗色別売上 ***
        series_color = categorybase_cust.groupby(['シリーズ名', '塗色CD'])['金額'].sum().sort_values(ascending=False) #降順
        series_color2 = series_color.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('シリース別塗色別売上')
        st.dataframe(series_color2)

    with col2:
        # **シリーズ別塗色別売上 ***
        series_color_fab = categorybase_cust.groupby(['シリーズ名', '塗色CD', '張布CD'])['金額'].sum().sort_values(ascending=False).head(25) #降順
        series_color_fab2 = series_color_fab.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('シリーズ別塗色別張地別売上')
        st.dataframe(series_color_fab2)

def series_col_fab2():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df_now[df_now['商品分類名2']==option_category]
    categorybase_cust = categorybase[categorybase['得意先名']== option_customer]

    # ***シリーズベース ***
    # *** selectbox 商品分類2***
    series_list = df_now['シリーズ名'].unique()
    option_series = st.selectbox(
        'series:',
        series_list,   
    ) 
    st.write('You selected: ', option_series) 

    seriesbase = categorybase_cust[categorybase['シリーズ名']==option_series]
    seriesbase_col_fab = seriesbase.groupby(['塗色CD', '張布CD'])['金額'].sum().sort_values(ascending=False)

    st.write('塗色別張地別売上')
    st.caption('※ダイニングチェアの場合、張地空欄は板座')
    st.dataframe(seriesbase_col_fab)

def hokkaido_fushi_kokusanzai():
    # *** 北海道比率　節材比率　国産材比率 ***
    col1, col2, col3 = st.columns(3)
    cust = df_now[df_now['得意先名']== option_customer]
    total = cust['金額'].sum()
    with col1:
        hokkaido = cust[cust['出荷倉庫']==510]['金額'].sum()

        st.metric('北海道工場比率', value=f'{hokkaido/total*100: 0.1f} %') #小数点以下1ケタ
        st.caption(f'{hokkaido} 円')
        st.caption(f'売り上げ合計：{total} 円')
    with col2:
        fushi = cust[cust['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        # sdソファ拾えていない isin その値を含む行　true
        st.metric('節材比率', value=f'{fushi/total*100: 0.1f} %') #小数点以下1ケタ
        st.caption(f'{fushi} 円')
        st.caption('森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
    with col3:
        kokusanzai = cust[cust['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum() #SHSカバ拾えていない
        st.metric('国産材比率', value=f'{kokusanzai/total*100: 0.1f} %') #小数点以下1ケタ
        st.caption(f'{kokusanzai} 円')
        st.caption('北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた/Kinoe')

def living_dining_latio():
    col1, col2, col3 = st.columns(3)
    cust = df_now[df_now['得意先名']== option_customer]
    total = cust['金額'].sum()
    with col1:
        living = cust[cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        st.metric('リビング比率', value=f'{living/total*100: 0.1f} %')
        st.caption(f'{living} 円')
        st.caption('クッション/リビングチェア/リビングテーブル')
        st.caption(f'売り上げ合計：{total} 円')
    with col2:
        dining = cust[cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        st.metric('ダイニング比率', value=f'{dining/total*100: 0.1f} %')
        st.caption(f'{dining} 円')  
        st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')
    with col3:
        sonota = cust[cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
        'デスク', '小物・その他'])]['金額'].sum()
        st.metric('その他比率', value=f'{sonota/total*100: 0.1f} %') 
        st.caption(f'{sonota} 円')  
        st.caption('キャビネット類/その他テーブル/雑品・特注品/その他椅子/デスク/小物・その他')

def profit_aroma():
    col1, col2 = st.columns(2)
    cust = df_now[df_now['得意先名']== option_customer]
    total = cust['金額'].sum()
    with col1:
        cost = cust['原価金額'].sum()
        st.metric('粗利率', value=f'{(total-cost)/total*100: 0.1f} %')
    with col2:
        aroma = cust[cust['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        st.metric('きつつき森の研究所関連', value=('{:,}'.format(aroma)))

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '売上　対前年比': earnings_comparison_year,
        '売り上げ　対前年比　月毎': earnings_comparison_month,
        'LD　前年比/構成比': living_dining_comparison,
        '商品分類別売り上げ 塗色/張地': color_fabric,
        'シリーズ別　売り上げ/構成比': series,
        '商品分類別シリーズ別　塗色/張地': series_col_fab,
        '商品分類別シリーズ別　塗色/張地　詳細': series_col_fab2,
        '比率　北海道工場/節あり材/国産材': hokkaido_fushi_kokusanzai,
        '比率　リビング/ダイニング': living_dining_latio,
        '比率　粗利/アロマ関連': profit_aroma,
        
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