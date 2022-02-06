import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import datetime
import numpy as np
import dash_table as dt
from collections import Counter
import plotly.express as px
from nsepy import get_history

portfolio_df = pd.read_csv('D:\ScreenMyStocks\Exploration\holdings (2).csv')
screener_df = pd.read_csv('D:\ScreenMyStocks\Exploration\Tickertape_04022022.csv')
portfolio_df = portfolio_df.sort_values(by='P&L', ascending=False)

# Map tickers to sub-sectors
subsector_df = screener_df[['Name', 'Ticker', 'Sub-Sector']]
subsector_df = subsector_df.dropna()
stock_names = subsector_df['Name'].values.tolist()
stock_tickers = subsector_df['Ticker'].values.tolist()
stock_sectors = subsector_df['Sub-Sector'].values.tolist()
subsector_dict = {}
ticker_dict = {}
for irow in range(len(stock_names)):
    subsector_dict[stock_tickers[irow]] = stock_sectors[irow]
    ticker_dict[stock_tickers[irow]] = stock_names[irow]


# Compute descriptive summary
totalInvested = np.round((portfolio_df['Qty.']*portfolio_df['Avg. cost']).sum(), 0)
currentValue = np.round(portfolio_df['Cur. val'].sum(), 0)
dayChange = -0.83

gainloss = currentValue - totalInvested
gainlossperc = np.round(100*gainloss/totalInvested, 2)
if gainlossperc > 0:
    gainlossperc_color = 'green'
elif gainlossperc < 0:
    gainlossperc_color = 'red'
else:
    gainlossperc_color = 'black'

if dayChange > 0:
    dayChange_color = 'green'
elif dayChange < 0:
    dayChange_color = 'red'
else:
    dayChange_color = 'black'

# Subsector statistics - pie-chart
portfolio_stocks = portfolio_df['Instrument'].values.tolist()
portfolio_sectors = [subsector_dict[x] if x in subsector_dict.keys() else 'NA' for x in portfolio_stocks]
portfolio_df['Subsector'] = portfolio_sectors
subsector_distribution_df = portfolio_df.pivot_table(index='Subsector', values='Cur. val').reset_index(drop=False)
subsector_distribution_df = subsector_distribution_df.sort_values(by='Cur. val', ascending=False)
subsector_distribution_df['Percentage'] = 100 * subsector_distribution_df['Cur. val']/subsector_distribution_df['Cur. val'].sum()
subsector_distribution_df = subsector_distribution_df.reset_index(drop=True)
subsector_distribution_df = subsector_distribution_df[:15]

pie_fig = px.pie(data_frame=subsector_distribution_df,
                 values='Cur. val',
                 names='Subsector',
                 hole=.5,
                 color_discrete_sequence=px.colors.sequential.RdBu,
                 )
pie_fig.update_traces(textfont_size=15, textinfo='label+percent', textposition='outside')
#pie_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20),
#                      legend = dict(font = dict(family = "Courier", size = 15, color = "black")))
pie_fig.update_layout(showlegend=False,
                      margin=dict(l=20, r=20, t=20, b=20))


