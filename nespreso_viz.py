import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import xarray as xr
import numpy as np
from viz_utils.update_prof import Profiles
from viz_utils.styles import NespresoStyles
from viz_utils.update_trans import Transects
from viz_utils.update_main import MainFigures
from datetime import datetime
import time

# %% Make a basic dash interface to explore a NetCDF file
import plotly.graph_objs as go

# Load your NetCDF data
file_name = '/data/SubsurfaceFields/NeSPReSO_20240101_to_20240131.nc'
ds = xr.open_dataset(file_name)
dates = ds['time'].values

start_date = '2024-04-01'
styles_obj = NespresoStyles(dates, start_date)
prof_obj = Profiles(ds, styles_obj)
trans_obj = Transects(ds, styles_obj)
mainfigs_obj = MainFigures(ds, styles_obj)

currently_drawn_line_id = None

# Selected locations
transect_loc = [[24, -90], [24, -92]]

# Create Dash app
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__)
server = app.server

# Create layout with three rows and specified figures
app.layout = styles_obj.default_layout()

# =================== Date picker ===================
# Updates the date and the index of the date
@app.callback(
    Output('nespreso-date', 'children'),
    Output('cur_date', 'data'),
    Output('cur_date_str', 'data'),
    Input('date-picker-single', 'date'),
)
def update_calendar_store(selected_date):
    if not selected_date:
        selected_datetime = start_date
        selected_date_str = datetime.strptime(start_date, '%Y-%m-%d').strftime("%b %d, %Y")
    else:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
        selected_date_str = datetime.strptime(selected_date, '%Y-%m-%d').strftime("%b %d, %Y")

    dates_np = np.array(dates, dtype='datetime64')
    date_idx = np.argmin(np.abs(dates_np - np.datetime64(selected_datetime)))

    return [f"NesPreso date {selected_date_str}", date_idx, selected_date_str]

# =================== Profile locations ===================
@app.callback(
    Output('prof_loc', 'data'),
    Input('clear_prof', 'n_clicks'),
    Input('fig_aviso', 'clickData'),
    Input('fig_SST', 'clickData'),
    Input('fig_SSS', 'clickData'),
    State('prof_loc', 'data')
)
def update_profiles_loc(n_clicks, clickData_aviso, clickData_temp, clickData_sal, prof_loc):
    # Placeholder function to generate figures. Customize according to your data.
    # Using go.Heatmap plot aviso

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    click_data = None

    if trigger_id == 'fig_aviso':
        click_data = clickData_aviso
    elif trigger_id == 'fig_SST':
        click_data = clickData_temp
    elif trigger_id == 'fig_SSS':
        click_data = clickData_sal
    elif trigger_id == 'clear_prof':
        return []

    if click_data is not None:
        lat = click_data['points'][0]['y']
        lon = click_data['points'][0]['x']
        print(f"Adding profile at {lat}, {lon}")
        prof_loc.append([lat, lon])

    return prof_loc

## ================================ Transects Locations ====================================
@app.callback(
    Output('trans_lines', 'data'),
    [Input('fig_aviso', 'relayoutData'),
     Input('fig_SST', 'relayoutData'),
     Input('fig_SSS', 'relayoutData')],
)
def update_transect_locations(relayout_data_aviso, relayout_data_temp, relayout_data_sal):

    if not relayout_data_aviso and not relayout_data_temp and not relayout_data_sal:
        raise dash.exceptions.PreventUpdate

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    relayout_data = None
    if trigger_id == 'fig_aviso':
        relayout_data = relayout_data_aviso
    elif trigger_id == 'fig_SST':
        relayout_data = relayout_data_temp
    elif trigger_id == 'fig_SSS':
        relayout_data = relayout_data_sal

    if relayout_data and 'shapes' in relayout_data:
        new_shape = relayout_data['shapes'][-1]

        # Remove non-valid properties
        new_shape.pop('label', None)
        # Add the new line with a unique name
        new_shape['name'] = str(id(new_shape))
        return new_shape
    else:
        raise dash.exceptions.PreventUpdate

