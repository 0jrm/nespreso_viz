
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
        r=36,  # tighter right margin; colorbar sits closer
        b=0,  # bottom margin
        t=36,  # increased top margin to avoid title clipping
        pad=0  # padding
    )

    # Typography and theme
    font_family = "Inter, Roboto, Lato, system-ui, -apple-system, 'Segoe UI', Arial, sans-serif"
    font_sizes = {
        'base': 14,
        'axis_title': 16,
        'tick': 13,
        'title': 18,
        'legend': 14,
    }
    paper_bgcolor = "#f2f4f8"
    plot_bgcolor = "#eceff3"

    # Will be initialized in __init__ to include theme defaults
    def_figure = {'data': [], 'layout': {'height': fig_height}}

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
        # Default empty figure with theme
        self.def_figure = {
            'data': [],
            'layout': {
                'height': self.fig_height,
                'paper_bgcolor': self.paper_bgcolor,
                'plot_bgcolor': self.plot_bgcolor,
                'font': {'family': self.font_family, 'size': self.font_sizes['base']},
                'margin': self.margins,
            }
        }

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
        layout = dbc.Container(fluid=True, style={'backgroundColor': '#f8f9fa'}, children=[
                # ------------------- Citation bar -------------------
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                dbc.Row([
                                    dbc.Col(
                                        html.Div([
                                            html.Span("NeSPReSO (Neural Synthetic Profiles from Remote Sensing and Observations)", className="citation-text", style={'fontSize': '30px'}),
                                            html.Br(),
                                            html.Span([
                                                "Miranda et al., 2025, Ocean Modelling. ",
                                                html.A(
                                                    "DOI: 10.1016/j.ocemod.2025.102550",
                                                    href="https://doi.org/10.1016/j.ocemod.2025.102550",
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                    className="citation-text"
                                                )
                                            ], className="citation-text")
                                        ]),
                                        align='center'
                                    ),
                                    dbc.Col(
                                        dbc.Button(html.I(className='bi bi-info-circle'), id='about_toggle', color='link', className='about-icon'),
                                        width='auto', align='center'
                                    )
                                ], align='center')
                            ), className='citation-bar'
                        ), width=12
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody([
                                html.Div([
                                    html.Strong("Method:"),
                                    html.Span(" Neural network trained on Argo + satellite data (ADT, SST, SSS), reduced via PCA, reconstructs subsurface T/S profiles up to 1800 meters with 1m resolution."),
                                ], style={'marginBottom':'5px'}),
                                html.Div([
                                    html.Strong("Performance:"),
                                    html.Span(" Outperforms Multiple Linear Regression (MLR), Gravest Empirical Modes (GEM), and Navy's Improved Synthetic Ocean Profiles (ISOP) in Gulf of Mexico tests (lower RMSE and bias, higher R²)."),
                                ], style={'marginBottom':'5px'}),
                                html.Div([
                                    html.Strong("Limitations:"),
                                    html.Span(" Tuned for Gulf of Mexico; may struggle with submesoscale processes and in regions of sparse satellite fidelity; depth limited to 0-1800 m.", style={'marginBottom':'5px'}),
                                ]),
                            ]), className='about-panel'), id='about_collapse', is_open=False
                        ), width=12
                    )
                ]),
                # ------------------- Control Bar -------------------
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
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
                                    dbc.Col(
                                        dbc.Button(
                                            "Download NeSPReSO data",
                                            id="btn-download",
                                            color="primary",
                                            className="btn-modern",
                                            style={"minWidth":"200px"}
                                        ),
                                        width="auto"
                                    ),
                                ], align='center', className='mb-2'),
                                dbc.Row([
                                    dbc.Col(html.Span("Satellite display:", className="font-weight-bold"), width="auto"),
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
                                    dbc.Col(
                                        dbc.Checklist(
                                            id='enable_add_points',
                                            options=[{'label': 'Add Points', 'value': 'on'}],
                                            value=['on'],
                                            switch=True
                                        ),
                                        width="auto", style={'display': 'none'}
                                    ),
                                ], align='center', className='mb-2'),
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
                                    ), width=6),
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
                                    ), width=4),
                                ], align='center')
                            ]),
                            className='control-bar'
                        ), width=12
                    )
                ]),

                # ------------------- Download component -------------------
                dcc.Download(id="download-dataframe-csv"),

                # ------------------- Section heading -------------------
                dbc.Row([
                    dbc.Col(html.H1(f"Satellite data for {selected_date_str}", id='nespreso-date'), style={'textAlign': 'center'})
                ]),

                # ------------------- Top figure (primary) -------------------
                dbc.Row([
                    dbc.Col(
                        dbc.Card(dbc.CardBody([dcc.Graph(id='fig_aviso', figure=self.def_figure, config=self.def_config)], style={'backgroundColor':'#f2f4f8'}), className='viz-card', style={'backgroundColor':'#f2f4f8','border':'none'}),
                        xl=6, lg=6, md=6
                    ),
                    dcc.Store(id='prof_loc', data=[]),
                    dcc.Store(id='cur_date', data=0),
                    dcc.Store(id='cur_date_str', data=max(self.days).astype('datetime64[D]').astype(str)),
                    dcc.Store(id='trans_lines', data=[]),
                ], justify='center'),

                # ------------------- Secondary satellite figures -------------------
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_SST',  figure=self.def_figure, config=self.def_config)], style={'backgroundColor':'#f2f4f8'}), className='viz-card', style={'backgroundColor':'#f2f4f8','border':'none'}),   xl=6, lg=6, md=6),
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_SSS',  figure=self.def_figure, config=self.def_config)], style={'backgroundColor':'#f2f4f8'}), className='viz-card', style={'backgroundColor':'#f2f4f8','border':'none'}),   xl=6, lg=6, md=6),
                ]),

                # ------------------- NeSPReSO heading -------------------
                dbc.Row([
                    dbc.Col(html.H1("NeSPReSO synthetics", id='nespreso-predictions', style={'textAlign': 'center'}), width=12)
                ]),

                # ------------------- NeSPReSO maps -------------------
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_temp', figure=self.def_figure, config=self.trans_config), html.Div("Generated with NeSPReSO (Miranda et al. 2025)", className='viz-footer')], style={'backgroundColor':'#f2f4f8'}), className='viz-card', style={'backgroundColor':'#f2f4f8', 'border':'none'}), xl=6, lg=6, md=6),
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_sal',  figure=self.def_figure, config=self.trans_config), html.Div("Generated with NeSPReSO (Miranda et al. 2025)", className='viz-footer')], style={'backgroundColor':'#f2f4f8'}), className='viz-card', style={'backgroundColor':'#f2f4f8', 'border':'none'}), xl=6, lg=6, md=6),
                ]),

                # ------------------- Transect controls and plots -------------------
                dbc.Row([
                    dbc.Col(
                        html.Div(id='transect_controls', children=[
                            html.Div(
                                ["To see T and S transects, use 'Draw line' ", html.I(className='bi bi-vector-pen'), " on any map to specify it's location."],
                                id='instructions_transect',
                                style={'padding':'6px','fontStyle':'italic'}
                            ),
                            dbc.ButtonGroup([
                                dbc.Button("Clear transect", id="clear_transect", className="btn-modern btn-clear", color='danger'),
                            ], id='transect_buttons', style={'display':'none'})
                        ]), width=12
                    )
                ]),
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_temp_trans', figure=self.def_figure, config=self.trans_config), html.Div("Generated with NeSPReSO (Miranda et al. 2025)", className='viz-footer')], style={'backgroundColor':'#f1f3f5'}), className='viz-card viz-dense', style={'backgroundColor':'#f1f3f5', 'border':'none'}), xl=6, lg=6, md=6),
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_sal_trans',  figure=self.def_figure, config=self.trans_config), html.Div("Generated with NeSPReSO (Miranda et al. 2025)", className='viz-footer')], style={'backgroundColor':'#f1f3f5'}), className='viz-card viz-dense', style={'backgroundColor':'#f1f3f5', 'border':'none'}), xl=6, lg=6, md=6),
                ]),

                # ------------------- Profile controls and plots -------------------
                dbc.Row([
                    dbc.Col(
                        html.Div(id='profile_controls', children=[
                            html.Div(
                                ["To view T and S profiles, click on any map at the desired locations."],
                                id='instructions_profile',
                                style={'padding':'6px','fontStyle':'italic'}
                            ),
                            dbc.ButtonGroup([
                                dbc.Button("Undo last point", id="undo_prof", className="btn-modern btn-undo", color='warning'),
                                dbc.Button("Clear points", id="clear_prof", className="btn-modern btn-clear", color='danger'),
                            ], id='profile_buttons', style={'display':'none'})
                        ]), width=12
                    )
                ]),
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_temp_prof', figure=self.def_figure,config=self.trans_config), html.Div("Generated with NeSPReSO (Miranda et al. 2025)", className='viz-footer')], style={'backgroundColor':'#f1f3f5'}),  className='viz-card viz-dense', style={'backgroundColor':'#f1f3f5', 'border':'none'}),  xl=6, lg=6, md=6),
                    dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(id='fig_sal_prof',  figure=self.def_figure,config=self.prof_config), html.Div("Generated with NeSPReSO (Miranda et al. 2025)", className='viz-footer')], style={'backgroundColor':'#f1f3f5'}),    className='viz-card viz-dense', style={'backgroundColor':'#f1f3f5', 'border':'none'}),  xl=6, lg=6, md=6),
                ]),

                # ------------------- Additional metrics (removed MLD) -------------------
                dbc.Row([]),

            ])

        return layout