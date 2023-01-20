import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
# from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析（全体）')
st.markdown('#### 売り上げ分析（全体)')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
        uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51])  # index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')


# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = pd.read_excel(
        uploaded_file_last, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 43, 50, 51])
else:
    st.info('前期のファイルを選択してください。')
    st.stop()

# *** 出荷月、受注月列の追加***
df_now['出荷月'] = df_now['出荷日'].dt.month
df_now['受注月'] = df_now['受注日'].dt.month
df_now['商品コード2'] = df_now['商　品　名'].map(lambda x: x.split()[0]) #品番
df_now['商品コード3'] = df_now['商　品　名'].map(lambda x: str(x)[0:2]) #頭品番
df_now['張地'] = df_now['商　品　名'].map(
    lambda x: x.split()[2] if len(x.split()) >= 4 else '')
df_last['出荷月'] = df_last['出荷日'].dt.month
df_last['受注月'] = df_last['受注日'].dt.month
df_last['商品コード2'] = df_last['商　品　名'].map(lambda x: x.split()[0])
df_last['商品コード3'] = df_last['商　品　名'].map(lambda x: str(x)[0:2]) #頭品番
df_last['張地'] = df_last['商　品　名'].map(
    lambda x: x.split()[2] if len(x.split()) >= 4 else '')

# ***INT型への変更***
df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_now[[
    '数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める
df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']] = df_last[[
    '数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月', '受注月']].fillna(0).astype('int64')
#fillna　０で空欄を埋める

df_now_total = df_now['金額'].sum()
df_last_total = df_last['金額'].sum()

def earnings_comparison_year():
    
    total_comparison = f'{df_now_total / df_last_total * 100: 0.1f} %'
    total_diff = '{:,}'.format(df_now_total - df_last_total)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('今期売上', value= '{:,}'.format(df_now_total), delta=total_diff) # ★delta使いたい
    with col2:
        st.metric('前期売上', value= '{:,}'.format(df_last_total))
    with col3:
        st.metric('対前年比', value= total_comparison)

def earnings_comparison_month():
    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    sales_now = []
    sales_last = []
    df_month = pd.DataFrame(index=month_list)

    for month in month_list:
        sales_now_month =df_now[df_now['受注月']==month]['金額'].sum()
        sales_last_month =df_last[df_last['受注月']==month]['金額'].sum()

        sales_now.append(sales_now_month)
        sales_last.append(sales_last_month)

    df_month['今期売上'] = sales_now
    df_month['前期売上'] = sales_last

    df_month['対前期比'] = df_month['今期売上'] / df_month['前期売上']
    df_month['対前期差'] = df_month['今期売上'] - df_month['前期売上']
    df_month['累計(前期売上)'] = df_month['前期売上'].cumsum()
    df_month['累計(今期売上)'] = df_month['今期売上'].cumsum()
    df_month['累計(対前期比)'] = df_month['累計(今期売上)'] / df_month['累計(前期売上)']
    df_month['累計(対前期差)'] = df_month['累計(今期売上)'] - df_month['累計(前期売上)']

    df_month['対前期比'] = df_month['対前期比'].map('{:.1%}'.format)
    df_month['累計(対前期比)'] = df_month['累計(対前期比)'].map('{:.1%}'.format)

    df_month['今期売上'] = df_month['今期売上'].astype(int).apply('{:,}'.format)
    df_month['前期売上'] = df_month['前期売上'].astype(int).apply('{:,}'.format)
    df_month['対前期差'] = df_month['対前期差'].astype(int).apply('{:,}'.format)
    df_month['累計(前期売上)'] = df_month['累計(前期売上)'].astype(int).apply('{:,}'.format)
    df_month['累計(今期売上)'] = df_month['累計(今期売上)'].astype(int).apply('{:,}'.format)
    df_month['累計(対前期差)'] = df_month['累計(対前期差)'].astype(int).apply('{:,}'.format)

    st.markdown('###### 月別売上')
    st.table(df_month)



