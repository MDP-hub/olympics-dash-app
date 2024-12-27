import pandas as pd
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

#read main data file
olympics_data = pd.read_csv('olympics_pivot.csv')

#set up variables for dropdowns
olympics_list = olympics_data.sort_values('game_year', ascending=False).slug_game.unique()
iso_3 = pd.read_html("https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes#Current_ISO_3166_country_codes")[0].iloc[:, 4]
mask = ~olympics_data.country_3_letter_code.isin(iso_3)
missing_iso = list(olympics_data.loc[mask, 'country_3_letter_code'].unique())
countries_list = olympics_data['country_name'].unique()
countries_data = (olympics_data
 .groupby(['country_3_letter_code'], as_index=False)
 .agg({'country_name': 'first'}))
country_dict = (countries_data
 .rename(columns={'country_3_letter_code':'value', 'country_name':'label'})
 .to_dict('records'))

#app name and template
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

load_figure_template('slate')


#app layout: 2 tabs
app.layout = html.Div([
    dbc.Tabs([
        dbc.Tab([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dcc.Markdown(id="intro")
                        ], style={'padding': 3})
                    ], width=2),
                    dbc.Col([
                        html.H1(id='title', style={'font-size': 50,
                                                   'font-weight': 'bold',
                                                   'text-align': 'center'}),
                    ]),
                    dbc.Col([
                        html.H6(id='subtitle-olympics', children='Olympics selector'),
                        dcc.Dropdown(id='olympics-selector',
                                    options=olympics_list,
                                    value=olympics_list[0])
                    ], width=2),
                    dbc.Col([
                        html.H6(id='subtitle-method', children=['Methodology selector',
                                                                html.Span(id='question-mark', children=['🯄',
                                                                                                        dbc.Tooltip(
                                                                                                            'Weighted Total: \nGold = 3, Silver = 2, Bronze = 1', target='question-mark')], style={'margin-left':10})
                                                                ]),
                        dcc.Dropdown(id='methodology',
                                     options=[{'label':'Gold Medals', 'value':'gold'},
                                              {'label': 'Total Medals', 'value':'total'},
                                              {'label': 'Weighted Total', 'value':'weighted_total'}],
                                     value='gold')
                    ], width=2)
                ], style={'margin-bottom': 10, 'margin-top': 5}),
                dbc.Row([
                    dbc.Col([dcc.Graph(id='map_olympics')]),
                    dbc.Col([
                        dbc.Row([html.H3("Missing Countries:"),
                             html.Ul(id='missing-countries'),])
                             ], width= 3),


                ], style={'margin-bottom': 10}),
                dbc.Row([
                    dbc.Col([
                        dbc.Card(html.P(id='legend',
                                     children=[
                                 html.Span('▪ Women', style={'color': '#FED9D7', 'margin-right': 15}),
                                 html.Span('▪ Men' , style={'color': '#16537e', 'margin-right': 15}),
                                 html.Span('▪ Even', style={'color': 'grey'})
                             ], style={'text-align':'center'}))
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                        dcc.Markdown(id='warning', style={'text-align': 'center'})
                    ])])
                ])
            ])
        ], label='Overview'),
        dbc.Tab([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1(id="country-selected", style={'font-size': 50,
                                                   'font-weight': 'bold',
                                                   'text-align': 'left'}),
                    ]),

                    dbc.Col([
                        html.H6(id='subtitle-country-sel', children='Country Selector'),
                        dcc.Dropdown(id='countries-sel',
                                    options=country_dict,
                                    value='ITA')
                    ], width=2),
                    dbc.Col([
                        html.H6(id='subtitle-method-second', children=['Methodology selector',
                                                                       html.Span(id='question-mark-2', children=['🯄',
                                                                                                        dbc.Tooltip(
                                                                                                            'Weighted Total: \nGold = 3, Silver = 2, Bronze = 1', target='question-mark-2')], style={'margin-left':10})]),
                        dcc.Dropdown(id='methodology-tab2',
                                     options=[{'label':'Gold Medals', 'value':'gold'},
                                              {'label': 'Total Medals', 'value':'total'},
                                              {'label': 'Weighted Total', 'value':'weighted_total'}],
                                     value='gold')
                    ], width=2),
                    dbc.Col([
                        html.H6("Season:"),
                        dcc.RadioItems(id='winter-summer',
                                      options=['Winter', 'Summer'],
                                      value='Summer')
                    ], width=2)
                ], style={'margin-bottom': 10, 'margin-top': 5}),
                dbc.Row([
                    dbc.Col([
                        html.H3(id='line-title', children='Men & Women Medals Over Time'),
                        dcc.Graph(id='line-chart', clear_on_unhover= True )
                    ]),
                    dbc.Col([html.H3("Total Medals:"),
                             dcc.Markdown(id='medal-tot')
                             ], width= 3)

                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card(html.P(id='legend bar',
                                     children=[
                                 html.Span('▪ Women', style={'color': '#FED9D7', 'margin-right': 15}),
                                 html.Span('▪ Men' , style={'color': '#16537e', 'margin-right': 15}),
                             ], style={'text-align':'center'}))
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                        html.P(id='outro', style={'text-align': 'center'}, children=[
                            'Data: ',
                            dcc.Link('1 ',  href="https://www.kaggle.com/datasets/piterfm/olympic-games-medals-19862018?select=olympic_results.csv"),
                            dcc.Link('2 ',  href="https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games?select=medals.csv")
                        ])
                    ])])
                ])
            ])
        ], label='Country View'),
    ])
])


