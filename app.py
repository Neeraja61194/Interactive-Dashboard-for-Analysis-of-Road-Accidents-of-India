import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

df = pd.read_csv("Modified_Data_forMap - Sheet1.csv",sep=r'\s*,\s*', engine='python')
dff2 = df[~df['States/UT'].isin(['Delhi', 'Andaman and Nicobar Island', 'Chandigarh', 'Dadra abd Nagar Haveli', 'Daman and Diu', 'Lakshadweep', 'Puducherry'])]
cols_dd = ['Number of Persons Injured', 'Number of Persons Killed', 'Total No. of Road Accidents']

de = pd.read_csv("accidents_hours.csv",sep=r'\s*,\s*', engine='python')
dee = de.loc[(de['STATE/UT']=='Uttar Pradesh') | (de['STATE/UT']=='Andhra Pradesh')]

state_hours = de['STATE/UT'].unique()

df1= pd.melt(dee,id_vars=['STATE/UT', 'YEAR'],var_name='Time of Accident',value_name='Count')

app.layout = html.Div([
        html.Br(),
        dbc.Row(
            [dbc.Col(html.H2("Analysis of Road Accidents in India"),
                        width={'size': 6, 'offset': 4},
                        ),  
            ]),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='demo-dropdown',
                                    options=[{'label': k, 'value': k} for k in cols_dd],
                                    value=cols_dd[0],
                                    placeholder=cols_dd[0],),
                        width={'size': 3, "offset": 2, 'order': 2}
                        ),
                dbc.Col(dcc.Slider(id = 'slider_year',
                    included = True,
                    updatemode='drag',
                    tooltip={'always_visible': True},
                    min = 2006,
                    max = 2015,
                    step = 1,
                    value = 2006,
                    marks = {'2006': '2006', '2007': '2007', '2008': '2008', '2009': '2009','2010': '2010','2011': '2011','2012': '2012','2013': '2013','2014': '2014','2015': '2015'},
                    className = 'dcc_compon'
                ), width={'size': 5, "offset": 1, 'order': 1}, style={'color': 'black'}
                ),
            ], no_gutters=True
        ),

        html.Br(),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='display-selected-values', clickData=None, hoverData=None,style={'display': 'inline-block'}),
                        width={'size': 2, "offset": 0, 'order': 1}
                        ),
                dbc.Col(
                    [
                    html.Div(dcc.Graph(id='line_bar_all', clickData=None, hoverData=None),),
                    html.Br(),
                    html.Label(['Click a state in Map or Bar Chart to see individual counts of accidents'],
                        style={'font-weight': 'bold', 'color': 'red'}),
                    html.Div(dcc.Graph(id='selected_state', clickData=None, hoverData=None),),
                    ],width={'size': 4,  "offset": 3, 'order': 2}),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.H3("Analysis of Time of Road Accidents"),
                        width={'size': 4, 'offset': 2},
                        ),
                dbc.Col(dbc.Button("Accidents Times Plot", id="button_bubble", color="primary", className="mr-1"),
                       width={'size': 2, 'offset': 0},
                        ), 
            ]),
        html.Br(),
        dbc.Row(dbc.Col(
        dbc.Collapse(
            [
            dcc.Graph(id='bubble', clickData=None, hoverData=None),],
            id="collapse_bubble", is_open=False),
            width={'size': 4, 'offset': 2},
        ),)
])

@app.callback(
    dash.dependencies.Output('display-selected-values', 'figure'),
    [dash.dependencies.Input('demo-dropdown', 'value')],
    [dash.dependencies.Input('slider_year', 'value')])

