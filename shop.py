import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import openpyxl
from streamlit.state.session_state import Value

st.set_page_config(page_title='売り上げ分析 Shop')
st.markdown('#### 売り上げ分析 Shop')

# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = pd.read_excel(
    uploaded_file_now, sheet_name='受注委託移動在庫生産照会', usecols=[3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 43, 50, 51]) #index　ナンバー不要　index_col=0
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

def emp_earnings():
    st.markdown('###### 担当者別売上')
    selected_base = st.radio('出荷ベース/受注ベースの選択', ('出荷ベース', '受注ベース'))
    
    if selected_base == '出荷ベース':
        selected_base = '出荷月'
    else:
        selected_base = '受注月'

    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]
    month_sum_list = []
    emp_sum_list = []
    emps = df_now['取引先担当'].unique()
    df_emp_earn = pd.DataFrame(index=month_list)

    selected_emp = st.multiselect('表示する担当者を選択', emps)

    df_total = pd.DataFrame(index=selected_emp)
    
    for emp in selected_emp:

        df_now_emp = df_now[df_now['取引先担当']==emp]
        emp_sum = df_now_emp['金額'].sum()
        emp_sum_list.append(emp_sum)
        
        for month in month_list:
            sum_emp_month = df_now_emp[df_now_emp[selected_base]==month]['金額'].sum()
            month_sum_list.append('{:,}'.format(sum_emp_month))
        df_emp_earn[emp] = month_sum_list
        month_sum_list = []
    df_total['売上'] = emp_sum_list 

    col1, col2 = st.columns(2)
    with col1:
        # グラフ
        st.markdown('###### 担当者別構成比')
        fig_ratio = go.Figure(
            data=[
                go.Pie(
                    labels=df_total.index,
                    values=df_total['売上']
                    )])
        fig_ratio.update_layout(
            showlegend=True, #凡例表示
            height=200,
            margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
            )
        fig_ratio.update_traces(textposition='inside', textinfo='label+percent') 
        #inside グラフ上にテキスト表示
        st.plotly_chart(fig_ratio, use_container_width=True) 
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    with col2:
        st.markdown('###### 売上合計')
        st.table(df_total)
    st.markdown('###### 売上月別') 
    st.table(df_emp_earn)


def hokkai_ratio_month():
    col1, col2 =st.columns(2)
    with col1:
        st.markdown('###### 北海道工場比率')
        selected_base = st.radio('出荷ベース/受注ベースの選択', ('出荷ベース', '受注ベース'))
        
        if selected_base == '出荷ベース':
            selected_base = '出荷月'
        else:
            selected_base = '受注月'

    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    kokusan_now_list = []
    kokusan_last_list = []
    kokusan_diff_list = []

    for month in month_list:
        df_now_month = df_now[df_now[selected_base]==month]
        df_last_month = df_last[df_last[selected_base]==month]

        now_month_sum = df_now_month['金額'].sum()
        last_month_sum = df_last_month['金額'].sum()


        kokusan_now = df_now_month[df_now_month['出荷倉庫']==510]['金額'].sum()
        kokusan_last = df_last_month[df_last_month['出荷倉庫']==510]['金額'].sum()
        kokusan_now_ratio = f'{(kokusan_now/now_month_sum*100): 0.1f} %'
        kokusan_last_ratio = f'{(kokusan_last/last_month_sum*100): 0.1f} %'
        kokusan_diff = f'{(kokusan_now/now_month_sum*100) - (kokusan_last/last_month_sum*100): 0.1f} %'

        kokusan_now_list.append(kokusan_now_ratio)
        kokusan_last_list.append(kokusan_last_ratio)
        kokusan_diff_list.append(kokusan_diff)

    df_fushi = pd.DataFrame(index=month_list)
    df_fushi['今期'] = kokusan_now_list
    df_fushi['前期'] = kokusan_last_list
    df_fushi['対前年差'] = kokusan_diff_list

    fushi_now_sum = df_now[df_now['出荷倉庫']==510]['金額'].sum()
    fushi_last_sum = df_last[df_last['出荷倉庫']==510]['金額'].sum()
    fushi_diff_sum = f'{(fushi_now_sum/df_now_total*100) - (fushi_last_sum/df_last_total*100): 0.1f} %'
    
    st.markdown('###### 北海道工場比率')
    with col1:
        st.metric('今期比率', value=f'{fushi_now_sum/df_now_total*100: 0.1f} %', delta=fushi_diff_sum) #小数点以下1ケタ
        st.caption(f'前期 {fushi_last_sum/df_last_total*100: 0.1f} %')

    with col2:
        st.markdown('###### 月別比率')
        st.table(df_fushi)

