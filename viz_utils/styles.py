
# Make a class NespresoStyles that will contain all the styles and configurations for the figures
import numpy as np
import cmocean.cm as cm
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from datetime import datetime

# /doc 
class NespresoStyles:
    """
    A class that defines the visual styles and configurations for Nespreso visualization.

    Attributes:
        colors (list): A list of color codes used for plotting.
        fig_height (int): The height of the figures.
        margins (dict): A dictionary that defines the margins of the figures.
        def_figure (dict): A dictionary that defines the default figure configuration.
        def_config (dict): A dictionary that defines the default configuration for the plotly graph.
        trans_config (dict): A dictionary that defines the configuration for the plotly graph in transects.
        prof_config (dict): A dictionary that defines the configuration for the plotly graph in profiles.

    Methods:
        __init__(self, dates: np.ndarray, start_date: str): Initializes the NespresoStyles object.
        cmocean_to_plotly(self, cmap, pl_entries): Converts a cmocean colormap to a plotly compatible colormap.
        default_layout(self): Returns the default layout for the Nespreso visualization.
    """

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    fig_height = 300
    margins = dict(
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=30,  # top margin
        pad=0  # padding
    )

    def_figure = {'data':[],'layout':{'height':fig_height}}

    def_config = dict(
        modeBarButtonsToRemove=['zoomOut2d','zoomIn2d','lasso','select2d'],
        modeBarButtonsToAdd=['drawline','eraseshape'],
        scrollZoom=True,
        displayModeBar=True,
        displaylogo=False,
    )

    trans_config = dict(
        modeBarButtonsToRemove=['zoomOut2d','zoomIn2d', 'autoScale2d','lasso', 'select'],
        modeBarButtonsToAdd=['drawline','eraseshape'],
        scrollZoom=True,
        displayModeBar=True,
        displaylogo=False,
    )

    prof_config = trans_config

    def __init__(self, dates: np.ndarray, start_date: str):
        """
        Initializes the NespresoStyles object.

        Args:
            dates (np.ndarray): An array of dates.
            start_date (str): The start date in the format '%Y-%m-%d'.
        """
        self.days = dates
        self.selected_date = datetime.strptime(start_date, '%Y-%m-%d')

    def cmocean_to_plotly(self, cmap, pl_entries):
        '''
        This function converts a cmocean colormap to a plotly compatible colormap
        '''
        h = 1.0/(pl_entries-1)
        pl_colorscale = []
        
        for k in range(pl_entries):
            r, g, b = cmap(k*h)[:3]
            r = int(round(float(r)*255))
            g = int(round(float(g)*255))
            b = int(round(float(b)*255))
            pl_colorscale.append([k*h, f'rgb({r}, {g}, {b})'])
            
        return pl_colorscale

    def default_layout(self):
        selected_date_str = self.selected_date.strftime("%b %d, %Y")
        layout = dbc.Container(fluid=True, children=[
                dbc.Row([
                dbc.Col(html.H1(f"Satellite fields for {selected_date_str}", id='nespreso-date'), style={'textAlign': 'center'})
                ]),
                # Include a Row with a calendar picker
                # ------------------- Top row of figures (Satellite primary)-------------------
                dbc.Row([
                    dbc.Col(
                        [
                        dbc.Row([
                            dbc.Col(html.P("Satellite display:"), width=4),
                            dbc.Col(
                                dbc.Checklist(
                                    id='show_all_sat',
                                    options=[{'label': 'Show all maps', 'value': 'all'}],
                                    value=[],
                                    switch=True
                                ),
                                width=8
                            ),
                        ]),
                        dbc.Row([
                            dbc.Col(html.P("Field:"), width=3),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='sat_field_selector',
                                    options=[
                                        {'label': 'AVISO', 'value': 'AVISO'},
                                        {'label': 'SST', 'value': 'SST'},
                                        {'label': 'SSS', 'value': 'SSS'},
                                    ],
                                    value='AVISO',
                                    clearable=False
                                ),
                                width=9
                            ),
                        ]),
                        dbc.Row([
                            dbc.Col(dcc.DatePickerSingle(
                                id='date-picker-single',
                                calendar_orientation='vertical',
                                # Restrict date selection to March 1st to April 30th 2024
                                min_date_allowed=min(self.days).astype('datetime64[D]').astype(str),
                                max_date_allowed=max(self.days).astype('datetime64[D]').astype(str),
                                date=min(self.days).astype('datetime64[D]').astype(str),
                                clearable=True,
                                with_portal=True,
                            )),
                        ]),
                        dbc.Row([
                            dbc.Col(
                                dbc.Checklist(
                                    id='enable_add_points',
                                    options=[{'label': 'Add Points', 'value': 'on'}],
                                    value=['on'],
                                    switch=True
                                ),
                                width=12
                            ),
                        ])
                        ], xl=2, lg=3, md=4),
                    dbc.Col(dcc.Graph(id='fig_aviso', figure=self.def_figure, config=self.def_config), xl=10, lg=9, md=8),
                    dcc.Store(id='prof_loc', data=[]),
                    dcc.Store(id='cur_date', data=0),
                    dcc.Store(id='cur_date_str', data=selected_date_str),
                    dcc.Store(id='trans_lines', data=[]),
                ]),
                # ------------------- Second row of satellite figures (secondary maps) -------------------
                dbc.Row([
                    dbc.Col([], xl=2, lg=3, md=4),
                    dbc.Col(dcc.Graph(id='fig_SST',  figure=self.def_figure, config=self.def_config),   xl=3, lg=4, md=6),
                    dbc.Col(dcc.Graph(id='fig_SSS',  figure=self.def_figure, config=self.def_config),   xl=3, lg=4, md=6),
                    dbc.Col([], xl=4, lg=1, md=0),
                ]),
                # ------------------- Line separator  -------------------
                dbc.Row([
                dbc.Col(html.Hr(), style={'borderTop': '1px solid #ccc', 'margin': '20px 0'},xl=2, lg=1, md=0),  
                dbc.Col(html.H1("NeSPReSO synthetics", id='nespreso-predictions', style={'textAlign': 'center'}), xl=8, lg=10, md=11),
                dbc.Col(html.Hr(), style={'borderTop': '1px solid #ccc', 'margin': '20px 0'},xl=2, lg=1, md=0),  
                ]),
                # ------------------- Depth slider row (below title) -------------------
                dbc.Row([
                    dbc.Col([], xl=2, lg=3, md=4),
                    dbc.Col([
                        html.Div("Display depth:", className="text-right font-weight-bold"),
                        dcc.Slider(
                            id='depth_idx',
                            min=0,
                            max=1800,
                            step=10,
                            value=0,
                            marks={0: '0', 500: '500', 1000: '1000', 1800: '1800'},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className='small-slider'
                        )
                    ], xl=8, lg=9, md=8, sm=12),
                    dbc.Col([], xl=2, lg=0, md=0),
                ]),
                # ------------------- NeSPReSO maps (match satellite sizes) -------------------
                dbc.Row([
                    dbc.Col([], xl=2, lg=3, md=4),
                    dbc.Col(dcc.Graph(id='fig_temp', figure=self.def_figure, config=self.trans_config), xl=3, lg=4, md=6),
                    dbc.Col(dcc.Graph(id='fig_sal',  figure=self.def_figure, config=self.trans_config), xl=3, lg=4, md=6),
                    dbc.Col([], xl=4, lg=1, md=0),
                ]),
                # ------------------- Transect controls and plots -------------------
                dbc.Row([
                    dbc.Col(
                        html.Div(id='transect_controls', children=[
                            html.Div(
                                ["Use 'Draw line' ", html.I(className='bi bi-vector-pen'), " to draw transects."],
                                id='instructions_transect',
                                style={'padding':'6px','fontStyle':'italic'}
                            ),
                            dbc.ButtonGroup([
                                dbc.Button("Undo", id="undo_transect", color="secondary"),
                                dbc.Button("Clear", id="clear_transect", color="danger"),
                            ], id='transect_buttons', style={'display':'none'})
                        ]), width=12
                    )
                ]),
                dbc.Row([
                    dbc.Col([], xl=2, lg=3, md=4),
                    dbc.Col(dcc.Graph(id='fig_temp_trans', figure=self.def_figure, config=self.trans_config), xl=3, lg=4, md=6),
                    dbc.Col(dcc.Graph(id='fig_sal_trans',  figure=self.def_figure, config=self.trans_config), xl=3, lg=4, md=6),
                    dbc.Col([], xl=4, lg=1, md=0),
                ]),
                # ------------------- Depth options between transect and profile -------------------
                dbc.Row([
                    dbc.Col([], xl=2, lg=3, md=4),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(html.P("Depth options:"), width=3),
                            dbc.Col(dcc.Dropdown(
                                id='depth_selection',
                                options=[
                                    {'label': 'First 100 m', 'value': 'upto100'},
                                    {'label': 'First 200 m', 'value': 'upto200'},
                                    {'label': 'First 300 m', 'value': 'upto300'},
                                    {'label': 'First 500 m', 'value': 'upto500'},
                                    {'label': '(all) Every 10 m', 'value': 'every10'},
                                    {'label': '(all) Every 5 m', 'value': 'every05'},
                                    {'label': '(all) Every 1 m', 'value': 'every01'},
                                ],
                                value='upto500',
                                clearable=False
                            ), width=9)
                        ])
                    ], xl=8, lg=9, md=8),
                    dbc.Col([], xl=2, lg=0, md=0)
                ]),
                # ------------------- Profile controls and plots -------------------
                dbc.Row([
                    dbc.Col(
                        html.Div(id='profile_controls', children=[
                            html.Div(
                                ["Use 'Pan and add profile' ", html.I(className='bi bi-arrows-move'), " then click to see T and S profiles at locations."],
                                id='instructions_profile',
                                style={'padding':'6px','fontStyle':'italic'}
                            ),
                            dbc.ButtonGroup([
                                dbc.Button("Undo", id="undo_prof", color="secondary"),
                                dbc.Button("Clear", id="clear_prof", color="danger"),
                            ], id='profile_buttons', style={'display':'none'})
                        ]), width=12
                    )
                ]),
                dbc.Row([
                    dbc.Col([], xl=2, lg=3, md=4),
                    dbc.Col(dcc.Graph(id='fig_temp_prof', figure=self.def_figure,config=self.trans_config),  xl=3, lg=4, md=6),
                    dbc.Col(dcc.Graph(id='fig_sal_prof', figure=self.def_figure,config=self.prof_config),    xl=3, lg=4, md=6),
                    dbc.Col([], xl=4, lg=1, md=0),
                ]),
                # ------------------- Additional metrics (removed MLD) -------------------
                dbc.Row([]),

            ])

        return layout