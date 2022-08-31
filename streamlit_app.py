from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import yfinance as yf
from sklearn import preprocessing
import numpy as np
st.title("American Agricultural Economy Barometer")
st.subheader("Surveying the state of the agriculture industry on a monthly basis")
st.caption("Data sources include Ag Economy Barometer Indices produced by Perdue Univeristy and key Agricultural input and output prices.")
### format ag barometer data
df = pd.read_html("https://ag.purdue.edu/commercialag/ageconomybarometer/tables/")[0]
df['Month/Year.1'] = df['Month/Year.1'].apply(lambda x: str(x))
df['Date'] = df['Month/Year'] +'-'+ df['Month/Year.1']
df['Date'] = pd.to_datetime(df['Date'])
df = df.drop(['Month/Year', 'Month/Year.1'], axis=1)
#######
### get yahoo finance data
data = yf.download(
        # tickers list or string as well
        tickers = "UFV=F ZC=F ZS=F LE=F DC=F HE=F NG=F",

        #LE=F is live cattle futures
        # DC=F is milk futures
        # HE=F is lean hog futures
        period = "max",
        interval = "1mo",
        group_by = 'column',
        auto_adjust = True,
        prepost = True,
    )
data = data['Close'].rename(columns={"DC=F":"Milk Futures (DC-F)", "HE=F" :"Lean Hog Futures (HE=F)",
                              "LE=F": "Live Cattle Futures (LE=F)",
                              "UFV=F":"Urea (Granular) FOB US Gulf Fut (UFV=F)",
                              "ZS=F":"Soybean Futures,Nov-2022 (ZS=F)",
                              "NG=F": "Natural Gas Oct 22 (NG=F)",
                              "ZC=F":"Corn Futures,Dec-2022 (ZC=F)"})



#merge dataframes
total_data = data.reset_index().merge(df, how='left')
# normalize data
#create scaled dataframe
total_data = total_data.set_index('Date')
scaled_df = preprocessing.normalize(total_data.fillna(0), axis=0)
scaled_df = pd.DataFrame(scaled_df, columns=total_data.columns, index =total_data.index).replace({0:np.NaN}).reset_index()
total_data = total_data.reset_index()
barometer_list = ['Purdue/CME Ag Economy Barometer',
 'Index of Current Conditions',
 'Index of Future Expectations',
 'Farm Capital Investment Index']
####
# correlations df
corr_df = scaled_df[scaled_df['Date']>'2010-10-01'].rename(columns={"DC=F":"Milk Futures (DC-F)", "HE=F" :"Lean Hog Futures (HE=F)",
                              "LE=F": "Live Cattle Futures (LE=F)",
                              "UFV=F":"Urea (Granular) FOB US Gulf Fut (UFV=F)",
                              "ZS=F":"Soybean Futures,Nov-2022 (ZS=F)",
                              "NG=F": "Natural Gas Oct 22 (NG=F)",
                              "ZC=F":"Corn Futures,Dec-2022 (ZC=F)"}).corr().drop(barometer_list, axis=0)
###functions
def display_data(norm):
    if norm:
        return scaled_df
    else :
        return total_data
#frontend

indicators = st.multiselect('Agricultural Economic Indicators', list(total_data.drop('Date', axis=1).columns))
norm = st.checkbox('Normalize Economic Indicators')
st.text("Ag Economy Indicators, by month")
st.line_chart(data = display_data(norm), x= 'Date' , y = indicators)
st.text("Ag Economy Indicator Data Table")
st.dataframe(display_data(norm).set_index('Date'))
st.subheader('Historically, Farmer Setiment Is Assocated with Key Agricultural Commodity Prices')
st.text('Correlation Between Ag Economy Barometer Indices and Key Ag Commodity Prices')
radio = st.radio('Ag Barometer Index', ['Purdue/CME Ag Economy Barometer',
 'Index of Current Conditions',
 'Index of Future Expectations',
 'Farm Capital Investment Index'], index=0, horizontal=True)
bar_df = corr_df[radio].sort_values()
st.bar_chart(data=bar_df)
col1, col2 = st.columns([4, 1])
col1.text('Data Sources: Purdue Ag Barometer and Yahoo Finance')
col2.text('By Sam Kobrin')


