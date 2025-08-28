#!/bin/env python3
# /etc/httpd/conf/ozavala_custom_wsgi.conf
import dash
from dash import Input, Output, State
import plotly.graph_objs as go
import cmocean.cm as cm
import dash_bootstrap_components as dbc
import numpy as np
import xarray as xr
import numpy as np
from viz_utils.update_prof import Profiles
from viz_utils.styles import NespresoStyles
from viz_utils.update_trans import Transects
from viz_utils.update_main import MainFigures
from datetime import datetime

# %% Make a basic dash interface to explore a NetCDF file

# Load your NetCDF data
file_path = "/Net/work/ozavala/DATA/SubSurfaceFields/NeSPReSO"
file_name = '/Net/work/ozavala/DATA/SubSurfaceFields/NeSPReSO/nespreso_grid_2020-01-01.nc'
# file_name = 'data/NeSPReSO_20230801_to_20230910.nc'

ds = xr.open_dataset(file_name)

# Normalize time to an array of at least length 1
_raw_time = ds['time'].values
dates = np.atleast_1d(_raw_time)
has_time_dim = len(dates) > 1
print(f"Time entries detected: {len(dates)}")

start_date = '2024-04-01'
styles_obj = NespresoStyles(dates, start_date)
prof_obj = Profiles(ds, styles_obj)
trans_obj = Transects(ds, styles_obj)
mainfigs_obj = MainFigures(ds, styles_obj)

currently_drawn_line_id = None

# Selected locations
transect_loc = [[24, -90], [24, -92]]

# Create Dash app (simplify base path for local debugging)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = app.server

# Create layout with three rows and specified figures
app.layout = styles_obj.default_layout()

# =================== Date picker ===================
# Updates the date and the index of the date
@app.callback(
    Output('nespreso-predictions', 'children'),
    Output('cur_date', 'data'),
    Output('cur_date_str', 'data'),
    Input('date-picker-single', 'date'),
)
def update_calendar_store(selected_date):
    print(f"update_calendar_store called with selected_date: {selected_date}")
    
    if not selected_date:
        selected_datetime = start_date
        selected_date_str = datetime.strptime(start_date, '%Y-%m-%d').strftime("%b %d, %Y")
        print(f"No date selected, using default: {selected_date_str}")
    else:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
        selected_date_str = datetime.strptime(selected_date, '%Y-%m-%d').strftime("%b %d, %Y")
        print(f"Date selected: {selected_date_str}")

    # Handle single time case
    if not has_time_dim:
        # Single time - always return index 0
        date_idx = 0
        print(f"Single time file: using date_idx = {date_idx}")
    else:
        # Multiple times - find closest match
        dates_np = np.array(dates, dtype='datetime64')
        date_idx = np.argmin(np.abs(dates_np - np.datetime64(selected_datetime)))
        print(f"Multiple time file: using date_idx = {date_idx}")

    return [f"NeSPReSO synthetics for {selected_date_str}", date_idx, selected_date_str]