#---------------------------------------------------------------------------------------------------------
app = dash.Dash(__name__, title="screenmystocks",)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('Logo_long.png'),
                     id='logo-image',
                     style={'height':'60px', 'width':'auto', 'margin-bottom':'25px'})
        ], className='one-third column'),

        html.Div([
            html.Div([
                html.H3('Cognitive Stock Screener', style={'margin-bottom':'0px', 'color':'white'}),
                html.H5('AI powered portfolio guidance', style={'margin-bottom':'0px', 'color':'white'})
                ])
        ], className='one-half column', id = 'title'),


        html.Div([
            html.H6('Last updated :' + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' IST' , style={'color':'black'})
        ], className='one-third column', id = 'title1')



    ], id='header', className= 'row flex-display', style={'margin-bottom':'25px'}),

    html.Div([
        html.Div([
            html.Button(id='login-button-state', n_clicks=0, children='Login',
                        style={'color':'white', 'background':'#41AD6A', 'fontSize':15}),
            html.Button(id='signup-button-state', n_clicks=0, children='Sign Up',
                        style={'color':'white', 'background':'#41AD6A', 'fontSize':15}),
            html.Button(id='load-button-state', n_clicks=0, children='Upload Holdings',
                        style={'color':'white', 'background':'#D896BF', 'fontSize':15})
        ]),
        html.Br(),
        html.P('NIFTY 50 : 17516.30 ( -0.25% )', style={'fontSize': 20, 'color':'black', 'fontWeight':'bold'}),
        html.P('SENSEX : 58644.82 ( -0.24% )', style={'fontSize': 20, 'color':'black', 'fontWeight':'bold'})
    ], style={'display':'inline'}),

    html.Div([
        html.Div([
            html.H6(children='Total Investment',
                    style = {'textAlign': 'center',
                             'color': 'black',
                             'fontWeight':'bold'}),
            html.P("{:,}".format(totalInvested),
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 30}),
            html.P('INR',
                   style={'textAlign': 'center',
                          'color': '#ededed',
                          'fontSize': 20,
                          'margin-bottom': '-18px'}
                   )
        ], className='card_container three columns'),

        html.Div([
            html.H6(children='Current Value',
                    style = {'textAlign': 'center',
                             'color': 'black',
                             'fontWeight':'bold'}),
            html.P("{:,}".format(currentValue),
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 30}),
            html.P('INR',
                   style={'textAlign': 'center',
                          'color': '#ededed',
                          'fontSize': 20,
                          'margin-bottom': '-18px'}
                   )
        ], className='card_container three columns'),

        html.Div([
            html.H6(children='Profit/Loss',
                    style = {'textAlign': 'center',
                             'color': 'black',
                             'fontWeight':'bold'}),
            html.P("{:,}".format(gainloss),
                   style={'textAlign': 'center',
                          'color': gainlossperc_color,
                          'fontSize': 30}),
            html.P(' (' + str(gainlossperc) + '%)',
                   style={'textAlign': 'center',
                          'color': gainlossperc_color,
                          'fontSize': 20,
                          'margin-top': '-18px'}
                   )
        ], className='card_container three columns'),

        html.Div([
            html.H6(children='% day change',
                    style = {'textAlign': 'center',
                             'color': 'black',
                             'fontWeight':'bold'}),
            html.P("{:,}".format(dayChange),
                   style={'textAlign': 'center',
                          'color': dayChange_color,
                          'fontSize': 30}),
            html.P("{:,}".format(dayChange),
                   style={'textAlign': 'center',
                          'color': '#ededed',
                          'fontSize': 20,
                          'margin-bottom': '-18px'}
                   )
        ], className='card_container three columns'),


    ], className='row flex-display'),

    html.Div([
        html.Div([
            dt.DataTable(portfolio_df.to_dict('records'), [{"name": i, "id": i} for i in portfolio_df.columns],
                         page_action='none',
                         style_table={'height': '450px', 'overflowY': 'auto'},
                         style_cell={
                             'font_size': '20px',
                             'text_align': 'center'
                         },
                         style_data_conditional=[
                             {
                                 'if': {
                                     'filter_query': '{P&L} > 0',
                                     'column_id': 'P&L'
                                 },
                                 'backgroundColor': 'green',
                                 'color': 'white'
                             },
                             {
                                 'if': {
                                     'filter_query': '{P&L} < 0',
                                     'column_id': 'P&L'
                                 },
                                 'backgroundColor': 'red',
                                 'color': 'white'
                             },
                             {
                                 'if': {
                                     'filter_query': '{Day chg.} > 0',
                                     'column_id': 'Day chg.'
                                 },
                                 'backgroundColor': 'green',
                                 'color': 'white'
                             },
                             {
                                 'if': {
                                     'filter_query': '{Day chg.} < 0',
                                     'column_id': 'Day chg.'
                                 },
                                 'backgroundColor': 'red',
                                 'color': 'white'
                             },

                         ]
                         )
        ]),

        html.Div([
            dcc.Graph(id='bar_chart',
                      config={'displayModeBar':'hover',
                              'scrollZoom': True},
                      figure = pie_fig
                      )
        ], className='create_container four columns')
    ], className='row flex-display'),

    html.Div([
        html.Div([
            html.H3('Select stock symbols:', style={'paddingRight': '30px', 'fontSize':20}),
            dcc.Dropdown(
                id='my_ticker_symbol',
                options=portfolio_df['Instrument'].unique().tolist(),
                value=[portfolio_df['Instrument'].unique().tolist()[0]]
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            html.H3('Select start and end dates:', style={'fontSize':20}),
            dcc.DatePickerRange(
                id='my_date_picker',
                min_date_allowed=datetime.datetime(2015, 1, 1),
                max_date_allowed=datetime.datetime.today(),
                start_date=datetime.datetime(2021, 1, 1),
                end_date=datetime.datetime.today()
            )
        ], style={'display': 'inline-block'}),
        dcc.Graph(
            id='my_graph',
            figure={
                'data': [
                    {'x': [0, 1], 'y': [0, 1]}
                ]
            },
        style={'width': '45vh', 'height': '25vh'}
        )
    ])

], id='mainContainer', style={'display':'flex', 'flex-direction':'column'})

@app.callback(
    Output('my_graph', 'figure'),
    #Input('submit-button', 'n_clicks'),
    Input('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date'))
def update_graph(stock_ticker, start_date, end_date):
    start = datetime.datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date[:10], '%Y-%m-%d')
    traces = []
    if type(stock_ticker) != list:
        stock_ticker = [stock_ticker]
    for tic in stock_ticker:
        df = get_history(symbol=tic, start=start, end=end)
        print(tic, df.shape)
        traces.append(go.Scatter(x=df.index, y= df['Prev Close']))
    fig = {
        'data': traces
    }
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)