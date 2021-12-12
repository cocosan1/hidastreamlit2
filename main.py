import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='test')
st.title('売り上げ分析')
st.subheader('エクセルファイルを読み込ませてください')

# ***ファイルアップロード***
uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')
df = DataFrame()
if uploaded_file:
    st.markdown('---')
    df = pd.read_excel(
    uploaded_file, sheet_name='受注委託移動在庫生産照会', usecols=[10, 14, 15, 28, 31, 42, 50, 51, 52], index_col=0)
    df['金額'] = df['金額'].astype(int)

total = df['金額'].sum()

def color_fabric():
    # *** selectbox 商品分類2***
    category = df['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df[df['商品分類名2']==option_category]

    col1, col2 = st.columns(2)

    with col1:
        # ***塗色別売り上げ ***
        color = categorybase.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
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
        fabric = categorybase.groupby('張布CD')['金額'].sum().sort_values(ascending=False).head(25) #降順
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
    category = df['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df[df['商品分類名2']==option_category]

    col1, col2 = st.columns(2)

    with col1:
        # ***シリーズ別売り上げ ***
        series = categorybase.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(25) #降順
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
    category = df['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df[df['商品分類名2']==option_category]

    col1, col2 = st.columns(2)

    with col1:
        # *** シリース別塗色別売上 ***
        series_color = categorybase.groupby(['シリーズ名', '塗色CD'])['金額'].sum().sort_values(ascending=False) #降順
        series_color2 = series_color.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('シリース別塗色別売上')
        st.dataframe(series_color2)

    with col2:
        # **シリーズ別塗色別売上 ***
        series_color_fab = categorybase.groupby(['シリーズ名', '塗色CD', '張布CD'])['金額'].sum().sort_values(ascending=False).head(25) #降順
        series_color_fab2 = series_color_fab.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.write('シリーズ別塗色別張地別売上')
        st.dataframe(series_color_fab2)

def series_col_fab2():
    # *** selectbox 商品分類2***
    category = df['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.write('選択した項目: ', option_category)
    categorybase = df[df['商品分類名2']==option_category]

    # ***シリーズベース ***
    # *** selectbox 商品分類2***
    series_list = df['シリーズ名'].unique()
    option_series = st.selectbox(
        'series:',
        series_list,   
    ) 
    st.write('You selected: ', option_series) 

    seriesbase = categorybase[categorybase['シリーズ名']==option_series]
    seriesbase_col_fab = seriesbase.groupby(['塗色CD', '張布CD'])['金額'].sum().sort_values(ascending=False)

    st.write('塗色別張地別売上')
    st.caption('※ダイニングチェアの場合、張地空欄は板座')
    st.dataframe(seriesbase_col_fab)

def hokkaido_fushi_kokusanzai():
    # *** 北海道比率　節材比率　国産材比率 ***
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hokkaido = df[df['出荷倉庫']==510]['金額'].sum()
        st.metric('北海道工場比率', value=f'{hokkaido/total*100: 0.1f} %') #小数点以下1ケタ
        st.caption(f'{hokkaido} 円')
        st.caption(f'売り上げ合計：{total} 円')
    with col2:
        fushi = df[df['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        # sdソファ拾えていない isin その値を含む行　true
        st.metric('節材比率', value=f'{fushi/total*100: 0.1f} %') #小数点以下1ケタ
        st.caption(f'{fushi} 円')
        st.caption('森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
    with col3:
        kokusanzai = df[df['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum() #SHSカバ拾えていない
        st.metric('国産材比率', value=f'{kokusanzai/total*100: 0.1f} %') #小数点以下1ケタ
        st.caption(f'{kokusanzai} 円')
        st.caption('北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた/Kinoe')

def living_dining_latio():
    col1, col2, col3 = st.columns(3)
    with col1:
        living = df[df['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        st.metric('リビング比率', value=f'{living/total*100: 0.1f} %')
        st.caption(f'{living} 円')
        st.caption('クッション/リビングチェア/リビングテーブル')
        st.caption(f'売り上げ合計：{total} 円')
    with col2:
        dining = df[df['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        st.metric('ダイニング比率', value=f'{dining/total*100: 0.1f} %')
        st.caption(f'{dining} 円')  
        st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')
    with col3:
        sonota = df[df['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
         'デスク', '小物・その他'])]['金額'].sum()
        st.metric('その他比率', value=f'{sonota/total*100: 0.1f} %') 
        st.caption(f'{sonota} 円')  
        st.caption('キャビネット類/その他テーブル/雑品・特注品/その他椅子/デスク/小物・その他')

def profit_aroma():
    col1, col2 = st.columns(2)
    with col1:
        cost = df['原価金額'].sum()
        st.metric('粗利率', value=f'{(total-cost)/total*100: 0.1f} %')
    with col2:
        aroma = df[df['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        st.metric('きつつき森の研究所関連', value=('{:,}'.format(aroma)))

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '塗色/張地　売り上げ': color_fabric,
        'シリーズ別売上/構成比': series,
        'シリーズ別 塗色/張地': series_col_fab,
        'シリーズ別 塗色/張地 詳細': series_col_fab2,
        '比率　北海道工場/節材': hokkaido_fushi_kokusanzai,
        'リビング・ダイニング比率' :living_dining_latio,
        '粗利/きつつき森の研究所　売り上げ': profit_aroma, 
    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

if __name__ == '__main__':
    main()