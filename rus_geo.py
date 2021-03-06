#!/usr/bin/env python
# coding: utf-8

# импорт библиотек
from io import BytesIO
import pandas as pd
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go 
import plotly.express as px


colors = {
    'background': '#27292d',
    'H':'white',
    'text': 'e8f0fc',
    'lines' :'red',
    'grid' : '59616e'
}


# качаем нашу табличку и изменяем названия столбцов
r = requests.get('https://docs.google.com/spreadsheets/d/1x85oldnFJr2SqHQhvhTVYj08T62FbIiwL9ub2QB9TZY/export?format=csv')
data = r.content
df = pd.read_csv(BytesIO(data), index_col=0).reset_index()
df.columns = ['timestamp','gender','age','city','most_difficult_theme','quality_rate','job_rate','review']

# манипуляции с таблицой
df['timestamp']= pd.to_datetime(df['timestamp'], format='%d.%m.%Y %H:%M:%S')
df['day'] = df['timestamp'].astype('datetime64[D]')


#---------------------diff_theme-------------------
# создадим таблицу со сложными темами и кол-вом
most_dif = df.groupby('most_difficult_theme')['most_difficult_theme'].count()
most_dif.name = 'count'
most_dif = most_dif.reset_index()
# логика для диффзем
x = most_dif['most_difficult_theme']
y = most_dif['count'].sort_values(ascending = False)
colorss = ['lightslategray',] * 5
colorss[0] = 'crimson'
#--------------------diff_theme-------------------

#---------------------Рейтинг--------------------
# Временная замена на среднее 
df['review'].fillna(df.review.mean(),inplace=True)
# Столбец с рейтингом для каждого пользователя
df['pr_rate']= df.quality_rate*df.job_rate*df.review
# Таблица со средними рейтингами по дням
pr_rate_per_day = df.groupby('day')['pr_rate'].mean().round(2).reset_index()
pr_day_rate = pr_rate_per_day.iloc[-2,1]
last_day_rate = pr_rate_per_day.iloc[-1,1]
#---------------------Рейтинг--------------------

#---------------------GEO------------------------

list_of_cities = df['city']
token_Geocoder = 'c29e4b87-39fb-4f54-9689-ccc8cec48cd7'
# запускаем функцию
import requests as r
url = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey={}&geocode='.format(token_Geocoder)
coordinates1 = []
coordinates2 = []
for city in list_of_cities:
    if city == city: # чтоб не столкнуться с nan
        url_formatted = url + city
        response = r.get(url_formatted).json()
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

mapbox_access_token = "pk.eyJ1IjoiYWxiZWw5OTk5IiwiYSI6ImNrNmI0M2NydTA1YjAzZnBha2dtcnJ1YmYifQ.7H3jZRqSGUnb88yeLgkN_A"


data1 = [go.Scattermapbox(lat=df['x'], lon=df['y'],
                          mode='markers+text',
                          hovertext=df['size'],
                          textfont=dict(color='#e8f0fc'),
                          marker=dict(size=df['size']+20,
                          color = 'crimson'),
                          text=df['city'])]

layout1 = go.Layout(mapbox_style='dark',
                    autosize=True,
                    hovermode='closest',
                    mapbox=dict(accesstoken=mapbox_access_token,
                                bearing=0,
                                center=dict(lat=55, lon=62),
                                pitch=0, zoom=2.3),
                                plot_bgcolor = colors['background'],
                                paper_bgcolor = colors['background'])
    

figg = dict(data=data1, layout=layout1) 
    
#---------------------GEO------------------------



# df gender count
dfg = df.groupby('gender')['timestamp'].count().reset_index()
# df кволитирейт
q_r = df.groupby('day')['quality_rate'].mean().reset_index()

#задаем словарь цветов



# подгружаем css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)





# Задаем лэйаут
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
# Заголовок
    html.H4(children = '''DA5 cohort''',style={
            'textAlign': 'center',
            'color': colors['H'],
            'margin-bottom' : '0',
            'padding-top' : '90px',
            #'font-style' : 'italic',
            #'font-family' : 'William',
            'font-size' : '15',
            'font-weight' : 'light'
	}
),
# Картинка ЯП
# Кривая, надо заменить
    #html.Img(src='https://sun9-58.userapi.com/c845120/v845120357/191e11/LfsgKtO-vkA.jpg'),

# Подпись ян_пр рейт
   # html.Div(children = '''Rate''', style={
   #     'textAlign': 'center',
   #     'color': colors['text']
   #  }),   
    
    