#callback functions
@app.callback(Output('map_olympics', 'figure'),
              Output('title', 'children'),
              Output('missing-countries', 'children'),
              Output('warning', 'children'),
              Output('intro', 'children'),
              Output('methodology-tab2', 'value'),
              Input('olympics-selector', 'value'),
              Input('methodology', 'value'))
def update_map(olympics, methodology):

    #select field based on the methodology selected
    male_field = 'men_' + methodology
    female_field = 'women_' + methodology

    #group by the data for the currect level
    map_data = (olympics_data.query("slug_game == @olympics")
            .groupby(['country_3_letter_code', 'country_name'], as_index=False)
            .agg({male_field:'sum',
                   female_field:'sum',
                   }))

    #info on the season depending on the olympics selection to create the title
    if olympics_data.query("slug_game == @olympics").game_season.unique()[0] == 'Summer':
        season = '☀'
    else:
        season = '❄'

    #create title
    title = f"{olympics.upper()} {season}"

    #create color fields depending on the methodology selected.

    map_data['color'] = np.where(map_data[male_field]>map_data[female_field], 'Men',
                             np.where(map_data[female_field]>map_data[male_field], 'Women', 'Even'))

    map_data['colorhex'] = np.where(map_data[male_field]>map_data[female_field], '#16537e',
                             np.where(map_data[female_field]>map_data[male_field], '#FED9D7', 'grey'))

    #create choropleth map
    fig = px.choropleth(map_data,
                        locations='country_3_letter_code',
                        locationmode = 'ISO-3',
                        color = 'color',
                        color_discrete_map={'Men': '#16537e',
                                            'Women': '#FED9D7',
                                            'Even': 'grey' },
                        hover_name = 'country_name',
                        hover_data={male_field : True,
                                    female_field : True,
                                    'color': False,
                                    'country_3_letter_code': False,},
                        ).update_layout(showlegend=False,
                                        margin= {"r":0,"t":0,"l":0,"b":0},
                                        paper_bgcolor= '#272b30',
                                        ).update_geos(projection_type="natural earth")


    #Add the info on the right hand side for the missing countries. The check is done comparing with Wiki
    missing_countries = []
    for index in map_data.query("country_3_letter_code in @missing_iso").index:
        name = map_data.loc[index, 'country_name']
        color_dot = map_data.loc[index, 'colorhex']
        missing_countries += [html.Li(children=name,
                                      style={'color': color_dot, 'font-size':20})]


    #adding intro. It could be removed from here, since it's static (TODO)
    intro = f"What gender is winning the most at the Olympics?"

    #warning informing that the number of medals is not the same
    warning = f"**{int(map_data[male_field].sum())}** {methodology} medals for **Men** & **{int(map_data[female_field].sum())}** medals for **Women**"

    return fig, title, missing_countries, warning, intro, methodology

