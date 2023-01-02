import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
# from streamlit.state.session_state import Value

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
df['商品コード2'] = df['商品コード'].map(lambda x: x.split()[0]) #品番


df['張地'] = df['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
df['HTSサイズ'] = df['張地'].map(lambda x: x.split('x')[0]) #HTSサイズ
df['HTS形状'] = df['商　品　名'].map(lambda x: x.split()[1] if len(x.split()) >= 4 else '') #HTS天板形状


df2 = df[df['商品分類名2'].isin(['ダイニングチェア', 'リビングチェア'])]

def ranking_series():
    # *** selectbox 商品分類2***
    category = ['リビングチェア', 'ダイニングチェア']
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
        
    df_cate_seri = df_cate_seri[df_cate_seri['張地'] != ''] #空欄を抜いたdf作成

    df_result= df_cate_seri.groupby(['張地'])['数量'].sum().sort_values(ascending=False).head(12)

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

def ranking_item():
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

def hts_width():
    st.markdown('###### 侭サイズ　一覧')
    df_hts = df[df['商品コード2']=='HTS2']
    size_list = df_hts['HTSサイズ'].unique() #張地だがサイズを拾える

    cnt_list = []
    index = []

    for size in size_list:
        index.append(size)
        cnt = df_hts[df_hts['HTSサイズ']==size]['数量'].sum()
        cnt_list.append(cnt)

    df_size = pd.DataFrame(index=index)
    df_size['数量'] = cnt_list
    df_size = df_size.sort_values(by='数量', ascending=False)
    df_size2 = df_size.head(12)

    col1, col2 = st.columns(2)

    with col1:
        st.table(df_size)

    with col2:    
    # グラフ　シリーズ別売り上げ
        fig_size = go.Figure()
        fig_size.add_trace(
            go.Bar(
                x=df_size2.index,
                y=df_size2['数量'],
                )
        )
        fig_size.update_layout(
            height=500,
            width=2000,
        )        
        st.plotly_chart(fig_size, use_container_width=True)

def hts_shape():
    st.markdown('###### 天板形状　一覧')
    df_hts = df[df['商品コード2']=='HTS2']
    shape_list = df_hts['HTS形状'].unique()

    cnt_list = []
    index = []

    for shape in shape_list:
        index.append(shape)
        cnt = df_hts[df_hts['HTS形状']==shape]['数量'].sum()
        cnt_list.append(cnt)

    df_shape = pd.DataFrame(index=index)
    df_shape['数量'] = cnt_list
    df_shape = df_shape.sort_values(by='数量', ascending=False)
    df_shape2 = df_shape.head(12)

    col1, col2 = st.columns(2)

    with col1:
        st.table(df_shape)

    with col2:    
    # グラフ　シリーズ別売り上げ
        fig_shape = go.Figure()
        fig_shape.add_trace(
            go.Bar(
                x=df_shape2.index,
                y=df_shape2['数量'],
                )
        )
        fig_shape.update_layout(
            height=500,
            width=2000,
        )        
        st.plotly_chart(fig_shape, use_container_width=True)


def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'ランキング シリーズ': ranking_series,
        'ランキング アイテム': ranking_item,
        '品番別粗利率': profit,
        '侭　サイズランキング': hts_width,
        '侭　天板形状ランキング': hts_shape,
          
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