# =================== Profile locations ===================
@app.callback(
    Output('prof_loc', 'data'),
    Input('clear_prof', 'n_clicks'),
    Input('undo_prof', 'n_clicks'),
    Input('fig_aviso', 'clickData'),
    Input('fig_SST', 'clickData'),
    Input('fig_SSS', 'clickData'),
    Input('fig_temp', 'clickData'),
    Input('fig_sal', 'clickData'),
    Input('enable_add_points', 'value'),
    State('prof_loc', 'data')
)
def update_profiles_loc(n_clicks_clear, n_clicks_undo, clickData_aviso, clickData_temp, clickData_sal, clickData_temp_syn, clickData_sal_syn, enable_add_points, prof_loc):
    # Placeholder function to generate figures. Customize according to your data.

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
    elif trigger_id == 'fig_temp':
        click_data = clickData_temp_syn
    elif trigger_id == 'fig_sal':
        click_data = clickData_sal_syn
    elif trigger_id == 'clear_prof':
        return []
    elif trigger_id == 'undo_prof':
        if prof_loc:
            prof_loc.pop()
        return prof_loc

    # Only add when toggle is on
    if click_data is not None and enable_add_points and ('on' in enable_add_points):
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
     Input('fig_SSS', 'relayoutData'),
     Input('fig_temp', 'relayoutData'),
     Input('fig_sal', 'relayoutData'),
     Input('clear_transect', 'n_clicks'),
     Input('undo_transect', 'n_clicks')],
)
def update_transect_locations(relayout_data_aviso, relayout_data_temp, relayout_data_sal, relayout_data_temp_syn, relayout_data_sal_syn, n_clicks_clear, n_clicks_undo):

    if not relayout_data_aviso and not relayout_data_temp and not relayout_data_sal and not relayout_data_temp_syn and not relayout_data_sal_syn and not n_clicks_clear and not n_clicks_undo:
        raise dash.exceptions.PreventUpdate

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id in ['clear_transect', 'undo_transect']:
        return []

    relayout_data = None
    if trigger_id == 'fig_aviso':
        relayout_data = relayout_data_aviso
    elif trigger_id == 'fig_SST':
        relayout_data = relayout_data_temp
    elif trigger_id == 'fig_SSS':
        relayout_data = relayout_data_sal
    elif trigger_id == 'fig_temp':
        relayout_data = relayout_data_temp_syn
    elif trigger_id == 'fig_sal':
        relayout_data = relayout_data_sal_syn

    if relayout_data and 'shapes' in relayout_data:
        new_shape = relayout_data['shapes'][-1]
        # Only accept line shapes for transects
        if new_shape.get('type', 'line') != 'line':
            raise dash.exceptions.PreventUpdate
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
    Input('show_all_sat', 'value'),
    Input('sat_field_selector', 'value'),
    State('cur_date_str', 'data'),
)
def update_satellite_figures(prof_loc, date_idx, trans_lines, show_all_value, selected_field, cur_date_str):
    print(f"update_satellite_figures -> date_idx={date_idx}, prof_loc_len={0 if not prof_loc else len(prof_loc)}, cur_date_str={cur_date_str}")
    # Guard
    if date_idx is None:
        date_idx = 0
    # If trans_lines is
    if trans_lines is None:
        trans_lines = []

    fig_aviso, fig_SST, fig_SSS = mainfigs_obj.update_satellite_figures(prof_loc, date_idx, trans_lines, cur_date_str)

    show_all = isinstance(show_all_value, list) and ('all' in show_all_value)
    if show_all:
        return [fig_aviso, fig_SST, fig_SSS]

    # Single mode: put the selected field in first slot
    if selected_field == 'AVISO':
        return [fig_aviso, mainfigs_obj.make_figure(np.nan*np.zeros_like(mainfigs_obj.SST[0]), go.Scatter(), cm.curl, '', '', '', None, None), mainfigs_obj.make_figure(np.nan*np.zeros_like(mainfigs_obj.SSS[0]), go.Scatter(), cm.curl, '', '', '', None, None)]
    if selected_field == 'SST':
        return [fig_SST, mainfigs_obj.make_figure(np.nan*np.zeros_like(mainfigs_obj.SST[0]), go.Scatter(), cm.curl, '', '', '', None, None), mainfigs_obj.make_figure(np.nan*np.zeros_like(mainfigs_obj.SSS[0]), go.Scatter(), cm.curl, '', '', '', None, None)]
    if selected_field == 'SSS':
        return [fig_SSS, mainfigs_obj.make_figure(np.nan*np.zeros_like(mainfigs_obj.SST[0]), go.Scatter(), cm.curl, '', '', '', None, None), mainfigs_obj.make_figure(np.nan*np.zeros_like(mainfigs_obj.SSS[0]), go.Scatter(), cm.curl, '', '', '', None, None)]
    return [fig_aviso, fig_SST, fig_SSS]


# =================== Nespresso maps figures ===================
# Update figure based on selections or a default example
@app.callback(
    Output('fig_temp', 'figure'),
    Output('fig_sal', 'figure'),
    Input('prof_loc', 'data'),
    Input('cur_date', 'data'),
    Input('trans_lines', 'data'),
    Input('depth_idx', 'value'),
    State('cur_date_str', 'data'),
)
def update_nespreso_figures(prof_loc, date_idx, trans_lines, depth_idx, cur_date_str):
    print(f"update_nespreso_figures -> date_idx={date_idx}, depth_idx={depth_idx}, prof_loc_len={0 if not prof_loc else len(prof_loc)}")
    # Guards
    if date_idx is None:
        date_idx = 0
    if depth_idx is None:
        depth_idx = 0
    # If trans_lines is
    if trans_lines is None:
        trans_lines = []

    fig_temp, fig_sal = mainfigs_obj.update_nespreso_maps(prof_loc, date_idx, depth_idx, trans_lines, cur_date_str)
    return [fig_temp, fig_sal]

# =================== Satellite layout visibility ===================
@app.callback(
    Output('fig_aviso', 'style'),
    Output('fig_SST', 'style'),
    Output('fig_SSS', 'style'),
    Input('show_all_sat', 'value'),
    Input('sat_field_selector', 'value'),
)
def toggle_satellite_visibility(show_all_value, selected_field):
    show_all = isinstance(show_all_value, list) and ('all' in show_all_value)
    visible_style = {}
    hidden_style = {'display': 'none'}
    if show_all:
        return visible_style, visible_style, visible_style
    # Single mode: always show first-slot graph only
    return visible_style, hidden_style, hidden_style

# =================== Instructions and buttons toggling ===================
@app.callback(
    Output('instructions_profile', 'style'),
    Output('profile_buttons', 'style'),
    Input('prof_loc', 'data'),
)
def toggle_profile_instructions(prof_loc):
    has_points = bool(prof_loc)
    return ({'padding':'6px','fontStyle':'italic','display': 'none'} if has_points else {'padding':'6px','fontStyle':'italic'}), \
           ({} if has_points else {'display':'none'})

@app.callback(
    Output('instructions_transect', 'style'),
    Output('transect_buttons', 'style'),
    Input('trans_lines', 'data'),
)
def toggle_transect_instructions(trans_lines):
    has_line = bool(trans_lines)
    return ({'padding':'6px','fontStyle':'italic','display': 'none'} if has_line else {'padding':'6px','fontStyle':'italic'}), \
           ({} if has_line else {'display':'none'})

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
    print(f"update_profiles -> date_idx={date_idx}, depth_type={depth_type}, depth_idx={depth_idx}, prof_loc_len={0 if not prof_loc else len(prof_loc)}")
    if date_idx is None:
        date_idx = 0
    if depth_idx is None:
        depth_idx = 0

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
   app.run(debug=False)

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

