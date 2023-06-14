#Import libraries 
import numpy as np 
import pandas as pd 
from datetime import datetime 
import plotly.graph_objects as go 
import plotly.figure_factory as ff 
from plotly.subplots import make_subplots 

#loading data into pandas dataframe 
aqi = pd.read_csv(r'air_quality_index_mumbai.csv')
temp = pd.read_csv(r'temp_and+precipitation_mumbai.csv')

#Since we are analysing data from 2022 only 
#Setting filter 
start_data = '2022-01-01'
end_date = '2022-12-31'

aqi.set_index('date',inplace=True)
aqi = aqi.resample('D').mean()
aqi = aqi.loc[start_date : end_date]

temp['time'] = pd.to_datetime(temp['time'], errors='coerce', format='%d-%m-%Y')
temp.set_index('time',inplace=True)
temp = temp.resample('D').mean()
temp = temp.loc[start_date : end_date]

#Merging the two datasets 
df = aqi.merge(temp, left_index=True, right_index=True,suffixes=('', ''),validate='1:1')

#Imputate 
df.fillna(method="ffill",inplace=True)

#View the data for further exploration 
df.head()

#Exploratory data analysis using data visualisation 

#Plotting heatmap with datetime 
pollutants = ['o3', 'pm2_5', 'pm10']
weather = ['tavg', 'prcp']
dates = df.index

#create ndarray
pol_array = []
for p in pollutants:
    pol_array.append(df[p])
pol_array = np.array(pol_array)

# create weather array
temp_array = np.array(df[weather[0]])
prcp_array = np.array(df[weather[1]])

# create a subplot
fig = make_subplots(rows=3, cols=1)

# add the pollutant heat-map
fig.append_trace(go.Heatmap(
        z=pol_array,
        x=dates,
        y=pollutants,
        colorscale='balance'), row=1, col=1)
fig.update_yaxes(title_text="pollutants", row=1, col=1)

# append the avg. temp line chart
fig.append_trace(go.Scatter(x=dates, y=temp_array,
                    mode='lines',
                    name='avgTemp'), row=2, col=1)
fig.update_yaxes(title_text="avg Temp", row=2, col=1)

# append the precipitation line chart
fig.append_trace(go.Scatter(x=dates, y=prcp_array,
                    mode='lines',
                    name='precipitation'), row=3, col=1)
fig.update_yaxes(title_text="precipitation", row=3, col=1)

fig.update_layout(
    title='Impact of Weather on AQI : Mumbai',
    title_font_size=20,
    xaxis_nticks=36,
    showlegend=False,
    yaxis = dict(
        tickmode = 'array',
        tickvals = pollutants,
        ticktext = ['Ozone', 'PM2.5', 'PM10', 'Avg Temp', 'Avg Precipitation'])
)

fig.show()

#Creating bubble chart 

# plot PM2.5

bubble_size = []
for pm in df['pm2_5']:
    if pm <= 12.5:
        bubble_size.append(20)
    elif 12.5 < pm <= 25:
        bubble_size.append(40)
    elif 25 < pm <= 50:
        bubble_size.append(60)
    elif 50 < pm <= 150:
        bubble_size.append(80)
    elif pm > 150:
        bubble_size.append(100)

pm25_pollutant = df.pm2_5.to_list()
dates = df.index

fig = go.Figure(data=[go.Scatter(
    x=dates,
    y=pm25_pollutant,
    mode='markers',
    marker=dict(
        size=bubble_size,
        color=bubble_size,
        colorscale='sunsetdark',
        showscale=True,
        sizemode='area',
        sizeref=2.*max(bubble_size)/(40.**2),
        sizemin=4
    )
)])

fig.update_layout(
    title='PM2.5 Concentration from Jan-July 2022 in Mumbai',
    title_font_size=20,
    xaxis_nticks=36,
)

fig.show()

#Plot PM10 bubble chart 
bubble_size = []
for pm in df['pm10']:
    if pm <= 40:
        bubble_size.append(20)
    elif 40 < pm <= 80:
        bubble_size.append(40)
    elif 80 < pm <= 120:
        bubble_size.append(60)
    elif 120 < pm <= 300:
        bubble_size.append(80)
    elif pm > 300:
        bubble_size.append(100)

pm10_pollutant = df.pm10.to_list()
dates = df.index

fig = go.Figure(data=[go.Scatter(
    x=dates,
    y=pm10_pollutant,
    mode='markers',
    marker=dict(
        size=bubble_size,
        color=bubble_size,
        colorscale='sunsetdark',
        showscale=True,
        sizemode='area',
        sizeref=2.*max(bubble_size)/(40.**2),
        sizemin=4
    )
)])

fig.update_layout(
    title='PM10 Concentration from Jan-July 2022 in Mumbai',
    title_font_size=20,
    xaxis_nticks=36,
)

fig.show()

#Build ternary plot 
a_list = df['tavg']
b_list = df['prcp']
c_list = df['pm10']

fig = go.Figure(go.Scatterternary(
  a=a_list,
  b=b_list,
  c=c_list,
  mode='markers',
  marker={'symbol': 100,
          'color': 'green',
          'size': 10},
))

fig.update_layout({
    'title': 'PM10 Ternary Plot from Jan-July 2022 (Mumbai)',
    'ternary':
        {
        'sum':1,
        'aaxis':{'title': 'temp', 'min': 0.01, 'linewidth':2, 'ticks':'outside' },
        'baxis':{'title': 'prcp', 'min': 0.01, 'linewidth':2, 'ticks':'outside' },
        'caxis':{'title': 'pm10', 'min': 0.01, 'linewidth':2, 'ticks':'outside' }
    },
    'showlegend': False
})

fig.show()

#Build polar plot 
#Check correlation between air quality index and the major pollutants 
corr_list = []
pollutants = ['co', 
              'no2', # from fossil fuels
              'o3', 
              'pm2_5', 
              'pm10']

for p in pollutants:
    corr = df['AQI'].corr(df[p])
    corr_list.append(round(corr,3))

# plot polar-plot
fig = go.Figure(data=go.Scatterpolar(
    r= corr_list,
  theta=['Carbon Monooxide','Nitrogen Dioxide','Ozone', 'Pm2.5','PM10'],
  fill='toself'))

fig.update_layout(polar=dict(radialaxis=dict(visible=True),)
                  ,showlegend=False
                  ,title='Correlation of AQI with major pollutants'
                  ,title_font_size=20,
                 )

fig.show()