def fushi_ratio_month():
    col1, col2 =st.columns(2)
    with col1:
        st.markdown('###### 節材比率')
        selected_base = st.radio('出荷ベース/受注ベースの選択', ('出荷ベース', '受注ベース'))
        
        if selected_base == '出荷ベース':
            selected_base = '出荷月'
        else:
            selected_base = '受注月'

    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    kokusan_now_list = []
    kokusan_last_list = []
    kokusan_diff_list = []

    for month in month_list:
        df_now_month = df_now[df_now[selected_base]==month]
        df_last_month = df_last[df_last[selected_base]==month]

        now_month_sum = df_now_month['金額'].sum()
        last_month_sum = df_last_month['金額'].sum()


        kokusan_now = df_now_month[df_now_month['シリーズ名'].isin(['森のことば', '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        kokusan_last = df_last_month[df_last_month['シリーズ名'].isin(['森のことば', '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
        kokusan_now_ratio = f'{(kokusan_now/now_month_sum*100): 0.1f} %'
        kokusan_last_ratio = f'{(kokusan_last/last_month_sum*100): 0.1f} %'
        kokusan_diff = f'{(kokusan_now/now_month_sum*100) - (kokusan_last/last_month_sum*100): 0.1f} %'

        kokusan_now_list.append(kokusan_now_ratio)
        kokusan_last_list.append(kokusan_last_ratio)
        kokusan_diff_list.append(kokusan_diff)

    df_fushi = pd.DataFrame(index=month_list)
    df_fushi['今期'] = kokusan_now_list
    df_fushi['前期'] = kokusan_last_list
    df_fushi['対前年差'] = kokusan_diff_list

    fushi_now_sum = df_now[df_now['シリーズ名'].isin(['森のことば', '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
    fushi_last_sum = df_last[df_last['シリーズ名'].isin(['森のことば', '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
    fushi_diff_sum = f'{(fushi_now_sum/df_now_total*100) - (fushi_last_sum/df_last_total*100): 0.1f} %'
    
    st.markdown('###### 節材比率')
    with col1:
        st.metric('今期比率', value=f'{fushi_now_sum/df_now_total*100: 0.1f} %', delta=fushi_diff_sum) #小数点以下1ケタ
        st.caption(f'前期 {fushi_last_sum/df_last_total*100: 0.1f} %')
        st.caption('森のことば/森のことばIBUKI/森のことば ウォルナット')

    with col2:
        st.markdown('###### 月別比率')
        st.table(df_fushi)

def kokusan_ratio_month():
    col1, col2 =st.columns(2)
    with col1:
        st.markdown('###### 国産材比率')
        selected_base = st.radio('出荷ベース/受注ベースの選択', ('出荷ベース', '受注ベース'))
        
        if selected_base == '出荷ベース':
            selected_base = '出荷月'
        else:
            selected_base = '受注月'

    month_list = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    kokusan_now_list = []
    kokusan_last_list = []
    kokusan_diff_list = []

    for month in month_list:
        df_now_month = df_now[df_now[selected_base]==month]
        df_last_month = df_last[df_last[selected_base]==month]

        now_month_sum = df_now_month['金額'].sum()
        last_month_sum = df_last_month['金額'].sum()


        kokusan_now = df_now_month[df_now_month['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum()
        kokusan_last = df_last_month[df_last_month['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum()
        kokusan_now_ratio = f'{(kokusan_now/now_month_sum*100): 0.1f} %'
        kokusan_last_ratio = f'{(kokusan_last/last_month_sum*100): 0.1f} %'
        kokusan_diff = f'{(kokusan_now/now_month_sum*100) - (kokusan_last/last_month_sum*100): 0.1f} %'

        kokusan_now_list.append(kokusan_now_ratio)
        kokusan_last_list.append(kokusan_last_ratio)
        kokusan_diff_list.append(kokusan_diff)

    df_fushi = pd.DataFrame(index=month_list)
    df_fushi['今期'] = kokusan_now_list
    df_fushi['前期'] = kokusan_last_list
    df_fushi['対前年差'] = kokusan_diff_list

    fushi_now_sum = df_now[df_now['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum()
    fushi_last_sum = df_last[df_last['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe'])]['金額'].sum()
    fushi_diff_sum = f'{(fushi_now_sum/df_now_total*100) - (fushi_last_sum/df_last_total*100): 0.1f} %'
    
    with col1:
        st.metric('今期比率', value=f'{fushi_now_sum/df_now_total*100: 0.1f} %', delta=fushi_diff_sum) #小数点以下1ケタ
        st.caption(f'前期 {fushi_last_sum/df_last_total*100: 0.1f} %')
        st.caption('北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた/Kinoe')

    with col2:
        st.markdown('###### 月別比率')
        st.table(df_fushi)

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '担当別月別売上/出荷ベース': emp_earnings,
        '比率 北海道工場': hokkai_ratio_month,
        '比率 節材': fushi_ratio_month,
        '比率 国産材': kokusan_ratio_month,
        
        
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


