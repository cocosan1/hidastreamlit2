import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='ranking')
st.markdown('#### 品番別分析')

# ***ファイルアップロード***
uploaded_file = st.sidebar.file_uploader('Excel', type='xlsx', key='xlsx')
df = DataFrame()
if uploaded_file:
    df = pd.read_excel(
    uploaded_file, sheet_name='受注委託移動在庫生産照会', usecols=[2, 8, 9, 10, 15, 31, 42, 50, 51]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')
    st.stop()
    
df['数量'] = df['数量'].fillna(0).astype('int64')
df['金額'] = df['金額'].fillna(0).astype('int64')
df['原価金額'] = df['原価金額'].fillna(0).astype('int64')

df['得意先CD2'] = df['得意先CD'].map(lambda x:str(x)[0:5])
df['商品コード2'] = df['商品コード'].map(lambda x: x.split()[0])
df['張地'] = df['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
df2 = df[df['商品分類名2'].isin(['ダイニングチェア', 'リビングチェア'])]

def ranking():
    # *** selectbox 商品分類2***
    category = ['ダイニングチェア', 'リビングチェア']
    option_category = st.selectbox(
        'category:',
        category,   
    )
    df_cate = df2[df2['商品分類名2']==option_category]

    # *** selectbox シリーズ名***
    series_list = df_cate['シリーズ名'].unique()
    option_series = st.selectbox(
        'series:',
        series_list,   
    )
    df_cate_seri = df_cate[df_cate['シリーズ名']==option_series]
    
    with st.form('入力フォーム'):
        hinban_list = df_cate_seri['商品コード2'].unique()
        option_hinban = st.selectbox(
            'code:',
            hinban_list,
        )
        df_cate_seri_code = df_cate_seri[df_cate_seri['商品コード2']==option_hinban]

        # *** selectbox 塗色***
        color_list = df_cate_seri_code['塗色CD'].unique()
        option_color = st.selectbox(
            'color:',
            color_list,   
        )
        st.form_submit_button('submit')
        
    df_cate_seri_code_col = df_cate_seri_code[df_cate_seri_code['塗色CD']==option_color]
    df_cate_seri_code_col = df_cate_seri_code_col[df_cate_seri_code_col['張地'] != ''] #空欄を抜いたdf作成

    df_result= df_cate_seri_code_col.groupby(['張地'])['数量'].sum().sort_values(ascending=False).head(12)

    # グラフ　張布売り上げ
    st.write('ランキング 張地別')
    fig_fabric = go.Figure()
    fig_fabric.add_trace(
        go.Bar(
            x=df_result.index,
            y=df_result,
            )
    )
    fig_fabric.update_layout(
        height=500,
        width=2000,
    )        
    
    st.plotly_chart(fig_fabric, use_container_width=True)
    st.caption('※ダイニングチェアの場合、張地空欄は板座')

def profit():
    hinban = st.text_input('品番を入力', 'SG261A')
    
    # cate_list = df['商品分類名2'].unique()
    # option_category = st.selectbox(
    #     '商品分類:',
    #     cate_list,   
    # )
    # df_cate = df[df['商品分類名2']==option_category]

    # seri_list = df_cate['シリーズ名'].unique()
    # option_series = st.selectbox(
    #     'シリーズ名:',
    #     seri_list,   
    # )
    # df_cate_seri = df_cate[df_cate['シリーズ名']==option_series]

    # hinban_list = df_cate_seri['商品コード2'].unique()
    # option_hinban = st.selectbox(
    #     '品番:',
    #     hinban_list, 
    # )
    kingaku_mean = df[df['商品コード2']==hinban]['金額'].mean()
    genka_mean = df[df['商品コード2']==hinban]['原価金額'].mean()
    st.metric('粗利率', value=(f'{(kingaku_mean-genka_mean)/kingaku_mean*100:0.1f} %'))
    # st.write(f'{(kingaku_mean-genka_mean)/kingaku_mean*100:0.1f} %')









def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'ランキング 張地': ranking,
        '品番別粗利率': profit,
        
        
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
