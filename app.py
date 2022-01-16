# ----------------------------------------------------------------------------------------
# prepare environment (boilerplate)

# import the required packages using their usual aliases
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import humanize
import os

# read token string with your access mapbox token from a hidden file
# saved in environment's root directory same as where this app.py file is
# if you're using GitHub make sure to add '*.mapbox_token' to your .gitignore file
# to prevent your private credentials from being publicly viewed or uploaded to GitHub
mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')

# ----------------------------------------------------------------------------------------
# -- call the data
# -- read the food trade matrix data into pandas from CSV file of 2019 export quantities (exported from analysis in Jupyter Notebook)
# prepared using original dataset FAOSTAT Detailed trade matrix: All Data Normalized from https://fenixservices.fao.org/faostat/static/bulkdownloads/Trade_DetailedTradeMatrix_E_All_Data_(Normalized).zip
# with appended key demographics from FAOSTAT Key dataset (in Jupyter Notebook)
# # full dataset
dffood = pd.read_csv('./data/dffood.csv')

# -- read the 4.5 depth soil organic carbon density (%) measurements pre-filtered for audience China's and U.S.'s food's trade export Reporter Countries (exported from analysis in Jupyter Notebook)
# prepared using original dataset Soil organic carbon density: SOCD5min.zip from http://globalchange.bnu.edu.cn/research/soilw
# with appended country name and ISO3 code from GeoPandas embedded World dataset
dfsoil = pd.read_csv('./data/dfsoil_subUSCN_prod.csv')

# ----------------------------------------------------------------------------------------
# create (instantiate) the app,
# using the Bootstrap MORPH theme, Slate (dark) or Flatly (light) theme or Darkly (its dark counterpart) to align with my llc website in development with Flatly (dadeda.design)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH],
                meta_tags=[{'name': 'viewport',
                            # initial-scale is the initial zoom on each device on load
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]
                )

server = app.server
app.title = 'Sustain-Our-Soil-for-Our-Food'

# ----------------------------------------------------------------------------------------
# named variables for the app's layout
navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Email", href="mailto:kathryn@dadeda.design?subject=Sustain our Soil for our Food", target='_blank'),  # mailto link, github issues, and/or "http://kathrynhurchla.com/", target="_blank"),
                # submit a gitHub issue (with options of feature request or bug report active at time of prototype deployment)
                dbc.DropdownMenuItem("Submit issues or Ideas", href="https://github.com/khurchla/sustain-our-soil-for-our-food/issues/new/choose", target='_blank'),
                # link to gitHub repository for readme caveats, data preparation, or to recreate app/opensource code
                dbc.DropdownMenuItem("View source code", href="https://github.com/khurchla/sustain-our-soil-for-our-food", target='_blank')
            ],
            nav=True,
            in_navbar=True,
            label="Contact",
        ),
        dbc.DropdownMenu(
            children=[
                # placeholder for Twitter button javascript embed # <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-text="Organic carbon occurs naturally in soil, but whether it presents a threat or a service to humans depends on YOU." data-via="khurchla" data-hashtags="dataviz" data-show-count="false">Tweet</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                dbc.DropdownMenuItem("Tweet", href="#"),
                # placeholder for popular Chinese social media Weibo share URL: http://service.weibo.com/share/share.php?url=http://example.com&appkey=&title=Organic carbon occurs naturally in soil, but whether it presents a threat or a service to humans depends on YOU.&pic=&ralateUid=&language=zh_cn
                dbc.DropdownMenuItem("Weibo", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Share",
        ),
    ],
    brand='Sustain Our Soil for Our Food',
    color='#483628',  # "dark", #hex code color matching text in graphs, a dark orange brown; "dark" is MORPH theme option and a dark charcoal
    dark=True,
    class_name="fixed-top",
)

appSubheading = dbc.Container(
    html.Div([
        html.H5("Organic carbon occurs naturally in soil, but whether it presents a threat or a service to humans depends on YOU.")
        ])
)

