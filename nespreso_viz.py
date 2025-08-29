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
import os
import re
from functools import lru_cache

# %% Make a basic dash interface to explore a NetCDF file

### Load available NetCDF files and default to the latest date
file_path = "/Net/work/ozavala/DATA/SubSurfaceFields/NeSPReSO"

date_regex = re.compile(r"nespreso_grid_(\d{4}-\d{2}-\d{2})\.nc$")

def _scan_available_dates(directory: str):
    try:
        candidates = [f for f in os.listdir(directory) if f.endswith('.nc')]
    except Exception as exc:
        print(f"Failed listing directory {directory}: {exc}")
        candidates = []
    date_to_file = {}
    for fname in candidates:
        m = date_regex.search(fname)
        if not m:
            continue
        date_str = m.group(1)
        full_path = os.path.join(directory, fname)
        # Keep the last occurrence if duplicates; they should point to same day
        date_to_file[date_str] = full_path
    sorted_dates = sorted(date_to_file.keys())
    # Convert to numpy datetime64[D]
    days = np.array([np.datetime64(d, 'D') for d in sorted_dates]) if sorted_dates else np.array([np.datetime64('2020-01-01')])
    return date_to_file, days

DATE_TO_FILE, dates = _scan_available_dates(file_path)
if dates.size == 0:
    # Fallback: try a known file
    default_file_name = '/Net/work/ozavala/DATA/SubSurfaceFields/NeSPReSO/nespreso_grid_2020-01-01.nc'
    ds = xr.open_dataset(default_file_name)
    dates = np.atleast_1d(ds['time'].values)
    print(f"Fallback time entries detected: {len(dates)}")
else:
    default_date_np = dates.max()
    default_date_str = str(default_date_np.astype('datetime64[D]'))
    default_file_name = DATE_TO_FILE.get(default_date_str)
    ds = xr.open_dataset(default_file_name)
    print(f"Loaded default dataset for {default_date_str}: {default_file_name}")

has_time_dim = len(dates) > 1
start_date = str(dates.max().astype('datetime64[D]')) if dates.size > 0 else '2024-04-01'
styles_obj = NespresoStyles(dates, start_date)
# Instantiate default objects for initial render
prof_obj = Profiles(ds, styles_obj)
trans_obj = Transects(ds, styles_obj)
mainfigs_obj = MainFigures(ds, styles_obj)

# Lightweight cache for datasets by date
@lru_cache(maxsize=16)
def get_ds_for_date(date_str: str):
    path = DATE_TO_FILE.get(date_str)
    if path is None:
        # Choose nearest available date
        if dates.size == 0:
            return ds
        target = np.datetime64(date_str)
        nearest_idx = int(np.argmin(np.abs(dates - target)))
        use_date = str(dates[nearest_idx].astype('datetime64[D]'))
        path = DATE_TO_FILE.get(use_date)
        print(f"Requested date {date_str} not found, using nearest {use_date}")
    try:
        cur_ds = xr.open_dataset(path)
        return cur_ds
    except Exception as exc:
        print(f"Failed to open dataset {path}: {exc}")
        return ds

def get_objs_for_date(date_str: str):
    cur_ds = get_ds_for_date(date_str)
    return MainFigures(cur_ds, styles_obj), Profiles(cur_ds, styles_obj), Transects(cur_ds, styles_obj)

currently_drawn_line_id = None

# Selected locations
transect_loc = [[24, -90], [24, -92]]

# Create Dash app (simplify base path for local debugging)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True

# Create layout with three rows and specified figures
app.layout = styles_obj.default_layout()

# =================== Date picker ===================
# Updates the date and the index of the date
@app.callback(
    Output('nespreso-predictions', 'children'),
    Output('cur_date', 'data'),
    Output('cur_date_str', 'data'),
    Input('date-picker-single', 'value'),
    Input('date-picker-single', 'date'),
    prevent_initial_call=False,
)
def update_calendar_store(selected_value, selected_date_legacy):
    print(f"update_calendar_store called with selected_value={selected_value}, date={selected_date_legacy}")
    # Support both Mantine (value) and DCC (date)
    selected_date = selected_value if selected_value else selected_date_legacy
    if not selected_date:
        selected_date = start_date
    # Compute formatted label and index within available dates
    try:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
    except Exception:
        selected_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    selected_date_str = selected_datetime.strftime("%b %d, %Y")

    if dates.size <= 1:
        date_idx = 0
    else:
        date_idx = int(np.argmin(np.abs(dates - np.datetime64(selected_date))))
    print(f"Selected date index within available pool: {date_idx}")

    return [f"NeSPReSO synthetics for {selected_date_str}", date_idx, selected_date]

