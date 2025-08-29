
# Make a class NespresoStyles that will contain all the styles and configurations for the figures
import numpy as np
import cmocean.cm as cm
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import os
try:
    import dash_mantine_components as dmc
except Exception:
    dmc = None
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
        r=60,  # right margin to accommodate colorbar
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
        # Optionally compute disabled days (disabled for now to avoid heavy payloads)
        disabled_days = []
        # Precompute default values
        latest = max(self.days).astype('datetime64[D]').astype(str)
        use_dmc = (dmc is not None) and (os.environ.get('USE_DMC_CAL', '0') == '1')
        layout = dbc.Container(fluid=True, children=[
                # ------------------- Calendar at the very top -------------------
                dbc.Row([
                    dbc.Col(html.Span("Select data date (Year, Month, Day):", className="font-weight-bold"), width="auto"),
                    dbc.Col(
                        (
                            dmc.DatePickerInput(
                                id='date-picker-single',
                                value=latest,
                                minDate=min(self.days).astype('datetime64[D]').astype(str),
                                maxDate=max(self.days).astype('datetime64[D]').astype(str),
                                dropdownType='popover',
                                clearable=False,
                                valueFormat='YYYY-MM-DD',
                                firstDayOfWeek=0,
                                style={"minWidth":"260px"}
                            )
                            if use_dmc
                            else html.Div([
                                dcc.Dropdown(
                                    id='calendar_year',
                                    options=[
                                        {'label': str(y), 'value': y}
                                        for y in sorted(list({int(str(d).split('-')[0]) for d in self.days.astype('datetime64[D]')}))
                                    ],
                                    value=int(latest.split('-')[0]),
                                    clearable=False,
                                    style={"minWidth":"120px", "display":"inline-block", "marginRight":"8px"}
                                ),
                                dcc.Dropdown(
                                    id='calendar_month',
                                    options=[
                                        {'label': name, 'value': m}
                                        for m, name in [
                                            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                                            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                                            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
                                        ]
                                    ],
                                    value=int(latest.split('-')[1]),
                                    clearable=False,
                                    style={"minWidth":"160px", "display":"inline-block", "marginRight":"8px"}
                                ),
                                dcc.DatePickerSingle(
                                    id='date-picker-single',
                                    calendar_orientation='vertical',
                                    min_date_allowed=min(self.days).astype('datetime64[D]').astype(str),
                                    max_date_allowed=max(self.days).astype('datetime64[D]').astype(str),
                                    initial_visible_month=max(self.days).astype('datetime64[D]').astype(str),
                                    date=latest,
                                    clearable=False,
                                ),
                            ])
                        )
                    ),
                ]),

                dbc.Row([
                    dbc.Col(html.H1(f"Satellite fields for {selected_date_str}", id='nespreso-date'), style={'textAlign': 'center'})
                ]),
                # ------------------- Top row of figures (Satellite primary)-------------------
                dbc.Row([
                    dbc.Col(
                        [
                        dbc.Row([
                            dbc.Col(html.P("Satellite display:"), width="auto"),
                            dbc.Col(
                                dbc.Checklist(
                                    id='show_all_sat',
                                    options=[{'label': 'Show all maps', 'value': 'all'}],
                                    value=[],
                                    switch=True
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Div([
                                    html.Span("Field:", style={"marginRight":"6px"}),
                                    dcc.Dropdown(
                                        id='sat_field_selector',
                                        options=[
                                            {'label': 'CMEMS ADT', 'value': 'AVISO'},
                                            {'label': 'OISST SST', 'value': 'SST'},
                                            {'label': 'SMAP SSS', 'value': 'SSS'},
                                        ],
                                        value='AVISO',
                                        clearable=False,
                                        style={"minWidth":"180px"}
                                    )
                                ], id='sat_field_selector_container'),
                                width="auto"
                            ),
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
                        ], style={'display': 'none'})
                        ], xl=2, lg=3, md=4),
                    dbc.Col(dcc.Graph(id='fig_aviso', figure=self.def_figure, config=self.def_config), xl=10, lg=9, md=8),
                    dcc.Store(id='prof_loc', data=[]),
                    dcc.Store(id='cur_date', data=0),
                    dcc.Store(id='cur_date_str', data=max(self.days).astype('datetime64[D]').astype(str)),
                    dcc.Store(id='trans_lines', data=[]),
                ]),
                # ------------------- Second row of satellite figures (secondary maps) -------------------
                dbc.Row([
                    dbc.Col(dcc.Graph(id='fig_SST',  figure=self.def_figure, config=self.def_config),   xl=6, lg=6, md=6),
                    dbc.Col(dcc.Graph(id='fig_SSS',  figure=self.def_figure, config=self.def_config),   xl=6, lg=6, md=6),
                ]),
                # ------------------- Line separator  -------------------
                dbc.Row([
                    dbc.Col(html.H1("NeSPReSO synthetics", id='nespreso-predictions', style={'textAlign': 'center'}), width=12)
                ]),
                # ------------------- Depth slider row (below title) -------------------
                dbc.Row([
                    dbc.Col(html.Div("Display depth:", className="font-weight-bold"), width="auto"),
                    dbc.Col(dcc.Slider(
                        id='depth_idx',
                        min=0,
                        max=1800,
                        step=10,
                        value=0,
                        marks={0: '0', 500: '500', 1000: '1000', 1800: '1800'},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className='small-slider'
                    ), width=10),
                ]),
                # ------------------- NeSPReSO maps (match satellite sizes) -------------------
                dbc.Row([
                    dbc.Col(dcc.Graph(id='fig_temp', figure=self.def_figure, config=self.trans_config), xl=6, lg=6, md=6),
                    dbc.Col(dcc.Graph(id='fig_sal',  figure=self.def_figure, config=self.trans_config), xl=6, lg=6, md=6),
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
                    dbc.Col(dcc.Graph(id='fig_temp_trans', figure=self.def_figure, config=self.trans_config), xl=6, lg=6, md=6),
                    dbc.Col(dcc.Graph(id='fig_sal_trans',  figure=self.def_figure, config=self.trans_config), xl=6, lg=6, md=6),
                ]),
                # ------------------- Depth options between transect and profile -------------------
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(html.P("Depth options (transect and profile views):"), width=3),
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
                    ], xl=12, lg=12, md=12),
                ]),
                # ------------------- Profile controls and plots -------------------
                dbc.Row([
                    dbc.Col(
                        html.Div(id='profile_controls', children=[
                            html.Div(
                                ["Click any map to add profile points, then view T and S profiles at locations."],
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
                    dbc.Col(dcc.Graph(id='fig_temp_prof', figure=self.def_figure,config=self.trans_config),  xl=6, lg=6, md=6),
                    dbc.Col(dcc.Graph(id='fig_sal_prof', figure=self.def_figure,config=self.prof_config),    xl=6, lg=6, md=6),
                ]),
                # ------------------- Additional metrics (removed MLD) -------------------
                dbc.Row([]),

            ])

        return layout