# # empty card to push the info tooltip to the far right
# controlsSpacer = dbc.CardBody(
#     html.Div()
# )

tooltip = dbc.CardFooter(
    html.Div(children=[
        dbc.Button(
            "info",
            id="info-toolbar-tooltip",
            # class_name="mx-2",
            n_clicks=0,
            size="sm"
        ),
        dbc.Tooltip(
            "Use the in toolbar in the upper right corner of the map to zoom, move around, or reset your view.",
            target="info-toolbar-tooltip",
            placement="left"
        ),
    ],
))

learnMore = html.Div(children=[
    dbc.Button("Learn more about soil health, and how you can help.", id="learn-more-button", n_clicks=0, color="link", size="md", class_name="btn btn-link"),
    dbc.Modal(children=[
        dbc.ModalHeader(dbc.ModalTitle("Take Your Curiosity a Step Further.")),
        dbc.ModalBody(children=['Copy these suggested key terms by clicking the paper icon beside them or by selecting and copying them directly from within the text area below, and then paste them into your preferred search engine. There are many excellent resources to learn more on your journey as a soil stakeholder.',
                                html.Br(),
                                html.Br(),
                                dcc.Textarea(
                                    id="search_terms_textarea_id",
                                    value='"soil health" OR "soil carbon" OR "soil organic carbon" OR "regenerative agriculture" OR "regenerative grazing"',
                                    style={"heaight": '100%',
                                           "width": 300,
                                           "overflow": "auto"},
                                ),
                                dcc.Clipboard(
                                    target_id="search_terms_textarea_id",
                                    title="copy",
                                    style={
                                        "display": "inline-block",
                                        "fontSize": 20,
                                        "color": '#483628',
                                        "verticalAlign": "top"
                                    }
                                )
                                ]
                      ),

        dbc.ModalFooter(
            dbc.Button(
                "Close", id="learn-more-close", className="ms-auto", n_clicks=0
            )
        ),
    ],
        id="modal",
        size="lg",
        is_open=False,
        centered=True,
        style={"color": '#483628'}
    )
])

whyCarbon = dbc.Card(
    html.Div(children=[
        html.H5("Carbon has a superpower.",
                style={'text-align': 'left'}
                ),
        html.P("Often called the element or giver of life, carbon is critical to life supporting processes because it can bond to many other elements essentially as a building block of large and complex compounds that make up living things––including soil, and the plants and animals in the food chain. Soil organic carbon is left in the soil by the processes collectively called the Carbon Cycle, which includes both the growth and death of plants, animals, and other organisms.",
               style={'text-align': 'left'}
               ),
        html.P("Soil organic carbon (SOC) indicates soil's ability to hold water and nutrients that sustain plants in natural and farming settings. As an indicator of soil's overall organic matter, it also builds soil structure that reduces erosion leading to improved water quality and greater resilience from storms.",
               style={'text-align': 'left'}
               ),
        html.P("Including its mineral inorganic carbon parts, our soil holds the largest amount of carbon in Earth's ecosystem, and its release––through mismanagement from a lack of knowledge and the removal of forests and wetlands––is a great risk to increasing carbon dioxide in the atmosphere and speeding up climate change.",
               style={'text-align': 'left'}
               ),
        html.P("Whether your food comes from across the globe or your own garden, you have an opportunity to restore and ensure soil health to fill bellies all over the world with nutritious foods for years to come. By learning more, you can have an impact on soil health, and together we may even save the world one plate at a time.",
               style={'text-align': 'left'}
               )
        ]),
    body=True,
    color="light",
    class_name="card bg-light mb-3"
)