# =================== Satellite figures ===================
# Update figure based on selections or a default example
@app.callback(
    Output('fig_aviso', 'figure'),
    Output('fig_SST', 'figure'),
    Output('fig_SSS', 'figure'),
    Input('prof_loc', 'data'),
    Input('cur_date', 'data'),
    Input('trans_lines', 'data'),
    State('cur_date_str', 'data'),
)
def update_satellite_figures(prof_loc, date_idx, trans_lines, cur_date_str):
    # If trans_lines is
    if trans_lines is None:
        trans_lines = []

    fig_aviso, fig_SST, fig_SSS = mainfigs_obj.update_satellite_figures(prof_loc, date_idx, trans_lines, cur_date_str)

    return [fig_aviso, fig_SST, fig_SSS]


# =================== Nespresso maps figures ===================
# Update figure based on selections or a default example
@app.callback(
    Output('fig_temp', 'figure'),
    # Output('fig_temp_err', 'figure'),
    Output('fig_sal', 'figure'),
    # Output('fig_sal_err', 'figure'),
    Output('fig_mld', 'figure'),
    Output('fig_ohc', 'figure'),
    Output('fig_iso', 'figure'),
    Input('prof_loc', 'data'),
    Input('cur_date', 'data'),
    Input('trans_lines', 'data'),
    Input('depth_idx', 'value'),
    State('cur_date_str', 'data'),
)
def update_nespreso_figures(prof_loc, date_idx, trans_lines, depth_idx, cur_date_str):
    # If trans_lines is
    if trans_lines is None:
        trans_lines = []

    fig_temp, fig_sal, fig_mld, fig_ohc, fig_iso = mainfigs_obj.update_nespreso_maps(prof_loc, date_idx, depth_idx, trans_lines, cur_date_str)

    # return [fig_temp, fig_temp_err, fig_sal, fig_sal_err, fig_mld]
    return [fig_temp, fig_sal, fig_mld, fig_ohc, fig_iso]

## ================================ Profiles figures ====================================
@app.callback(
    Output('fig_temp_prof', 'figure'),
    Output('fig_sal_prof', 'figure'),
    Input('cur_date', 'data'),
    Input('prof_loc', 'data'),
    Input('depth_selection', 'value'),
    Input('depth_idx', 'value'),
    State('cur_date_str', 'data'),
)
def update_profiles(date_idx, prof_loc, depth_type, depth_idx, cur_date_str):

    fig_temp_prof, fig_sal_prof = prof_obj.update_profiles(prof_loc, date_idx, 
                                                           depth_type, cur_date_str, 
                                                           depth_idx) 

    return fig_temp_prof, fig_sal_prof


## ================================ Transects ====================================
@app.callback(
    Output('fig_temp_trans', 'figure'),
    Output('fig_sal_trans', 'figure'),
    Input('cur_date', 'data'),
    Input('trans_lines', 'data'),
    Input('depth_selection', 'value'),
    State('cur_date_str', 'data'),
)
def update_trans(date_idx, cur_transect, depth_type, cur_date_str):
    if cur_transect != []:
        x0, y0 = cur_transect['x0'], cur_transect['y0']
        x1, y1 = cur_transect['x1'], cur_transect['y1']

        transect_loc = [[y0, x0], [y1, x1]]
        return trans_obj.update_transects(transect_loc, date_idx, depth_type, cur_date_str)
    else:  # Prevent update
        raise dash.exceptions.PreventUpdate


if __name__ == '__main__':
    # Debug mode
   app.run_server(debug=True)

    # Production mode at ip 144.174.7.151
    # app.run_server(debug=False, host='144.174.7.151', port=8050)
    # app.run_server(debug=False, host='10.146.19.57', port=8050)

#     MLD
# TropicalHeatPotentialContent
# Integral up to 26 degrees -
# and depth of the 26 degrees

# RTOFS (Operational NOAA model (two models, regular and experimental. 
  # Both on the cloud access points. Ask scott for 'same' access to the cloud))
# GOFS 3.1 (retired on June 10th) (ISOP?) (Replaced by some version of the earth system model)
# MOM6 with Matthieu?  (Not ready)
# TOFS with Rafael Ramos (MASTER measurments)

# CMEMS
# HAFS (Doesn't assimilate data in the ocean) Data from RTOFS, then MOM6

# NCDIS Ocean Heat Content
# Navi Global Ocean
# OFS
# Julio (Nemo nature)
# Bruce Cornell Scripps Ganesh (MitGCM 4DVar)
# Andy Moore (ROMS 4DVar)
# Hyocom (3DVar)
# Ryooing (ROMS 4DVar)v

