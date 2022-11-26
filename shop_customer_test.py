import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
# from streamlit.state.session_state import Value
import datetime

st.set_page_config(page_title='顧客管理')
st.markdown('#### 顧客管理')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('顧客情報', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
        uploaded_file_now, sheet_name='Sheet1', index_col=0)  # index　ナンバー不要　index_col=0
else:
    st.info('顧客情報のファイルを選択してください。')

# ***ファイルアップロード 過去実績***
uploaded_file_past = st.sidebar.file_uploader('実績', type='xlsx', key='past')
df_past = DataFrame()
if uploaded_file_past:
    df_past = pd.read_excel(
        uploaded_file_past, sheet_name='受注委託移動在庫生産照会', usecols=[1, 3, 7, 8, 10, 14, 15, 16, 43, 44],\
            index_col=0)  # index　ナンバー不要　index_col=0
else:
    st.info('実績のファイルを選択してください。')
    st.stop()

#int化
df_past[['数量', '単価', '金額']] = df_past[['数量', '単価', '金額']].fillna(0).astype('int')

# 氏名からスペースの削除
df_now['氏名2'] = df_now['氏名'].map(lambda x: x.replace('\u3000', '')) #全角スペース削除
df_now['氏名2'] = df_now['氏名'].map(lambda x: x.replace(' ', ''))    

# 氏名からスペースの削除
df_past['得意先名2'] = df_past['得意先名'].map(lambda x: x.replace('\u3000', '')) #全角スペース削除
df_past['得意先名2'] = df_past['得意先名'].map(lambda x: x.replace(' ', '')) #半角スペース削除

#日時表示　時間分消す
df_now['来店日'] = pd.to_datetime(df_now['来店日'])
df_now['来店日'] = df_now['来店日'].dt.date
df_now['購入予定日'] = pd.to_datetime(df_now['購入予定日'])
df_now['購入予定日'] = df_now['購入予定日'].dt.date
df_past['必着日'] = pd.to_datetime(df_past['必着日'])
df_past['必着日'] = df_past['必着日'].dt.date
df_past['受注日'] = pd.to_datetime(df_past['受注日'])
df_past['受注日'] = df_past['受注日'].dt.date


def select_customer():
    name = st.text_input('氏名 ※スペースなし')
    df_now2 = df_now[df_now['氏名2']==name]
    df_past2 =df_past[df_past['得意先名2']==name]
    df_past2 = df_past2.sort_values('受注日')

    col1, col2, col3 = st.columns(3)
    with col1:
        total_sum = df_past2['金額'].sum()
        st.metric('購入金額', value='{:,}'.format(total_sum)) 
    with col2:
        buy_count= df_past2['受注日'].nunique()
        st.metric('購入回数', value=buy_count) 
    with col3:
        min_date = str(df_past2['受注日'].min())
        min_date = min_date.split(' ')[0]
        st.write('初回購入日') 
        st.write(min_date)

    #1000円単位でカンマ
    df_now2['金額'] = df_now2['金額'].map(lambda x: '{:,}'.format(x)) 
    df_past2['単価'] = df_past2['単価'].map(lambda x: '{:,}'.format(x))  
    df_past2['金額'] = df_past2['金額'].map(lambda x: '{:,}'.format(x))

    df_now2['確率'] = df_now2['確率'].map(lambda x: f'{x :0.1f}')   

    st.caption('来店情報')
    st.table(df_now2)
    st.caption('購入履歴')
    st.table(df_past2)

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        'お客様情報の抽出': select_customer,
        
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