dropdownReporterCountry = dbc.CardBody(
    html.Div(children=[
        # add a brief instructive subheading as a label
        dbc.Label('Choose a trade partner.', style={'text-align': 'left'}
                  ),
        # add a dropdown for audience member using app to select a reporter country (their partner who exports the food they've chosen to their country)
        dcc.Dropdown(id='reporter_country_dropdown',
                     options=[{'label': country, 'value': country}
                              # series values needed to be sorted first before taking unique to prevent errors
                              for country in dfsoil['Reporter_Country_name'].sort_values().unique()],
                     placeholder='Trade Partner',
                     searchable=True,
                     clearable=True,  # shows an 'X' option to clear selection once selection is made
                     persistence=True,  # True is required to use a persistence_type
                     persistence_type='session',  # remembers dropdown value selection until browser tab is closed (saves after refresh)
                     multi=False,  # do not allow multiple country selections (default); doing so would require more code development in callback function
                     style={"width": "75%"}
                     )
    ])
)

controls = html.Div(children=[
    dbc.CardGroup([dropdownReporterCountry, tooltip], class_name="card border-primary bg-light mb-2")
    ]
)

mapExplorer = dbc.Card([
    html.Div(children=[
        html.P('Explore how much of the soil where your food comes from is made up of organic carbon.',
               className="lead"
               ),
        html.Div(controls),
        # # map format without spinner for reference
        # html.Div(id='map-socd',
        #          ),
        # add a loading spinner to the map
        dbc.Spinner(id='map-socd', size="lg", color="primary", type="border", fullscreen=False
                 ),
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Dots on the map vary in size by the location's soil organic carbon density (SOCD), which can be understood as how much of the soil is made up of organic carbon, from the ground surface down to 4.5 centimeters deep. These density estimates are by global leading scientists from the available worldwide soil data––collected and mathematically modelled––and are expressed in metric tonnes per hectare (t ha-1), which are equal to about 1,000 kilograms or aproximately 2,205 pounds.",
               style={'text-align': 'left'}),
        html.P("Read more about carbon's importance in soil below.",
               style={'text-align': 'left'}),
        html.P(children=[
            "Data source: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, ",
            html.A("6: 249-263.",
                   href='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2013MS000293',
                   target='_blank'  # opens link in new tab or window
                   )
        ],
            style={'text-align': 'left'}),
    ]),
    # html.Br()
], body=True)

# --------------------------SOIL BAR graph--------------------------
# take the mean SOCD by grouping soil dataframe by Country and append the mean as a column
dfsoil['SOCDcountryMean'] = dfsoil['Reporter_Country_SOCD_depth4_5'].groupby(dfsoil['Reporter_Country_name']).transform('mean')
# drop the raw SOCD values from the subset of soil data; used in density ranges bar chart
dfsoilMeans = dfsoil.drop_duplicates(subset=['Reporter_Country_name', 'Reporter_Country_continent', 'SOCDcountryMean', 'Reporter_Country_pop_est']).drop(['Reporter_Country_SOCD_depth4_5'], axis=1).sort_values(by=['SOCDcountryMean', 'Reporter_Country_continent', 'Reporter_Country_name'], ascending=(False, True, True))
dfsoilMeansMaxOrder = ['Africa', 'Oceania', 'South America', 'Asia', 'North America', 'Europe']
# make numbers into a more human readable format, e.g., transform 12345591313 to '12.3 billion' for hover info
dfsoilMeans['humanPop'] = dfsoilMeans['Reporter_Country_pop_est'].apply(lambda x: humanize.intword(x))

# make a bar chart showing range of mean by countries, overlay countries within continent group to retain mean y axis levels
rangeSOCDfig = px.bar(dfsoilMeans, x='Reporter_Country_continent', y='SOCDcountryMean', color='SOCDcountryMean', barmode='overlay',
                      # set bolded title in hover text, and make a list of columns to customize how they appear in hover text
                      custom_data=['Reporter_Country_name',
                                   'Reporter_Country_continent',
                                   'SOCDcountryMean',
                                   'humanPop'
                                   ],
                      color_continuous_scale=px.colors.sequential.speed,  # alternately use turbid for more muted yellows to browns (speed for yellow to green to black scale)
                      # a better label that will display over color legend
                      labels={'SOCDcountryMean': 'Avg.<br>SOCD'},
                      # lower opacity to help see variations of color between countries as means change
                      opacity=0.20
                      )