# Fallback-only: sync Month/Year dropdowns with DatePicker and vice versa
@app.callback(
    Output('date-picker-single', 'initial_visible_month', allow_duplicate=True),
    Output('date-picker-single', 'date', allow_duplicate=True),
    Input('calendar_month', 'value'),
    Input('calendar_year', 'value'),
    State('date-picker-single', 'date'),
    prevent_initial_call=True,
)
def change_calendar_month_year(month_value, year_value, current_date):
    # If Mantine calendar is active, these inputs won't exist (callback will be suppressed by Dash)
    if month_value is None or year_value is None:
        raise dash.exceptions.PreventUpdate
    try:
        cur_day = int(current_date.split('-')[2]) if current_date else 1
    except Exception:
        cur_day = 1
    new_date_str = f"{int(year_value):04d}-{int(month_value):02d}-{min(cur_day, 28):02d}"
    try:
        if new_date_str not in DATE_TO_FILE:
            month_prefix = new_date_str[:7]
            month_candidates = sorted([d for d in DATE_TO_FILE.keys() if d.startswith(month_prefix)])
            if month_candidates:
                day_int = int(new_date_str.split('-')[2])
                def _dist(d):
                    return abs(int(d.split('-')[2]) - day_int)
                new_date_str = sorted(month_candidates, key=_dist)[0]
            else:
                target = np.datetime64(new_date_str)
                nearest_idx = int(np.argmin(np.abs(dates - target)))
                new_date_str = str(dates[nearest_idx].astype('datetime64[D]'))
    except Exception:
        pass
    return new_date_str, new_date_str

@app.callback(
    Output('calendar_month', 'value', allow_duplicate=True),
    Output('calendar_year', 'value', allow_duplicate=True),
    Input('date-picker-single', 'date'),
    prevent_initial_call=True,
)
def sync_month_year_with_date(date_value):
    if not date_value:
        date_value = start_date
    try:
        year = int(date_value.split('-')[0])
        month = int(date_value.split('-')[1])
    except Exception:
        dt = datetime.strptime(start_date, '%Y-%m-%d')
        year, month = dt.year, dt.month
    return month, year

# Keep DatePicker visible month in sync with Month/Year dropdowns
# Remove sync callbacks as month/year are handled inside the calendar popup

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
    Input('cur_date_str', 'data'),
    Input('trans_lines', 'data'),
    Input('show_all_sat', 'value'),
    Input('sat_field_selector', 'value'),
)
def update_satellite_figures(prof_loc, date_idx, cur_date_str, trans_lines, show_all_value, selected_field):
    print(f"update_satellite_figures -> date_idx={date_idx}, prof_loc_len={0 if not prof_loc else len(prof_loc)}, cur_date_str={cur_date_str}")
    # Guard
    if date_idx is None:
        date_idx = 0
    # If trans_lines is
    if trans_lines is None:
        trans_lines = []
    # Build figures for the chosen date
    date_key = cur_date_str if isinstance(cur_date_str, str) and len(cur_date_str) == 10 else start_date
    cur_mainfigs, _, _ = get_objs_for_date(date_key)
    # Coerce date_idx to be valid for the selected dataset (many daily files have a single time index)
    try:
        max_t = max(cur_mainfigs.SST.shape[0], cur_mainfigs.SSS.shape[0], cur_mainfigs.aviso.shape[0])
        local_idx = int(date_idx) if date_idx is not None else 0
        if local_idx < 0:
            local_idx = 0
        if local_idx >= max_t:
            local_idx = max_t - 1
    except Exception:
        local_idx = 0
    fig_aviso, fig_SST, fig_SSS = cur_mainfigs.update_satellite_figures(prof_loc, local_idx, trans_lines, cur_date_str)

    show_all = isinstance(show_all_value, list) and ('all' in show_all_value)
    if show_all:
        return [fig_aviso, fig_SST, fig_SSS]

    # Single mode: put the selected field in first slot
    if selected_field == 'AVISO':
        return [fig_aviso, cur_mainfigs.make_figure(np.nan*np.zeros_like(cur_mainfigs.SST[0]), go.Scatter(), cm.curl, '', '', '', None, None), cur_mainfigs.make_figure(np.nan*np.zeros_like(cur_mainfigs.SSS[0]), go.Scatter(), cm.curl, '', '', '', None, None)]
    if selected_field == 'SST':
        return [fig_SST, cur_mainfigs.make_figure(np.nan*np.zeros_like(cur_mainfigs.SST[0]), go.Scatter(), cm.curl, '', '', '', None, None), cur_mainfigs.make_figure(np.nan*np.zeros_like(cur_mainfigs.SSS[0]), go.Scatter(), cm.curl, '', '', '', None, None)]
    if selected_field == 'SSS':
        return [fig_SSS, cur_mainfigs.make_figure(np.nan*np.zeros_like(cur_mainfigs.SST[0]), go.Scatter(), cm.curl, '', '', '', None, None), cur_mainfigs.make_figure(np.nan*np.zeros_like(cur_mainfigs.SSS[0]), go.Scatter(), cm.curl, '', '', '', None, None)]
    return [fig_aviso, fig_SST, fig_SSS]