def update_output(value, option_slctd):

    container = "The year chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["Year"] == option_slctd]
    if value == 'Number of Persons Injured':
        color_pal = 'Blues'
        colour_font = '#0c297e'
    elif value == 'Number of Persons Killed':
        color_pal = 'Reds'
        colour_font = 'red'
    else:
        color_pal = 'emrld'
        colour_font = 'green'

    fig = go.Figure(data=go.Choropleth(
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey='properties.ST_NM',
    locationmode='geojson-id',
    locations=dff['States/UT'],
    z=dff[value],

    autocolorscale=False,
    colorscale=color_pal,

    colorbar=dict(
        title={'text': value},

        thickness=15,
        len=0.35,
        bgcolor='rgba(255,255,255,0.6)',

        tick0=0,
        dtick=100,

        xanchor='left',
        x=0.01,
        yanchor='bottom',
        y=0.05
    )
    ),
    layout=go.Layout(
            paper_bgcolor='rgba(0,255,0,0)',
            plot_bgcolor='rgba(0,0,255,0)'
        ))

    fig.update_geos(
    bgcolor= 'rgba(0,0,255,0)',
    visible=False,
    projection=dict(
        type='conic conformal',
        parallels=[12.472944444, 35.172805555556],
        rotation={'lat': 24, 'lon': 80}
    ),
    lonaxis={'range': [68, 98]},
    lataxis={'range': [6, 38]}
)

    fig.update_layout(
        title=dict(
            text=str(value) + " in the year : " + str(option_slctd),
            xanchor='center',
            x=0.5,
            yref='paper',
            yanchor='bottom',
            y=1,
            pad={'b': 10}
        ),
        title_font_color=colour_font,
        margin={'r': 0, 't': 30, 'l': 30, 'b': 0},
        height=650,
        width=650,
        plot_bgcolor= 'black',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

def mapHour(state_i):
    if (state_i == 'Kerala') or (state_i == 'Karnataka') or (state_i == 'Andhra Pradesh') or (state_i == 'Telangana') or (state_i == 'Tamil Nadu'):
        return'South Indian States'
    else:
        return'North Indian States'
        
@app.callback(
    dash.dependencies.Output('line_bar_all', 'figure'),
    [dash.dependencies.Input('demo-dropdown', 'value')],
    [dash.dependencies.Input('slider_year', 'value')])

def update_BarChart_All(dropdown_selected, year_selected):
    dff = dff2.copy()
    dff2['Type'] = dff2['States/UT'].apply(mapHour)
    #dff2.sort_values(dropdown_selected, inplace=True, ascending=False)
    
    if dropdown_selected is None:
        dff=dff2[(dff2['Year']==2006)]
        fig1 = px.bar(dff, y='Number of Persons Injured', x='States/UT', color='Type', height=400, width=850, template='none')
        #fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', title={'text':'North Indian and South Indian States',
                        'font':{'size':16},'x':0.5,'xanchor':'center'})
        fig1.data[0]['marker'].update(color='lightblue')
        return fig1
    else:
        if dropdown_selected == 'Number of Persons Injured':
            dff=dff2[(dff2['Year']==year_selected)]
            fig1 = px.bar(dff, y=dropdown_selected, x='States/UT', color='Type', height=400, width=850, template='none')
            fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', title={'text':'North Indian and South Indian States',
                        'font':{'size':16},'x':0.5,'xanchor':'center'})
            fig1.data[0]['marker'].update(color='lightblue')
            fig1.data[1]['marker'].update(color="#0c297e")
        elif dropdown_selected == 'Number of Persons Killed':
            dff=dff2[(dff2['Year']==year_selected)]
            fig1 = px.bar(dff, y=dropdown_selected, x='States/UT', color='Type', height=400, width=850, template='none')
            fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', title={'text':'North Indian and South Indian States',
                        'font':{'size':16},'x':0.5,'xanchor':'center'})
            fig1.data[0]['marker'].update(color='darkorange')
            fig1.data[1]['marker'].update(color="red")
        else:
            dff=dff2[(dff2['Year']==year_selected)]
            fig1 = px.bar(dff, y=dropdown_selected, x='States/UT', color='Type', height=400, width=850, template='none')
            fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', title={'text':'North Indian and South Indian States',
                        'font':{'size':16},'x':0.5,'xanchor':'center'})
            fig1.data[0]['marker'].update(color='lightgreen')
            fig1.data[1]['marker'].update(color="green")
        return fig1

@app.callback(
    dash.dependencies.Output('selected_state', 'figure'),
    [dash.dependencies.Input('display-selected-values', 'clickData')],
    [dash.dependencies.Input('line_bar_all', 'clickData')],
    [dash.dependencies.Input('display-selected-values', 'selectedData')],
    [dash.dependencies.Input('display-selected-values', 'hoverData')])

