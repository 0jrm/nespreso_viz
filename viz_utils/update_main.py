import numpy as np
import plotly.graph_objs as go
import cmocean.cm as cm
import xarray as xr
from viz_utils.styles import NespresoStyles
# from viz_utils.ocean_utils import *

class MainFigures:
    def __init__(self, data: xr.Dataset, styles: NespresoStyles):
        self.SSS = data.variables['SSS'][:]
        self.SST = data.variables['SST'][:]
        self.temp = data.variables['Temperature'][:]
        self.sal = data.variables['Salinity'][:]
        self.temp_err = data.variables['T_error'][:]
        self.sal_err = data.variables['S_error'][:]
        self.aviso = data.variables['AVISO'][:]
        self.mld = data.variables['MLD'][:]
        self.ohc = data.variables['OHC'][:]
        self.iso = data.variables['Isotherm'][:]
        self.lats = data.variables['lat'][:]
        self.lons = data.variables['lon'][:]
        self.depths = data.variables['depth'][:]  # Add this line
        self.styles = styles

        # Calculate pressure for first 200 mts
        # th = 100
        # pressure = calculate_ocean_pressure(self.temp[:,:,:,:th], self.sal[:,:,:,:th], self.depths[:th])
        # self.mld = get_mld(self.sal[:,:,:,:th], self.temp[:,:,:,:th], pressure[:,:,:,:th])

    def make_figure(self, data, prof_locations_scatter, colorscheme, title, hovertemplate):
        cur_fig = go.Figure(
            data=[
                go.Heatmap(
                    z=data,
                    colorscale=self.styles.cmocean_to_plotly(colorscheme, 256),
                    showscale=True,
                    x=self.lons,
                    y=self.lats,
                    hovertemplate=hovertemplate
                ),
                prof_locations_scatter
            ],
            layout=go.Layout(
                title=title,
                xaxis=dict(title="Longitude"),
                yaxis=dict(title="Latitude"),
                dragmode="pan",
                height=self.styles.fig_height,
                margin=self.styles.margins,
                shapes=[]
            )
        )

        return cur_fig

    def update_satellite_figures(self, prof_loc, date_idx, trans_lines, cur_date_str):
        if not prof_loc:
            prof_locations = go.Scatter()
        else:
            prof_locations = go.Scatter(
                        x=[loc[1] for loc in prof_loc],
                        y=[loc[0] for loc in prof_loc],
                        mode='markers',
                        marker=dict(
                            color=self.styles.colors[:len(prof_loc)],
                            size=10,
                            symbol='circle'
                        ),
                        name='Profile Locations'
                    )

        # -------------------------- AVISO -------------------------------
        fig_aviso = self.make_figure(self.aviso[date_idx, :, :], prof_locations, cm.curl, 
                                     f"AVISO {cur_date_str}", 'Lat: %{y}<br>Lon: %{x}<br>ADT: %{z:.1f} m<extra></extra>')

        # -------------------------- SST -------------------------------
        fig_SST = self.make_figure(np.round(self.SST[date_idx,:,:], 2), prof_locations, cm.thermal, 
                                     f"Temperature (satellite) {cur_date_str}",  'Lat: %{y}<br>Lon: %{x}<br>Temp: %{z:.1f} °F<extra></extra>')
        # -------------------------- SSS -------------------------------
        fig_SSS = self.make_figure(self.SSS[date_idx,:,:], prof_locations, cm.haline, 
                                     f"Salinity (satellite)  {cur_date_str}",  'Lat: %{y}<br>Lon: %{x}<br>Salt: %{z:.1f} PSU<extra></extra>')

        # Customize the figures as needed based on control_value and the data

        # ----------- Updates the figures with the last transect line drawn -----------
        # if trans_lines is not an empty array
        if trans_lines != []:
            fig_aviso['layout']['shapes'] = [trans_lines]
            fig_SST['layout']['shapes'] = [trans_lines]
            fig_SSS['layout']['shapes'] = [trans_lines]

        return [fig_aviso, fig_SST, fig_SSS]

    def update_nespreso_maps(self, prof_loc, date_idx, depth_idx, trans_lines, cur_date_str):
        """
        Update the metric figures based on the given parameters.

        Parameters:
        prof_loc (list): List of profile locations.
        date_idx (int): Index of the current date.
        trans_lines (list): List of transect lines.
        cur_date_str (str): Current date string.

        Returns:
        list: List of updated metric figures.
        """
        if not prof_loc:
            prof_locations = go.Scatter()
        else:
            prof_locations = go.Scatter(
                x=[loc[1] for loc in prof_loc],
                y=[loc[0] for loc in prof_loc],
                mode='markers',
                marker=dict(
                    color=self.styles.colors[:len(prof_loc)],
                    size=10,
                    symbol='circle'
                ),
                name='Profile Locations'
            )

        # -------------------------- Temp -------------------------------
        fig_temp = self.make_figure(np.round(self.temp[date_idx,depth_idx,:,:], 2), prof_locations, cm.thermal, 
                                     f"Temperature (Synthetic), {depth_idx} m, {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Temp: %{z:.1f} °C<extra></extra>')
        # -------------------------- Sal -------------------------------
        fig_sal = self.make_figure(self.sal[date_idx,depth_idx,:,:], prof_locations, cm.haline, 
                                     f"Salinity (Synthetic),{depth_idx} m, {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Salt: %{z:.1f} PSU<extra></extra>')
        # -------------------------- MLD -------------------------------
        fig_MLD = self.make_figure(self.mld[date_idx,:,:], prof_locations, cm.deep, 
                                     f"MLD (Synthetic), {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>MLD: %{z:.1f} m<extra></extra>')
        # -------------------------- Temp Error -------------------------------
        # fig_temp_err = self.make_figure(np.round(self.temp_err[date_idx,depth_idx,:,:], 2), prof_locations, cm.thermal, 
                                    #  f"Temperature Error (Synthetic), {depth_idx} m, {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Temp Error: %{z:.1f} °C<extra></extra>')
        # -------------------------- Sal Error -------------------------------
        # fig_sal_err = self.make_figure(self.sal_err[date_idx,depth_idx,:,:], prof_locations, cm.haline, 
                                    #  f"Salinity Error (Synthetic),{depth_idx} m, {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Salt Error: %{z:.1f} PSU<extra></extra>')
        # -------------------------- OHC -------------------------------
        fig_ohc = self.make_figure(self.ohc[date_idx,:,:], prof_locations, cm.thermal, 
                                     f"Ocean Heat Content (Synthetic), {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>OHC: %{z:.1f} J/m^2<extra></extra>')
        # -------------------------- Iso -------------------------------
        fig_iso = self.make_figure(self.iso[date_idx,:,:], prof_locations, cm.deep, 
                                     f"26 degrees Celsius isotherm depth (Synthetic), {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Isotherm: %{z:.1f} (m)<extra></extra>')


        # ----------- Updates the figures with the last transect line drawn -----------
        # if trans_lines is not an empty array
        if trans_lines != []:
            fig_temp['layout']['shapes'] = [trans_lines]
            fig_sal['layout']['shapes'] = [trans_lines]
            fig_MLD['layout']['shapes'] = [trans_lines]
            fig_ohc['layout']['shapes'] = [trans_lines]
            fig_iso['layout']['shapes'] = [trans_lines]
            # fig_temp_err['layout']['shapes'] = [trans_lines]
            # fig_sal_err['layout']['shapes'] = [trans_lines]

        # return [fig_temp, fig_temp_err, fig_sal, fig_sal_err, fig_MLD]
        return [fig_temp, fig_sal, fig_MLD, fig_ohc, fig_iso]
