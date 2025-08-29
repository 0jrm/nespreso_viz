import numpy as np
import plotly.graph_objs as go
import cmocean.cm as cm
import xarray as xr
from viz_utils.styles import NespresoStyles
try:
    import cartopy.feature as cfeature
    from cartopy.io import shapereader as shpreader
    from shapely.geometry import LineString, MultiLineString, box
except Exception:  # Optional dependency; figures will still render without coastlines
    cfeature = None
    shpreader = None
    LineString = None
    MultiLineString = None
    box = None
# from viz_utils.ocean_utils import *

class MainFigures:
    def __init__(self, data: xr.Dataset, styles: NespresoStyles):
        # Always normalize to numpy arrays with a leading time axis (size 1 if single-date)
        sss = data['SSS'].values
        sst = data['SST'].values
        aviso = data['AVISO'].values
        temp = data['Temperature'].values
        sal = data['Salinity'].values

        if sss.ndim == 2:
            sss = sss[np.newaxis, ...]
        if sst.ndim == 2:
            sst = sst[np.newaxis, ...]
        if aviso.ndim == 2:
            aviso = aviso[np.newaxis, ...]
        if temp.ndim == 3:
            temp = temp[np.newaxis, ...]
        if sal.ndim == 3:
            sal = sal[np.newaxis, ...]

        self.SSS = sss
        self.SST = sst
        self.aviso = aviso
        self.temp = temp
        self.sal = sal
        
        # Handle missing variables - create placeholders or remove references
        if 'T_error' in data.variables:
            terr = data['T_error'].values
            self.temp_err = terr if terr.ndim == 4 else terr[np.newaxis, ...]
        else:
            self.temp_err = np.zeros_like(self.temp)
            
        if 'S_error' in data.variables:
            serr = data['S_error'].values
            self.sal_err = serr if serr.ndim == 4 else serr[np.newaxis, ...]
        else:
            self.sal_err = np.zeros_like(self.sal)
            
        # MLD/OHC/Isotherm removed per latest dataset capabilities
            
        self.lats = data['lat'].values
        self.lons = data['lon'].values
        self.depths = data['depth'].values  # Add this line
        self.styles = styles

        # Pre-compute coastline traces for the default bbox
        self.bbox = dict(lon_min=-99, lon_max=-81, lat_min=18, lat_max=30)
        self.coastline_traces = self._generate_coastline_traces(self.bbox)

        # Calculate pressure for first 200 mts
        # th = 100
        # pressure = calculate_ocean_pressure(self.temp[:,:,:,:th], self.sal[:,:,:,:th], self.depths[:th])
        # self.mld = get_mld(self.sal[:,:,:,:th], self.temp[:,:,:,:th], pressure[:,:,:,:th])

    def make_figure(self, data, prof_locations_scatter, colorscheme, title, hovertemplate, colorbar_title, zmin=None, zmax=None):
        heatmap_trace = go.Heatmap(
            z=data,
            colorscale=self.styles.cmocean_to_plotly(colorscheme, 256),
            showscale=True,
            x=self.lons,
            y=self.lats,
            hovertemplate=hovertemplate,
            colorbar=dict(title={'text': colorbar_title, 'side': 'right'}, thickness=14, lenmode='fraction', len=0.9),
            zmin=zmin,
            zmax=zmax,
        )

        # Invisible corners to enforce reset axes ranges
        corner_trace = go.Scatter(
            x=[self.bbox['lon_min'], self.bbox['lon_max']],
            y=[self.bbox['lat_min'], self.bbox['lat_max']],
            mode='markers',
            marker=dict(size=0),
            opacity=0,
            hoverinfo='skip',
            showlegend=False,
        )

        traces = [heatmap_trace, corner_trace]
        # Add Cartopy-derived coastlines if available
        if self.coastline_traces:
            traces.extend(self.coastline_traces)
        traces.append(prof_locations_scatter)

        cur_fig = go.Figure(
            data=traces,
            layout=go.Layout(
                title=title,
                xaxis=dict(title="Longitude", range=[-99, -81]),
                yaxis=dict(title="Latitude", range=[18, 30]),
                dragmode="pan",
                height=self.styles.fig_height,
                margin=self.styles.margins,
                shapes=[]
            )
        )

        return cur_fig

    def _generate_coastline_traces(self, bbox):
        if cfeature is None or shpreader is None or box is None:
            return []
        try:
            traces = []
            clip_bbox = box(bbox["lon_min"], bbox["lat_min"], bbox["lon_max"], bbox["lat_max"])
            def extract_lines(geom):
                try:
                    from shapely.geometry import LineString as _LS, MultiLineString as _MLS
                except Exception:
                    return []
                if isinstance(geom, _LS):
                    return [geom]
                if isinstance(geom, _MLS):
                    return list(geom.geoms)
                if hasattr(geom, 'geoms'):
                    lines = []
                    for sub in geom.geoms:
                        lines.extend(extract_lines(sub))
                    return lines
                return []
            # First try the dedicated coastline lines
            try:
                shp_path = shpreader.natural_earth(resolution="50m", category="physical", name="coastline")
                reader = shpreader.Reader(shp_path)
                for geom in reader.geometries():
                    try:
                        inter = geom.intersection(clip_bbox)
                    except Exception:
                        continue
                    if inter.is_empty:
                        continue
                    geoms = extract_lines(inter)
                    for line in geoms:
                        xs, ys = line.xy
                        traces.append(go.Scattergl(x=xs, y=ys, mode="lines", line=dict(color="black", width=1), hoverinfo="skip", showlegend=False))
            except Exception:
                pass

            # Alternate attempt: iterate records (sometimes different driver backends)
            if not traces:
                try:
                    shp_path = shpreader.natural_earth(resolution="50m", category="physical", name="coastline")
                    reader = shpreader.Reader(shp_path)
                    for rec in reader.records():
                        geom = rec.geometry
                        try:
                            inter = geom.intersection(clip_bbox)
                        except Exception:
                            continue
                        if inter.is_empty:
                            continue
                        geoms = extract_lines(inter)
                        for line in geoms:
                            xs, ys = line.xy
                            traces.append(go.Scattergl(x=xs, y=ys, mode="lines", line=dict(color="black", width=1), hoverinfo="skip", showlegend=False))
                except Exception:
                    pass

            # Fallback: extract land boundaries
            if not traces:
                try:
                    land_path = shpreader.natural_earth(resolution="50m", category="physical", name="land")
                    reader = shpreader.Reader(land_path)
                    for geom in reader.geometries():
                        try:
                            inter = geom.intersection(clip_bbox)
                        except Exception:
                            continue
                        if inter.is_empty:
                            continue
                        # Use boundary to draw coast-like lines
                        boundary = inter.boundary
                        if boundary.is_empty:
                            continue
                        for line in extract_lines(boundary):
                            xs, ys = line.xy
                            traces.append(go.Scattergl(x=xs, y=ys, mode="lines", line=dict(color="black", width=1), hoverinfo="skip", showlegend=False))
                except Exception:
                    pass

                # Fallback to coarser resolution if still empty
                if not traces:
                    try:
                        land_path = shpreader.natural_earth(resolution="110m", category="physical", name="land")
                        reader = shpreader.Reader(land_path)
                        for geom in reader.geometries():
                            try:
                                inter = geom.intersection(clip_bbox)
                            except Exception:
                                continue
                            if inter.is_empty:
                                continue
                            boundary = inter.boundary
                            if boundary.is_empty:
                                continue
                            for line in extract_lines(boundary):
                                xs, ys = line.xy
                                traces.append(go.Scattergl(x=xs, y=ys, mode="lines", line=dict(color="black", width=1), hoverinfo="skip", showlegend=False))
                    except Exception:
                        pass

            # Last resort: use Cartopy's COASTLINE feature provider
            if not traces:
                try:
                    for geom in cfeature.COASTLINE.geometries():
                        try:
                            inter = geom.intersection(clip_bbox)
                        except Exception:
                            continue
                        if inter.is_empty:
                            continue
                        for line in extract_lines(inter):
                            xs, ys = line.xy
                            traces.append(go.Scattergl(x=xs, y=ys, mode="lines", line=dict(color="black", width=1), hoverinfo="skip", showlegend=False))
                except Exception:
                    pass

            return traces
        except Exception:
            return []

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
                        name='Profile Locations',
                        showlegend=False
                    )

        # -------------------------- AVISO -------------------------------
        fig_aviso = self.make_figure(
            self.aviso[date_idx, :, :],
            prof_locations,
            cm.curl,
            f"CMEMS ADT",
            'Lat: %{y}<br>Lon: %{x}<br>ADT: %{z:.2f} m<extra></extra>',
            'ADT [m]'
        )

        # -------------------------- SST -------------------------------
        fig_SST = self.make_figure(
            np.round(self.SST[date_idx,:,:] - 273.15, 2),
            prof_locations,
            cm.thermal,
            f"OISST SST",
            'Lat: %{y}<br>Lon: %{x}<br>Temp: %{z:.2f} °C<extra></extra>',
            'SST [°C]'
        )
        # -------------------------- SSS -------------------------------
        fig_SSS = self.make_figure(
            self.SSS[date_idx,:,:],
            prof_locations,
            cm.haline,
            f"SMAP SSS",
            'Lat: %{y}<br>Lon: %{x}<br>Salt: %{z:.2f} PSU<extra></extra>',
            'SSS [PSU]'
        )

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
                name='Profile Locations',
                showlegend=False
            )

        # -------------------------- Temp -------------------------------
        # depth_idx may exceed range; coerce safely
        depth_idx = int(depth_idx) if isinstance(depth_idx, (int, np.integer)) else 0
        if depth_idx < 0:
            depth_idx = 0
        if depth_idx >= self.depths.shape[0]:
            depth_idx = self.depths.shape[0] - 1
        fig_temp = self.make_figure(
            np.round(self.temp[date_idx,depth_idx,:,:], 2),
            prof_locations,
            cm.thermal,
            f"Synthetic T, {depth_idx} m",
            'Lat: %{y}<br>Lon: %{x}<br>Temp: %{z:.2f} °C<extra></extra>',
            'Temperature [°C]'
        )
        # -------------------------- Sal -------------------------------
        fig_sal = self.make_figure(
            self.sal[date_idx,depth_idx,:,:],
            prof_locations,
            cm.haline,
            f"Synthetic S, {depth_idx} m",
            'Lat: %{y}<br>Lon: %{x}<br>Salt: %{z:.2f} PSU<extra></extra>',
            'Salinity [PSU]'
        )
        # -------------------------- Temp Error -------------------------------
        # fig_temp_err = self.make_figure(np.round(self.temp_err[date_idx,depth_idx,:,:], 2), prof_locations, cm.thermal, 
                                    #  f"Temperature Error (Synthetic), {depth_idx} m, {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Temp Error: %{z:.1f} °C<extra></extra>')
        # -------------------------- Sal Error -------------------------------
        # fig_sal_err = self.make_figure(self.sal_err[date_idx,depth_idx,:,:], prof_locations, cm.haline, 
                                    #  f"Salinity Error (Synthetic),{depth_idx} m, {cur_date_str} ",  'Lat: %{y}<br>Lon: %{x}<br>Salt Error: %{z:.1f} PSU<extra></extra>')
        # OHC and Isotherm removed


        # ----------- Updates the figures with the last transect line drawn -----------
        # if trans_lines is not an empty array
        if trans_lines != []:
            fig_temp['layout']['shapes'] = [trans_lines]
            fig_sal['layout']['shapes'] = [trans_lines]
            # fig_temp_err['layout']['shapes'] = [trans_lines]
            # fig_sal_err['layout']['shapes'] = [trans_lines]

        return [fig_temp, fig_sal]