# sort bars by mean SOCD, and suppress redundant axis titles, instead of xaxis={'categoryorder': 'mean ascending'} I pre-sorted the dataframe above, but still force sort here by explicit names
rangeSOCDfig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': dfsoilMeansMaxOrder},
                           xaxis_title=None, yaxis_title=None,  # removed xaxis_tickangle=-45, # used to angle longer/more xaxis labels
                           paper_bgcolor='#e8ece8',  # next tint variation up from a low tint of #dadeda
                           plot_bgcolor='#f7f5fc',  # violet tone of medium purple to help greens pop forward
                           yaxis={'gridcolor': '#e8ece8'},  # match grid lines shown to background to appear as showing through
                           font={'color': '#483628'})  # a dark shade of orange that appears dark brown
rangeSOCDfig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{customdata[0]} </b><br>",  # bolded hover title included, since the separate hover_name is superseced by hovertemplae
        "%{customdata[1]}",  # Continent value with no label
        "Average SOCD: %{customdata[2]:.1f} t ha<sup>−1</sup>",  # with html <sup> superscript tag in abbr. metric tonnes per hectare (t ha-1) t ha<sup>−1</sup> formatted to 2 decimals
        "Estimated Population (2019): %{customdata[3]} people"  # in humanized format
    ])
)


densityRanges = dbc.Card([
    html.Div(children=[
        html.H5("Range of Average Soil Organic Carbon Density (SOCD) Worldwide"
                ),
        dcc.Graph(figure=rangeSOCDfig,
                  id="SOCD-bar-chart",
                  config={'displayModeBar': True, 'scrollZoom': True}
                  )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Bars show the range of soil organic carbon density on land as a mean average within each country in metric tonnes per hectare (t ha-1), which are equal to about 1,000 kilograms or aproximately 2,205 pounds. Hover over any bar to view details for specific countries.",
               style={'text-align': 'left'}),
        html.P(children=[
            "Data source: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, ",
            html.A("6: 249-263.",
                   href='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2013MS000293',
                   target='_blank'  # opens link in new tab or window
                   )
            ],
               style={'text-align': 'left'}),
    ]),
    html.Br()
], body=True)

# --------------------------FOOD TRADE graph--------------------------

# take the sum total of exported tonnes by grouping food dataframe by Partner (importing) Country and append the sum as a column
dffood['Export_Quantity_Sum'] = dffood['Export_Quantity_2019_Value_tonnes'].groupby(dffood['Partner_Country_name']).transform('sum')
# take the distinct count of exported items by grouping food dataframe by Reporter (exporting) Country and append the count as a column
dffood['Export_Items_Count'] = dffood['Item'].groupby(dffood['Partner_Country_name']).transform('nunique')
# make numbers into a more human readable format, e.g., transform 12345591313 to '12.3 billion' for hover info
dffood['tradeVolume'] = dffood['Export_Quantity_Sum'].apply(lambda x: humanize.intword(x))


# food data scatterplot points
RiskFoodsFig = px.scatter(dffood, x='Export_Items_Count', y='Export_Quantity_Sum', size='Export_Quantity_Sum',
                          custom_data=['Partner_Country_name',  # 'Reporter_Country_name_x',
                                       'Export_Quantity_Sum',
                                       'Export_Items_Count'
                                       ]
                          )