# ян_пр рейт 
    dcc.Graph(
        figure = {
        'data': [go.Indicator(mode = "number+delta",
                                value = last_day_rate,
                                delta = {"reference": pr_day_rate, "valueformat": ".0f"},
                                title = {"text": "Praktikum rate"},
                                domain = {'y': [0, 1], 'x': [0.25, 0.75]}),
                
                 go.Scatter(
                                x = pr_rate_per_day['day'],
                                y = pr_rate_per_day['pr_rate'],
                                marker_color = colorss[0])
                 
                ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                },
                'xaxis': {
                #'linecolor':'red',
                'gridcolor' :colors['grid'],
                'showgrid' : False
                },
                'yaxis': {
                #'linecolor':'red',
                'gridcolor' :colors['grid']
                }
            }
            },
        id ='prorate'
      ),
    
# Подпись мост дификлт зэм
    html.H4(children = '''Hardest theme''', style={
        'textAlign': 'center',
        'color': colors['H'],
        'font-size' : '15',
        'font-weight' : 'light'
     }),
    
    
    
# дификлт зэм 
    
    dcc.Graph(
        figure = {
        'data': [go.Bar(
            x=most_dif['most_difficult_theme'], y=y,
            text=most_dif['count'].sort_values(ascending = False),
            textposition='outside',
            marker_color=colorss
        )],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                },
                'xaxis': {
                #'linecolor':'red',
                'gridcolor' :colors['grid'],
                'showgrid' : False
                },
                'yaxis': {
                #'linecolor':'red',
                'gridcolor' :colors['grid']
                }
            }
            },
        id ='difftheme'
      ),
#-------------------Подпись MAP---------- 


    html.H4(children = '''Students location''', style={
        'textAlign': 'center',
        'color': colors['H'],
        'font-size' : '15',
        'font-weight' : 'light'
     }),        
#-------------------Подпись MAP----------  
    
#-------------------map------------------
dcc.Graph(id='map', figure=figg),
#-------------------map------------------
#fig = dict(data=data, layout=layout)

#app.layout = html.Div([
#dcc.Graph(id=‘map’, figure=fig),
    
    
# Подпись мж рэйт
#    html.H4(children = '''мужчины/женщины''', style={
#        'textAlign': 'center',
#        'color': colors['H'],
#        'font-size' : '15',
#        'font-weight' : 'light'
#    }),
# мж рейт
#    dcc.Graph(
#        figure = {
#            'data': [go.Pie(labels = dfg['gender'],
#                            values = dfg['timestamp'],
#                            
#                            name = 'city/age')],
#            'layout': {
#                'plot_bgcolor': colors['background'],
#                'paper_bgcolor': colors['background'],
#                'font': {
#                    'color': colors['text']
#                },
#                'xaxis': {
#                #'linecolor':'red',
#                'gridcolor' :colors['grid'],
#                'showgrid' : False
#                },
#                'yaxis': {
#                #'linecolor':'red',
#                'gridcolor' :colors['grid']
#                }
#            }
#            },
#        id = 'city_age'
#     ),
# Подпись кволити рэйт
#    html.H4(children = '''quality_rate''', style={
#            'textAlign': 'center',
#            'color': colors['H'],
#            'font-size' : '15',
#            'font-weight' : 'light'
#    }),
# 

# кволити рэйт
#    dcc.Graph(
#        figure = {
#        'data': [go.Scatter(x=q_r.day, y=q_r.quality_rate,
#                        mode='lines',
#                        name='lines')],
#            'layout': {
#                'plot_bgcolor': colors['background'],
#                'paper_bgcolor': colors['background'],
#                'font': {
#                    'color': colors['text']
#                    
#                }
#            }
#            },
#        id ='rate'
#      ),
   
###    дропдаун и радиокнопка 
#    html.Label('Multi-Select Dropdown'),
#    dcc.Dropdown(
#        options=[
#            {'label': 'New York City', 'value': 'NYC'},
#            {'label': u'Montréal', 'value': 'MTL'},
#            {'label': 'San Francisco', 'value': 'SF'}
#        ],
#        value=['MTL', 'SF'],
#        multi=True
#    ),

#    html.Label('Radio Items'),
 #   dcc.RadioItems(
  #      options=[
   #         {'label': 'New York City', 'value': 'NYC'},
    #        {'label': u'Montréal', 'value': 'MTL'},
     #       {'label': 'San Francisco', 'value': 'SF'}
      #  ],
       # value='MTL'
    #),
    
# credits
    html.H6(children = '''@AlBel''',style={
            'textAlign': 'center',
            'color': colors['H'],
        'font-size' : '7',
        'font-weight' : 'light'
	}
)
])

# условная конструкция и запуск
if __name__ == '__main__':
    app.run_server(debug=True)







