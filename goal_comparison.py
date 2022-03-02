import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st

# ***ファイルアップロード 今期***
uploaded_file = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df = DataFrame()
if uploaded_file:
    df = pd.read_excel(
    uploaded_file, sheet_name='受注委託移動在庫生産照会', usecols=[6, 15, 46]) #index　ナンバー不要　index_col=0
    # 出荷日/金額/営業担当者名
else:
    st.info('今期のファイルを選択してください。')

df['出荷月'] = df['出荷日'].dt.month

month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
goal_list = [7600000, 8400000, 7500000, 7400000, 7700000, 10500000, 8900000, 8800000, 8900000, 10000000, 8000000, 9300000]
last_year = [9803714, 9799641, 9545046, 7456769, 6069782, 9681984, 9212780, 9574734, 7219333, 10388374, 7057112, 10563832]

def goal_comparison_culc():

    sales = []

    df_kh = df[df['営業担当者名']=='星川 和博']
    for month in month_list:
        sales_month =df_kh[df_kh['出荷月']==month]['金額'].sum()
        sales.append(sales_month)

    df_result_g = pd.DataFrame(list(zip(goal_list, sales, last_year )), index=month_list, columns=['目標', '今期売上', '前期売上'])
    df_result_g['対目標比'] = df_result_g['今期売上'] / df_result_g['目標']
    df_result_g['対目標差'] = df_result_g['今期売上'] - df_result_g['目標']
    df_result_g['累計(目標)'] = df_result_g['目標'].cumsum()
    df_result_g['累計(今期売上)'] = df_result_g['今期売上'].cumsum()
    df_result_g['累計(対目標比)'] = df_result_g['累計(今期売上)'] / df_result_g['累計(目標)']
    df_result_g['累計(対目標差)'] = df_result_g['累計(今期売上)'] - df_result_g['累計(目標)']

    df_result_g['対目標比'] = df_result_g['対目標比'].map('{:.1%}'.format)
    df_result_g['累計(対目標比)'] = df_result_g['累計(対目標比)'].map('{:.1%}'.format)

    df_result_g['目標'] = df_result_g['目標'].astype(int).apply('{:,}'.format)
    df_result_g['今期売上'] = df_result_g['今期売上'].astype(int).apply('{:,}'.format)
    df_result_g['前期売上'] = df_result_g['前期売上'].astype(int).apply('{:,}'.format)
    df_result_g['対目標差'] = df_result_g['対目標差'].astype(int).apply('{:,}'.format)
    df_result_g['累計(目標)'] = df_result_g['累計(目標)'].astype(int).apply('{:,}'.format)
    df_result_g['累計(今期売上)'] = df_result_g['累計(今期売上)'].astype(int).apply('{:,}'.format)
    df_result_g['累計(対目標差)'] = df_result_g['累計(対目標差)'].astype(int).apply('{:,}'.format)

    st.markdown('###### 対目標')
    st.table(df_result_g)

def last_comparison_culc():

    sales = []

    df_kh = df[df['営業担当者名']=='星川 和博']
    for month in month_list:
        sales_month =df_kh[df_kh['出荷月']==month]['金額'].sum()
        sales.append(sales_month)

    df_result_l = pd.DataFrame(list(zip(goal_list, sales, last_year )), index=month_list, columns=['目標', '今期売上', '前期売上'])
    df_result_l['対前期比'] = df_result_l['今期売上'] / df_result_l['前期売上']
    df_result_l['対前期差'] = df_result_l['今期売上'] - df_result_l['前期売上']
    df_result_l['累計(前期売上)'] = df_result_l['前期売上'].cumsum()
    df_result_l['累計(今期売上)'] = df_result_l['今期売上'].cumsum()
    df_result_l['累計(対前期比)'] = df_result_l['累計(今期売上)'] / df_result_l['累計(前期売上)']
    df_result_l['累計(対前期差)'] = df_result_l['累計(今期売上)'] - df_result_l['累計(前期売上)']

    df_result_l['対前期比'] = df_result_l['対前期比'].map('{:.1%}'.format)
    df_result_l['累計(対前期比)'] = df_result_l['累計(対前期比)'].map('{:.1%}'.format)

    df_result_l['目標'] = df_result_l['目標'].astype(int).apply('{:,}'.format)
    df_result_l['今期売上'] = df_result_l['今期売上'].astype(int).apply('{:,}'.format)
    df_result_l['前期売上'] = df_result_l['前期売上'].astype(int).apply('{:,}'.format)
    df_result_l['対前期差'] = df_result_l['対前期差'].astype(int).apply('{:,}'.format)
    df_result_l['累計(前期売上)'] = df_result_l['累計(前期売上)'].astype(int).apply('{:,}'.format)
    df_result_l['累計(今期売上)'] = df_result_l['累計(今期売上)'].astype(int).apply('{:,}'.format)
    df_result_l['累計(対前期差)'] = df_result_l['累計(対前期差)'].astype(int).apply('{:,}'.format)

    st.markdown('###### 対前期')
    st.table(df_result_l)

def another_members():
    sales = []
    df_members = pd.DataFrame(index=month_list)
    
    members = ['渡辺 臣', '葛西 伸一', '瀬野尾 真里子']

    for member in members:
        df_mem = df[df['営業担当者名']==member]
        for month in month_list:
            mem_month =df_mem[df_mem['出荷月']==month]['金額'].sum()
            sales.append(mem_month)
        df_members[member] = sales
        sales = []
    df_members['累計(渡辺 臣)'] = df_members['渡辺 臣'].cumsum()
    df_members['累計(葛西 伸一)'] = df_members['葛西 伸一'].cumsum()
    df_members['累計(瀬野尾 真里子)'] = df_members['瀬野尾 真里子'].cumsum()  


    df_members['渡辺 臣'] = df_members['渡辺 臣'].astype(int).apply('{:,}'.format)
    df_members['葛西 伸一'] = df_members['葛西 伸一'].astype(int).apply('{:,}'.format)
    df_members['瀬野尾 真里子'] = df_members['瀬野尾 真里子'].astype(int).apply('{:,}'.format)
    df_members['累計(渡辺 臣)'] = df_members['累計(渡辺 臣)'].astype(int).apply('{:,}'.format)
    df_members['累計(葛西 伸一)'] = df_members['累計(葛西 伸一)'].astype(int).apply('{:,}'.format)
    df_members['累計(瀬野尾 真里子)'] = df_members['累計(瀬野尾 真里子)'].astype(int).apply('{:,}'.format)   

    st.markdown('###### 北日本') 
    st.table(df_members)   




def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '対目標（出荷ベース）': goal_comparison_culc, 
        '対前年（出荷ベース）': last_comparison_culc,
        '北日本': another_members
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