# sort bars by mean SOCD, and suppress redundant axis titles, instead of xaxis={'categoryorder': 'mean ascending'} I pre-sorted the dataframe above, but still force sort here by explicit names
RiskFoodsFig.update_layout(
                           xaxis_title='Diversity of Foods Imported (How many unique items?)',  # Exported (How many unique items?)',
                           # move yaxis text to title area for readability; add empty line above it so it appears below the plotly toolbar options
                           title={
                               'text': 'Volume as Total Quantity of Foods Imported (tonnes)',
                               'xref': 'container',
                           },
                           yaxis_title='',  # moved to title attribute for readability
                           paper_bgcolor='#e8ece8',  # next tint variation up from a low tint of #dadeda
                           plot_bgcolor='#f7f5fc',  # violet tone of medium purple to help greens pop forward
                           yaxis={'gridcolor': '#e8ece8'},  # match grid lines shown to background to appear as showing through
                           font={'color': '#483628'})  # a dark shade of orange that appears dark brown
RiskFoodsFig.update_traces(
    # hard code single point color
    marker=dict(
        color='#a99e54',
        sizemin=10
    ),
    # set bolded title in hover text, and make a list of columns to customize how they appear in hover text
    hovertemplate="<br>".join([
        "<b>%{customdata[0]} </b><br>",  # bolded hover title included, since the separate hover_name is superseced by hovertemplae
        "Trade Volume: %{customdata[1]:,} tonnes imported",  # %{customdata[2]:,} tonnes exported", # note html tags can be used in string; comma sep formatted; note with tradeVolume use format .1f to 1 decimals
        "Trade Diversity: %{customdata[2]:} unique food products imported"  # %{customdata[3]:} unique food products exported",
    ])
)

riskFoods = dbc.Card([
    html.Div(children=[
        html.H5("Food Security Risk Analysis by Volume & Diversity of Food Trade Reliance"
                ),
        dcc.Graph(figure=RiskFoodsFig,
                  id="food-quadrant-chart",
                  config={'displayModeBar': True, 'scrollZoom': True}
                  )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Points show where each country falls in relation to these two major trade metrics as indicators of risk for a country's ability to feed its population. Countries in the upper right corner can generally be understood to be most at risk if food trade lines are affected by decreased production.",
               style={'text-align': 'left'}),
        html.P("All food products traded between countries are included in the total summary of items imported, in 2019, as measured in metric tonnes (vertical axis showing range with M representing millions of tonnes). While soil organic carbon content is a major factor determining agricultural productivity, those levels are not directly shown in this graph and there are many factors that can lead to trade volatility",  # The major grid lines dividing the four sections are set at the median, in other words the middle, of that range of global values as a benchmark to divide high or low in population and trade dependency, in relation to other countries.",
               style={'text-align': 'left'}),
        html.P(children=["Food and Agriculture Organization of the United Nations. (2020). FAOSTAT Detailed trade matrix: All Data Normalized. ",
                         html.A('https://www.fao.org/faostat/en/#data/TM',
                                href='https://www.fao.org/faostat/en/#data/TM',
                                target="_blank"  # opens link in new tab or window
                                )
                         ],
               style={'text-align': 'left'}
               )
    ]),
    html.Br()
], body=True)

tab1 = dbc.Tab([densityRanges], label="Density Ranges")
tab2 = dbc.Tab([riskFoods], label="At Risk Foods")
tab3 = dbc.Tab([whyCarbon], label="Why Carbon?")
tabs = dbc.Tabs(children=[tab1, tab2, tab3])