# =================== Nespresso maps figures ===================
# Update figure based on selections or a default example
@app.callback(
    Output('fig_temp', 'figure'),
    Output('fig_sal', 'figure'),
    Input('prof_loc', 'data'),
    Input('cur_date', 'data'),
    Input('cur_date_str', 'data'),
    Input('trans_lines', 'data'),
    Input('depth_idx', 'value'),
)
def update_nespreso_figures(prof_loc, date_idx, cur_date_str, trans_lines, depth_idx):
    print(f"update_nespreso_figures -> date_idx={date_idx}, depth_idx={depth_idx}, prof_loc_len={0 if not prof_loc else len(prof_loc)}")
    # Guards
    if date_idx is None:
        date_idx = 0
    if depth_idx is None:
        depth_idx = 0
    # If trans_lines is
    if trans_lines is None:
        trans_lines = []
    date_key = cur_date_str if isinstance(cur_date_str, str) and len(cur_date_str) == 10 else start_date
    cur_mainfigs, _, _ = get_objs_for_date(date_key)
    try:
        max_t = max(cur_mainfigs.temp.shape[0], cur_mainfigs.sal.shape[0])
        local_idx = int(date_idx) if date_idx is not None else 0
        if local_idx < 0:
            local_idx = 0
        if local_idx >= max_t:
            local_idx = max_t - 1
    except Exception:
        local_idx = 0
    fig_temp, fig_sal = cur_mainfigs.update_nespreso_maps(prof_loc, local_idx, depth_idx, trans_lines, cur_date_str)
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
    Input('cur_date_str', 'data'),
    Input('prof_loc', 'data'),
    Input('depth_selection', 'value'),
    Input('depth_idx', 'value'),
)
def update_profiles(date_idx, cur_date_str, prof_loc, depth_type, depth_idx):
    print(f"update_profiles -> date_idx={date_idx}, depth_type={depth_type}, depth_idx={depth_idx}, prof_loc_len={0 if not prof_loc else len(prof_loc)}")
    if date_idx is None:
        date_idx = 0
    if depth_idx is None:
        depth_idx = 0

    date_key = cur_date_str if isinstance(cur_date_str, str) and len(cur_date_str) == 10 else start_date
    _, cur_prof, _ = get_objs_for_date(date_key)
    # Clamp date index to available range
    try:
        max_t = max(cur_prof.temp.shape[0], cur_prof.sal.shape[0])
        local_idx = int(date_idx) if date_idx is not None else 0
        if local_idx < 0:
            local_idx = 0
        if local_idx >= max_t:
            local_idx = max_t - 1
    except Exception:
        local_idx = 0
    fig_temp_prof, fig_sal_prof = cur_prof.update_profiles(prof_loc, local_idx, 
                                                           depth_type, cur_date_str, 
                                                           depth_idx) 

    return fig_temp_prof, fig_sal_prof


## ================================ Transects ====================================
@app.callback(
    Output('fig_temp_trans', 'figure'),
    Output('fig_sal_trans', 'figure'),
    Input('cur_date', 'data'),
    Input('cur_date_str', 'data'),
    Input('trans_lines', 'data'),
    Input('depth_selection', 'value'),
)
def update_trans(date_idx, cur_date_str, cur_transect, depth_type):
    if cur_transect != []:
        x0, y0 = cur_transect['x0'], cur_transect['y0']
        x1, y1 = cur_transect['x1'], cur_transect['y1']

        transect_loc = [[y0, x0], [y1, x1]]
        date_key = cur_date_str if isinstance(cur_date_str, str) and len(cur_date_str) == 10 else start_date
        _, _, cur_trans = get_objs_for_date(date_key)
        # Clamp date index
        try:
            max_t = int(cur_trans.temp.sizes.get('time', 1))
            local_idx = int(date_idx) if date_idx is not None else 0
            if local_idx < 0:
                local_idx = 0
            if local_idx >= max_t:
                local_idx = max_t - 1
        except Exception:
            local_idx = 0
        return cur_trans.update_transects(transect_loc, local_idx, depth_type, cur_date_str)
    else:  # Prevent update
        raise dash.exceptions.PreventUpdate

# =================== UI visibility helpers ===================
@app.callback(
    Output('sat_field_selector_container', 'style'),
    Input('show_all_sat', 'value'),
)
def toggle_field_selector_visibility(show_all_value):
    show_all = isinstance(show_all_value, list) and ('all' in show_all_value)
    return ({'display': 'none'} if show_all else {})

@app.callback(
    Output('nespreso-date', 'children'),
    Input('cur_date_str', 'data'),
)
def update_title(cur_date_str):
    try:
        dt = datetime.strptime(cur_date_str, '%Y-%m-%d')
        label = dt.strftime("%b %d, %Y")
    except Exception:
        label = cur_date_str
    return f"Satellite fields for {label}"


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