def update_side_graph(clk_data, clk_data_bar, slct_data, hov_data):
    if (clk_data is None) and (clk_data_bar is None):
        dff=df[(df['States/UT']=='Andhra Pradesh')]

        fig2 = px.line(dff, x="Year", y=['Total No. of Road Accidents', 'Number of Persons Injured', 'Number of Persons Killed'], color='variable', height=300, width=850, template='none')
        fig2.update_layout(yaxis={'title':'Total Count'},
                        title={'text':'Individual State Data : Andhra Pradesh',
                        'font':{'size':16},'x':0.5,'xanchor':'center'})
        return fig2
    elif (clk_data is not None) and (clk_data_bar is not None):
        clk_data = None
        click_state = clk_data_bar['points'][0]['x'] 
        dff=df[(df['States/UT']==click_state)]

        fig2 = px.line(dff, x="Year", y=['Total No. of Road Accidents', 'Number of Persons Injured', 'Number of Persons Killed'], color='variable', height=300, width=850, template='none')
        fig2.update_layout(yaxis={'title':'Total Count'},
                        title={'text':'Individual States Data : ' + click_state,
                        'font':{'size':28},'x':0.5,'xanchor':'center'})
        return fig2

    elif (clk_data is not None) or (clk_data_bar is not None):
        if clk_data is not None:
            click_state = clk_data['points'][0]['location'] 
        elif clk_data_bar is not None:
            click_state = clk_data_bar['points'][0]['x'] 

        dff=df[(df['States/UT']==click_state)]

        fig2 = px.line(dff, x="Year", y=['Total No. of Road Accidents', 'Number of Persons Injured', 'Number of Persons Killed'], color='variable', height=300, width=700, template='none')
        fig2.update_layout(yaxis={'title':'Total Count'},
                        title={'text':'Individual States Data : ' + click_state,
                        'font':{'size':16},'x':0.5,'xanchor':'center'})
        return fig2

@app.callback(
    dash.dependencies.Output('bubble', 'figure'),
    [dash.dependencies.Input('display-selected-values', 'clickData')])

def update_bubble_graph(clk_data):

    world_xrange=[500,9000]
    fig = px.scatter(df1, y="Count", x="Time of Accident", color="STATE/UT", animation_frame="YEAR",
                    range_y=world_xrange, range_x=[-0.9,8],
                    title="Time of Road Accidents",
                    template="none",
                    width=900,
                    height=500,
                    labels={"Rate":"Years a child is expected to spend at school/university",
                        "Indicator Name":"States"} # customize label
        )
    fig.update_layout(title={'x':0.5,'xanchor':'center','font':{'size':20}},
                    xaxis=dict(title=dict(font=dict(size=20))),
                    yaxis={'title':{'text':None}},
                    legend={'font':{'size':18},'title':{'font':{'size':18}}})

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 800
    fig.data[0].name = 'Uttar Pradesh'
    fig.data[1].name = 'Andhra Pradesh'
    fig.data[0]['marker'].update(size=14)
    fig.data[1]['marker'].update(size=14)
    fig.data[0]['marker'].update(color='green')
    fig.data[1]['marker'].update(color="red")

    for x in fig.frames:
        x.data[0]['marker']['color'] = 'green'
        x.data[1]['marker']['color'] = 'red'

    return fig

@app.callback(
    Output("collapse_bubble", "is_open"),
    [Input("button_bubble", "n_clicks")],
    [State("collapse_bubble", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)

# References:
# https://www.youtube.com/channel/UCqBFsuAz41sqWcFjZkqmJqQ
# https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Other/Dash_Introduction/intro.py
# https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Bootstrap/bootstrap_intro.py 
# https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson
# https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Plotly_Graphs/Animated_Scatter/gender_ineq.py
# Datasets - https://www.kaggle.com/arindambaruah/indian-road-accidents-data?select=Road_Accident_Profile_of_Select_Cities-2011-15.csv
# Datasets - https://www.kaggle.com/manugupta/road-accidents-in-india