def living_dining_latio():
    col1, col2, col3 = st.columns(3)
    with col1:
        living_now = df_now[df_now['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_last = df_last[df_last['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_diff = f'{(living_now/df_now_total*100) - (living_last/df_last_total*100): 0.1f} %'
        st.metric('リビング比率', value=f'{living_now/df_now_total*100: 0.1f} %', delta=living_diff)
        st.caption(f'前年 {living_last/df_last_total*100: 0.1f} %')
        st.caption('クッション/リビングチェア/リビングテーブル')
    with col2:
        dining_now = df_now[df_now['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_last = df_last[df_last['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_diff = f'{(dining_now/df_now_total*100) - (dining_last/df_last_total*100): 0.1f} %'
        st.metric('ダイニング比率', value=f'{dining_now/df_now_total*100: 0.1f} %', delta=dining_diff)
        st.caption(f'前年 {dining_last/df_last_total*100: 0.1f} %') 
        st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')
    with col3:
        sonota_now = df_now[df_now['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
         'デスク', '小物・その他'])]['金額'].sum()
        sonota_last = df_last[df_last['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
         'デスク', '小物・その他'])]['金額'].sum()
        sonota_diff = f'{(sonota_now/df_now_total*100) - (sonota_last/df_last_total*100): 0.1f} %'
        st.metric('その他比率', value=f'{sonota_now/df_now_total*100: 0.1f} %', delta=sonota_diff) 
        st.caption(f'前年 {sonota_last/df_last_total*100: 0.1f} %') 
        st.caption('キャビネット類/その他テーブル/雑品・特注品/その他椅子/デスク/小物・その他')

def living_dining_comparison_ld():

    # *** selectbox LD***
    category = ['リビング', 'ダイニング']
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    if option_category == 'リビング':
        df_now_cate = df_now[df_now['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        df_last_cate = df_last[df_last['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
    elif option_category == 'ダイニング':
        df_now_cate = df_now[df_now['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
        df_last_cate = df_last[df_last['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]

    index = []
    now_result = []
    last_result = []
    diff = []
    ratio = []
    series_list = df_now_cate['シリーズ名'].unique()
    
    for series in series_list:
        index.append(series)
        now_culc = df_now_cate[df_now_cate['シリーズ名']==series]['金額'].sum()
        last_culc = df_last_cate[df_last_cate['シリーズ名']==series]['金額'].sum()
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

def hokkaido_fushi_kokusanzai():
    # *** 北海道比率　節材比率　国産材比率 ***
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hokkaido_now = df_now[df_now['出荷倉庫']==510]['金額'].sum()
        hokkaido_last = df_last[df_last['出荷倉庫']==510]['金額'].sum()
        hokkaido_diff = f'{(hokkaido_now/df_now_total*100) - (hokkaido_last/df_last_total*100): 0.1f} %'
        st.metric('北海道工場比率', value=f'{hokkaido_now/df_now_total*100: 0.1f} %', delta=hokkaido_diff) #小数点以下1ケタ
        st.caption(f'前年 {hokkaido_last/df_last_total*100: 0.1f} %')
    with col2:
        fushi_now = df_now[df_now['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        # sdソファ拾えていない isin その値を含む行　true
        fushi_last = df_last[df_last['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
        '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        fushi_diff = f'{(fushi_now/df_now_total*100) - (fushi_last/df_last_total*100): 0.1f} %'
        st.metric('節材比率', value=f'{fushi_now/df_now_total*100: 0.1f} %', delta=fushi_diff) #小数点以下1ケタ
        st.caption(f'前年 {fushi_last/df_last_total*100: 0.1f} %')
        st.caption('森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
    with col3:
        kokusanzai_now1 = df_now[df_now['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]['金額'].sum() #SHSカバ拾えていない
        kokusanzai_last1 = df_last[df_last['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
        '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]['金額'].sum() #SHSカバ拾えていない

        kokusanzai_now2 = df_now[df_now['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]['金額'].sum()
        kokusanzai_last2 = df_last[df_last['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]['金額'].sum()
        
        kokusanzai_now3 = df_now[df_now['商品コード3']=='HJ']['金額'].sum()
        kokusanzai_last3 = df_last[df_last['商品コード3']=='HJ']['金額'].sum()

        kokusanzai_now_t = kokusanzai_now1 + kokusanzai_now2 + kokusanzai_now3
        kokusanzai_last_t = kokusanzai_last1 + kokusanzai_last2 + kokusanzai_last3 

        kokusanzai_diff = f'{(kokusanzai_now_t/df_now_total*100) - (kokusanzai_last_t/df_last_total*100): 0.1f} %'
        st.metric('国産材比率', value=f'{kokusanzai_now_t/df_now_total*100: 0.1f} %', delta=kokusanzai_diff) #小数点以下1ケタ
        st.caption(f'前年 {kokusanzai_last_t/df_last_total*100: 0.1f} %')
        st.caption('北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた/Kinoe/SUWARI/KURINOKI/HJ/SG261M/\
            SG261(K/C/M)/SG261A(K/C/M)/KD201(K/C/M)/KD201A(K/C/M)')
        # st.caption('ｿﾌｨｵ SUGI/風のうた/Kinoe/SUWARI/KURINOKI/HJ/SG261M/')
        # st.caption('SG261(K/C/M)/SG261A(K/C/M)/KD201(K/C/M)/KD201A(K/C/M)')

def profit_aroma():
    col1, col2 = st.columns(2)
    with col1:
        cost_now = df_now['原価金額'].sum()
        cost_last = df_last['原価金額'].sum()
        cost_diff = f'{((df_now_total-cost_now)/df_now_total*100) - ((df_last_total-cost_last)/df_last_total*100): 0.1f} %'
        st.metric('粗利率', value=f'{(df_now_total-cost_now)/df_now_total*100: 0.1f} %', delta=cost_diff)
        st.caption(f'前年 {(df_last_total-cost_last)/df_last_total*100: 0.1f} %')
    with col2:
        aroma_now = df_now[df_now['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        aroma_last = df_last[df_last['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
        aroma_last2 = '{:,}'.format(aroma_last)
        aroma_diff = '{:,}'.format(aroma_now - aroma_last)
        st.metric('きつつき森の研究所関連', value=('{:,}'.format(aroma_now)), delta=aroma_diff)
        st.caption(f'前年 {aroma_last2}')

def color():
    # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.caption('下段 構成比')
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]

    # ***塗色別売り上げ ***
    color_now = categorybase_now.groupby('塗色CD')['金額'].sum().sort_values(ascending=False).head(12) #降順
    color_now2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

    # ***塗色別売り上げ ***
    color_last = categorybase_last.groupby('塗色CD')['金額'].sum().sort_values(ascending=False).head(12) #降順
    color_last2 = color_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

    col1, col2 = st.columns(2)   

    with col1:
        # グラフ　シリーズ別売り上げ
        st.write('シリーズ別塗色別売上(今期)')
        fig_series = go.Figure()
        fig_series.add_trace(
            go.Bar(
                x=color_now.index,
                y=color_now,
                )
        )
        fig_series.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_series, use_container_width=True)

    with col2:
        # グラフ　シリーズ別売り上げ
        st.write('シリーズ別塗色別売上(前期)')
        fig_series = go.Figure()
        fig_series.add_trace(
            go.Bar(
                x=color_last.index,
                y=color_last,
                )
        )
        fig_series.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_series, use_container_width=True)    

    with col1:    
        # グラフ　塗色別売り上げ
        st.write('塗色別売上構成比(今期)')
        fig_color = go.Figure(
            data=[
                go.Pie(
                    labels=color_now.index,
                    values=color_now
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

    with col2:    
        # グラフ　塗色別売り上げ
        st.write('塗色別売上(前期)構成比')
        fig_color = go.Figure(
            data=[
                go.Pie(
                    labels=color_last.index,
                    values=color_last
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
           
def fabric():
    # *** selectbox ***
    category = ['ダイニングチェア', 'リビングチェア']
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    st.caption('下段 構成比')
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]
    
    # categorybase_now = categorybase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除
    # categorybase_last = categorybase_last.dropna(subset=['張地'])

    categorybase_now = categorybase_now[categorybase_now['張地'] != ''] #空欄を抜いたdf作成
    categorybase_last = categorybase_last[categorybase_last['張地'] != '']

    # ***張地別売り上げ ***
    fabric_now = categorybase_now.groupby('張地')['金額'].sum().sort_values(ascending=False).head(10) #降順
    fabric_now2 = fabric_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
    
    # ***張地別売り上げ ***
    fabric_last = categorybase_last.groupby('張地')['金額'].sum().sort_values(ascending=False).head(10) #降順
    fabric_last2 = fabric_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

    col1, col2 = st.columns(2)

    with col1:
        # グラフ　シリーズ別売り上げ
        st.write('シリーズ別張地別売上(今期)')
        fig_series = go.Figure()
        fig_series.add_trace(
            go.Bar(
                x=fabric_now.index,
                y=fabric_now,
                )
        )
        fig_series.update_layout(
            height=500,
            width=800,
        )        
        
        st.plotly_chart(fig_series, use_container_width=True)

    with col2:
        # グラフ　シリーズ別売り上げ
        st.write('シリーズ別張地別売上(前期)')
        fig_series = go.Figure()
        fig_series.add_trace(
            go.Bar(
                x=fabric_last.index,
                y=fabric_last,
                )
        )
        fig_series.update_layout(
            height=500,
            width=800,
        )        
        
        st.plotly_chart(fig_series, use_container_width=True)           

    with col1:
        # グラフ　張地別売り上げ
        st.write('張地別売上構成比(今期)')
        fig_fabric = go.Figure(
            data=[
                go.Pie(
                    labels=fabric_now.index,
                    values=fabric_now
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

    with col2:
        # グラフ　張地別売り上げ
        st.write('張地別売上構成比(前期)')
        fig_fabric = go.Figure(
            data=[
                go.Pie(
                    labels=fabric_last.index,
                    values=fabric_last
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
    st.caption('下段 構成比')
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_last = df_last[df_last['商品分類名2']==option_category]

    # ***シリーズ別売り上げ ***
    series_now = categorybase_now.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(12) #降順
    series_last = categorybase_last.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(12) #降順
    series_now2 = series_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
    series_last2 = series_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
    # *** DF シリーズ別売り上げ ***

    col1, col2 = st.columns(2)
    
    with col1:
        # グラフ　シリーズ別売り上げ
        st.write('シリーズ別売上(今期)')
        fig_series = go.Figure()
        fig_series.add_trace(
            go.Bar(
                x=series_now.index,
                y=series_now,
                )
        )
        fig_series.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_series, use_container_width=True)

    with col2:
        # グラフ　シリーズ別売り上げ
        st.write('シリーズ別売上(前期)')
        fig_series = go.Figure()
        fig_series.add_trace(
            go.Bar(
                x=series_last.index,
                y=series_last,
                )
        )
        fig_series.update_layout(
            height=500,
            width=2000,
        )        
        
        st.plotly_chart(fig_series, use_container_width=True)   

    with col1:
        # グラフ　シリーズ別売り上げ構成比
        st.write('シリーズ別売り上げ構成比(今期)')
        fig_series_ratio = go.Figure(
            data=[
                go.Pie(
                    labels=series_now.index,
                    values=series_now
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

    with col2:
        # グラフ　シリーズ別売り上げ構成比
        st.write('シリーズ別売り上げ構成比(前期)')
        fig_series_ratio = go.Figure(
            data=[
                go.Pie(
                    labels=series_last.index,
                    values=series_last
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

def series_col_fab():
     # *** selectbox 商品分類2***
    category = df_now['商品分類名2'].unique()
    option_category = st.selectbox(
        'category:',
        category,   
    ) 
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    categorybase_now = categorybase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除

    categorybase_now2 = categorybase_now.groupby(['シリーズ名', '塗色CD', '張地'])['金額'].sum().sort_values(ascending=False).head(20)
    categorybase_now2 = categorybase_now2.apply('{:,}'.format)
    st.dataframe(categorybase_now2)

def series_col_fab2():

    with st.form('入力フォーム'):
        # *** selectbox 商品分類2***
        category = ['ダイニングチェア', 'リビングチェア']
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        
        # *** selectbox シリーズ名***
        series_list = df_now['シリーズ名'].unique()
        option_series = st.selectbox(
            'series:',
            series_list,   
        )  

        # *** selectbox 塗色名***
        color_list = df_now['塗色CD'].unique()
        option_color = st.selectbox(
            'color:',
            color_list,   
        )

        submitted = st.form_submit_button('submit')
        
    categorybase_now = df_now[df_now['商品分類名2']==option_category]
    seriesbase_now = categorybase_now[categorybase_now['シリーズ名']==option_series]    

    colorbase_now = seriesbase_now[seriesbase_now['塗色CD']==option_color]
    colorbase_now = colorbase_now[colorbase_now['張地'] != '']
    # colorbase_now = colorbase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除

    colorbase_now2 = colorbase_now.groupby(['張地'])['金額'].sum().sort_values(ascending=False).head(10)

    # グラフ　張布売り上げ
    st.write('張地売り上げ 商品分類/シリース別/塗色別(今期)')
    fig_fabric = go.Figure()
    fig_fabric.add_trace(
        go.Bar(
            x=colorbase_now2.index,
            y=colorbase_now2,
            )
    )
    fig_fabric.update_layout(
        height=500,
        width=2000,
    )        
    
    st.plotly_chart(fig_fabric, use_container_width=True)
    st.caption('※ダイニングチェアの場合、張地空欄は板座')

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '売上 前年比●': earnings_comparison_year,
        '売上 月別': earnings_comparison_month,
        '比率 リビング/ダイニング●' :living_dining_latio,
        'LD シリーズ別/売上構成比': living_dining_comparison_ld,
        '比率 北海道工場/節材/国産材●': hokkaido_fushi_kokusanzai,
        '粗利/売上 きつつき森の研究所●': profit_aroma,
        '塗色別 売上/構成比 (商品分類別)●': color,
        '張地別 売上/構成比 (商品分類別)●': fabric,
        'シリーズ別 売上/構成比●': series,
        '売れ筋ランキング 商品分類別/シリーズ別 塗色/張地●': series_col_fab,
        '張地ランキング 商品分類別/シリーズ別/塗色別●': series_col_fab2,
        
    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))
    link = '[home](http://linkpagetest.s3-website-ap-northeast-1.amazonaws.com/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.caption('homeに戻る')                                       

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

if __name__ == '__main__':
    main()
