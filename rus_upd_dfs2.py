#!/usr/bin/env python
# coding: utf-8
#--------------------Библиотеки----------------------------------
from io import BytesIO
import pandas as pd
import requests
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
#--------------------/Библиотеки---------------------------------- 


#--------------------Таблицы-------------------------------------------------------------------------
#--------------------------------сложная тема---------------------------
def create_most_dif_df():
    r = requests.get('https://docs.google.com/spreadsheets/d/1x85oldnFJr2SqHQhvhTVYj08T62FbIiwL9ub2QB9TZY/export?format=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data), index_col=0).reset_index()
    df.columns = ['timestamp','gender','age','city','most_difficult_theme','quality_rate','job_rate','review']
    df['timestamp']= pd.to_datetime(df['timestamp'], format='%d.%m.%Y %H:%M:%S')
    df['day'] = df['timestamp'].astype('datetime64[D]')
    most_dif = df.groupby('most_difficult_theme')['most_difficult_theme'].count()
    most_dif.name = 'count'
    most_dif = most_dif.reset_index()
    return most_dif
#--------------------------------/сложная тема---------------------------
#--------------------------------рейтинг--------------------------------
def create_rating_df():
    r = requests.get('https://docs.google.com/spreadsheets/d/1x85oldnFJr2SqHQhvhTVYj08T62FbIiwL9ub2QB9TZY/export?format=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data), index_col=0).reset_index()
    df.columns = ['timestamp','gender','age','city','most_difficult_theme','quality_rate','job_rate','review']
    df['timestamp']= pd.to_datetime(df['timestamp'], format='%d.%m.%Y %H:%M:%S')
    df['day'] = df['timestamp'].astype('datetime64[D]')
    df['review'].fillna(df.review.mean(),inplace=True)
    df['pr_rate']= df.quality_rate*df.job_rate*df.review
    # Таблица со средними рейтингами по дням
    pr_rate_per_day = df.groupby('day')['pr_rate'].mean().round(2).reset_index()
    return pr_rate_per_day 
def create_df():
    r = requests.get('https://docs.google.com/spreadsheets/d/1x85oldnFJr2SqHQhvhTVYj08T62FbIiwL9ub2QB9TZY/export?format=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data), index_col=0).reset_index()
    df.columns = ['timestamp','gender','age','city','most_difficult_theme','quality_rate','job_rate','review']
    df['timestamp']= pd.to_datetime(df['timestamp'], format='%d.%m.%Y %H:%M:%S')
    df['day'] = df['timestamp'].astype('datetime64[D]')
    df['review'].fillna(df.review.mean(),inplace=True)
    df['pr_rate']= df.quality_rate*df.job_rate*df.review
    return df
#--------------------------------/рейтинг---------------------------------
#--------------------------------Карта-----------------------------------
def create_map_df():
    r = requests.get('https://docs.google.com/spreadsheets/d/1x85oldnFJr2SqHQhvhTVYj08T62FbIiwL9ub2QB9TZY/export?format=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data), index_col=0).reset_index()
    df.columns = ['timestamp','gender','age','city','most_difficult_theme','quality_rate','job_rate','review']
    df['timestamp']= pd.to_datetime(df['timestamp'], format='%d.%m.%Y %H:%M:%S')
    df['day'] = df['timestamp'].astype('datetime64[D]')
    df['review'].fillna(df.review.mean(),inplace=True)
    df['pr_rate']= df.quality_rate*df.job_rate*df.review
    list_of_cities = df['city']
    token_Geocoder = 'c29e4b87-39fb-4f54-9689-ccc8cec48cd7'
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey={}&geocode='.format(token_Geocoder)
    coordinates1 = []
    coordinates2 = []
    for city in list_of_cities:
        if city == city: # чтоб не столкнуться с nan
            url_formatted = url + city
            response = requests.get(url_formatted).json()
            data1 = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'].get('pos')
            coordinate1 = (float(data1.split()[1]))
            coordinate2 = (float(data1.split()[0]))
            coordinates1.append(coordinate1)
            coordinates2.append(coordinate2)
        else:
            coordinates.append('')
    df['x'] = coordinates1
    df['y'] = coordinates2
    size = df.groupby('city')['city'].count()
    size.name = 'size'
    df = df.merge(size,on = 'city')
    return df
#--------------------------------/Карта-----------------------------------
#--------------------/Таблицы-------------------------------------------------------------------------


#---------------------словарь цветов-----------------------------
colors = {
    'background': '#27292d',
    'H':'white',
    'text': '#e8f0fc',
    'lines' :'red',
    'grid' : '#59616e'
}
#---------------------/словарь цветов----------------------------- 
 
#---------------------CSS + app---------------------------------- 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#---------------------/CSS + app---------------------------------- 
 
#--------------------------------------------------------layout-------------------------------------------------------
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(
    html.Div([
    html.H4(children = '''DA5 cohort''',style=
            {
            'textAlign': 'center',
            'color': colors['text'],
            'margin-bottom' : '0',
            'padding-top' : '90px',
            #'font-style' : 'italic',
            #'font-family' : 'William',
            'font-size' : '15',
            'font-weight' : 'light'
            }
),
        dcc.Graph(#style = {'width': '45vw'},
            id='1live-update-graph'),
        dcc.Graph(id='live-update-graph'),
        dcc.Graph(id='map'),
        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        ),
        dcc.Interval(
            id='map-interval-component',
            interval=20*60000, #(каждые 20 минут, наверное можно сделать еще больше период)
            n_intervals=0
        )
    ])
)
])

#----------------------rating_plot--------------------------------------
 
@app.callback(Output('1live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    pr_rate_per_day = create_rating_df()
    df = create_df()
    # логика для рэйтинга
    pr_day_rate = pr_rate_per_day.iloc[-2,1]
    last_day_rate = pr_rate_per_day.iloc[-1,1]
#-------------------------------------
    data=[go.Indicator(mode = 'number+delta',
                       value = last_day_rate,
                       delta = {"reference": pr_day_rate, "valueformat": ".0f"},
                                title = {"text": "Praktikum rate"},
                                domain = {'y': [0, 1], 'x': [0.25, 0.75]}
                       ),
         go.Scatter(
                                 x = df['timestamp'],
                                 y = df['pr_rate'],
                                 line=dict(color="crimson"),name = 'rate'
         ),
         go.Scatter(
                                x=list(df.timestamp),
                                y=([df['pr_rate'].mean()] * len(df.timestamp)),
                                line=dict(color="#6b648f", dash="dash"),name = 'mean')]
         
    layout = go.Layout(plot_bgcolor=colors['background'],
                       paper_bgcolor = colors['background'],
                       font=dict(color=colors['text']),
                       xaxis=dict(gridcolor=colors['grid'],
                                 showgrid=False),
                       yaxis=dict(gridcolor=colors['grid']),
                       xaxis_rangeslider_visible=True
                      )
    fig = go.Figure(data=data, layout=layout)
    #fig.add_shape(go.layout.Shape(type="line", x0=df.loc[14,'timestamp'], y0=0, x1=df.loc[14,'timestamp'], y1=650, line=dict(color='green')))
   
    return fig
#----------------------/rating_plot--------------------------------------

#----------------------diff_theme_plot-----------------------------------
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])


def update_graph_live(n):
    most_dif = create_most_dif_df()
    most_dif = most_dif.reset_index().sort_values(ascending = False, by='count')
    
    # логика для диффзем
    x = most_dif['most_difficult_theme']
    y = most_dif['count']
    colorss = ['lightslategray',] * 5
    colorss[0] = 'crimson'
#--------------------diff_theme-------------------
    
    data=[go.Bar(x=x,
                 y=y,
            text=most_dif['count'].sort_values(ascending = False),
            textposition='outside',
            marker_color=colorss)]
    layout = go.Layout(plot_bgcolor=colors['background'],
                       paper_bgcolor = colors['background'],
                       font=dict(color=colors['text']),
                       xaxis=dict(gridcolor=colors['grid'],
                                 showgrid=False),
                       yaxis=dict(gridcolor=colors['grid'])
                      )
    fig = go.Figure(data=data, layout=layout)
    #fig.add_shape(go.layout.Shape(type="line", x0=df.loc[14,'timestamp'], y0=0, x1=df.loc[14,'timestamp'], y1=650, line=dict(color='green')))
   
    return fig
#----------------------/diff_theme_plot----------------------------------
#----------------------map_plot-----------------------------------------
@app.callback(Output('map', 'figure'),
              [Input('map-interval-component', 'n_intervals')])
def update_graph_live(n):
    df = create_map_df()
    # логика для карты
    mapbox_access_token =   "pk.eyJ1IjoiYWxiZWw5OTk5IiwiYSI6ImNrNmI0M2NydTA1YjAzZnBha2dtcnJ1YmYifQ.7H3jZRqSGUnb88yeLgkN_A"
    
#-------------------------------------


    data = [go.Scattermapbox(lat=df['x'], lon=df['y'],
                              mode='markers+text',
                              hovertext=df['size'],
                              textfont=dict(color='#e8f0fc'),
                              marker=dict(size=df['size']+20,
                              color = 'crimson'),
                              text=df['city'])]

    layout = go.Layout(mapbox_style='dark',
                        autosize=True,
                        hovermode='closest',
                        mapbox=dict(accesstoken=mapbox_access_token,
                                    bearing=0,
                                    center=dict(lat=55, lon=62),
                                    pitch=0, zoom=2.3),
                                    plot_bgcolor = colors['background'],
                                    paper_bgcolor = colors['background'])

    fig = go.Figure(data=data, layout=layout)
    #fig.add_shape(go.layout.Shape(type="line", x0=df.loc[14,'timestamp'], y0=0, x1=df.loc[14,'timestamp'], y1=650, line=dict(color='green')))
   
    return fig
#----------------------/map_plot----------------------------------------
#--------------------------------------------------------/layout-------------------------------------------------------   
    
def run_server(self,
               port=8050,
               debug=True,
               threaded=True,
               **flask_run_options):
    self.server.run(port=port, debug=debug, **flask_run_options)
 
 
# условная конструкция и запуск
if __name__ == '__main__':
    app.run_server(debug=True, port=8099) # or whatever you choose