# create the app's layout with the named variables
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(navbar,
                        width=12)
            ]
        ),
        dbc.Row(
            [
                dbc.Col(appSubheading,
                        width={"size": "auto", "offset": 0},
                        md={"size": "auto", "offset": 1},
                        xxl={"size": "auto", "offset": 2}
                        ),
            ],
            justify="left",
            style={"padding-top": 95, "padding-bottom": 0}
        ),
        dbc.Row(
            [
                dbc.Col(mapExplorer,
                        width={"size": 11, "offset": 0}
                        )
            ],
            justify="center",
            style={"padding-top": 10, "padding-bottom": 25}
        ),
        dbc.Row(
            [
                dbc.Col(learnMore,
                        width={'size': 9, 'offset': 2}, md={'size': 5, 'offset': 6}
                        )
            ],
            style={"padding-top": 10, "padding-bottom": 10}
        ),
        dbc.Row(
            [
                dbc.Col(html.Br(),
                        width=12
                        )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Container(
                        tabs),
                    width={"size": 11, "offset": 0}
                )
            ],
            justify="center",
        ),
        dbc.Row(
            html.Div(children=[
                html.Br(),
                html.Br(),
                html.Footer(children=[
                    html.A(u"\u00A9"+" Kathryn Hurchla 2021",
                           href="http://kathrynhurchla.com",
                           target="_blank",
                           style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
                           ),
                    ], className="text-muted",
                ),
            ],
            ),
        ),
    ],
    fluid=True,
    className="dbc"
)

# ----------------------------------------------------------------------------------------
# callback decorators and functions
# connecting the Dropdown values to the graph


# simple selection on country directly
@app.callback(
    Output('map-socd', 'children'),
    [Input('reporter_country_dropdown', 'value')]
)
def update_selected_reporter_country(selected_reporter_country):
    # always make a copy of any dataframe to use in the function
    # define the subset of data that matches the selected values from both dropdown(s)
    dfsoil_sub = dfsoil
    # filter dataframe with geo points for single selection multi=False (default)
    dfsoil_sub1 = dfsoil_sub[(dfsoil_sub['Reporter_Country_name'] == selected_reporter_country)]

    # create figure variables for the graph object

    locations = [go.Scattermapbox(
        name='SOCD at Surface Depth to 4.5cm',
        lon=dfsoil_sub1['Reporter_Country_lon'],
        lat=dfsoil_sub1['Reporter_Country_lat'],
        mode='markers',
        marker=go.scattermapbox.Marker(
                                       size=dfsoil_sub['Reporter_Country_SOCD_depth4_5'],
                                       # add a sequential color scale based on shades of fuschia #ff00ff
                                       # bright hues range for contrast to map background layer
                                       # to more easily differentiate each separate point on map
                                       color=dfsoil_sub['Reporter_Country_SOCD_depth4_5'],
                                       colorscale='Agsunset_r',
                                       # show a colorbar for this colorscale range
                                       showscale=True,
                                       colorbar=dict(title="SOCD"
                                                     ),
                                       opacity=0.8,  # float or integer range between 0 and 1
                                       ),
        hovertemplate="Longitude: %{lon}<br>" + "Latitude: %{lat}<br><extra></extra>"  # hide secondary tag with empty extra tag
        )
    ]

    # add a mapbox image layer below the data
    layout = go.Layout(
                # commented out uirevision to allow map to reset zoom level to default when selection is changed
                # uirevision='foo',  # to preserve state of figure/map after callback activated
                # match background behind color legend to the page area graph sit on
                paper_bgcolor='#e4ebf5',  # Morph theme card background color,
                font=dict(color='#483628'),  # a dark shade of orange that appears dark brown
                clickmode='event+select',
                hovermode='closest',
                hoverdistance=2,
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    style='white-bg'
                ),
                autosize=True,
                margin=dict(l=0, r=0, t=35, b=0),
                mapbox_layers=[
                    {
                        'below': 'traces',
                        'sourcetype': 'raster',
                        'source': [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ]
    )

    # Return figure
    return dcc.Graph(config={'displayModeBar': True, 'scrollZoom': True},
                     figure={
                         'data': locations,
                         'layout': layout
                     })

# connect theLearn More button and modal with user interactions


@app.callback(
    Output("modal", "is_open"),
    [Input("learn-more-button", "n_clicks"), Input("learn-more-close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# ----------------------------------------------------------------------------------------
# run the app


if __name__ == '__main__':
    app.run_server(debug=True)  # if inside Jupyter Notebook, add use_reloader=False inside parens to turn off reloader