@app.callback(Output('line-chart', 'figure'),
              Output('country-selected', 'children'),
              Output('line-title', 'children'),
              Input('countries-sel', 'value'),
              Input('methodology-tab2', 'value'),
              Input('winter-summer', 'value'))
def timeline_olympics(countries, method, season):

    #set up fields based on the methodology and the data based on the country and season
    male_field = 'men_' + method
    female_field = 'women_' + method
    timeline_data = (olympics_data
            .query("country_3_letter_code == @countries")
            .groupby(['country_3_letter_code', 'game_year', 'game_season'], as_index=False)
            .agg({male_field: 'sum',
                  female_field: 'sum'}))

    #create the linechart
    fig = (px.line(
            timeline_data.query("game_season == @season"),
            x='game_year',
            y=[male_field, female_field],
            markers=True,
            custom_data='game_year')
           .update_yaxes(title=method.replace("_", " ").capitalize())
           .update_layout(showlegend=False,
                          margin= {"r":0,"t":0,"l":0,"b":0},
                          paper_bgcolor= '#272b30')
           .update_xaxes(title="Year"))

    #change the color of the two lines
    fig['data'][0]['line']['color'] = '#16537e'
    fig['data'][1]['line']['color'] = '#FED9D7'

    #set up page title (country name)
    title = countries_data.query("country_3_letter_code == @countries").iloc[0, 1]

    #set up the chart title (based on the methodology)
    chart_title = f"Men & Women {method.replace("_", " ").capitalize()} medals Over Time"

    return fig, title, chart_title


@app.callback(Output('medal-tot', 'children'),
              Input('countries-sel', 'value'),
              Input('winter-summer', 'value'),
              Input('line-chart', 'hoverData'))
def total_medal(countries, season, hoverdata):

    #take the data depending if something has been selected on the line chart
    markdown_txt = ""
    if not hoverdata:
        base_data = olympics_data.query("country_3_letter_code == @countries and game_season == @season")
        # raise PreventUpdate
    else:
        year_selected = hoverdata['points'][0]['customdata'][0]
        base_data = olympics_data.query("game_year == @year_selected "
                                        "and country_3_letter_code == @countries "
                                        "and game_season == @season")
        markdown_txt += f"{season} {year_selected} Olympics\n"

    #final data for the text info
    total_data = (base_data
            .groupby(['country_3_letter_code', 'game_season'], as_index=False)
            .agg({'men_gold': 'sum',
                  'women_gold': 'sum',
                  'men_total': 'sum',
                  'women_total': 'sum',
                  'men_weighted_total': 'sum',
                  'women_weighted_total': 'sum',
                  'men_bronze': 'sum',
                  'women_bronze': 'sum',
                  'men_silver': 'sum',
                  'women_silver': 'sum'})
            )

    #create 2 sections: 1 for men and one for women. Append to the text for the markdown.
    for gender in ['men', 'women']:
        markdown_txt += f"### **{gender.upper()}:** \n"
        for field in ['gold', 'silver', 'bronze', 'total', 'weighted_total']:
            comb_field = f"{gender}_{field}"
            markdown_txt += f"- *{field.capitalize()}:* **{int(total_data[comb_field][0])}** \n"

    return markdown_txt

if __name__ == '__main__':
    app.run_server(port=8052)

