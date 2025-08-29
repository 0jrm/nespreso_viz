
import numpy as np
import plotly.graph_objs as go
import cmocean.cm as cm
import math

class Transects:
    def __init__(self, data, styles, res = 0.04): 
        # Ensure DataArrays with a leading time dimension for interpolation
        self.temp = data['Temperature']
        self.sal = data['Salinity']
        if 'time' not in self.temp.dims:
            self.temp = self.temp.expand_dims(dim='time')
        if 'time' not in self.sal.dims:
            self.sal = self.sal.expand_dims(dim='time')
            
        self.depths = data.variables['depth'][:]  # Add this line
        self.styles = styles
        self.res = res # Resolution for transect

    def haversine(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points
        on the Earth specified in decimal degrees of latitude and longitude.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in kilometers. Use 3956 for miles. Determines return value units.
        r = 6371  # Use 6371 for kilometers
        return c * r

    def update_transects(self, transect_loc, date_idx, depth_type, cur_date_str):
        x0 = transect_loc[0][1]
        y0 = transect_loc[0][0]
        x1 = transect_loc[1][1]
        y1 = transect_loc[1][0]

        # Calculate the Euclidean distance between start and end points
        line_length = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        line_length_km = self.haversine(y0, x0, y1, x1)
        
        # Determine the number of points based on the resolution
        resolution = self.res
        num_points = int(line_length / resolution)
        
        # Interpolating points along the line
        lons = np.linspace(x0, x1, num_points)
        lats = np.linspace(y0, y1, num_points)
        dist = np.array(range(num_points))*line_length_km/num_points
        dist = np.round(dist).astype(int)
        
        if depth_type.find('upto') != -1:
            max_depth = int(depth_type[-3:])
            depth_idx = slice(0, max_depth)
        else:
            interval = int(depth_type[-2:])
            depth_idx = slice(None, None, interval) 

        # Temperature
        temp_time_selected = self.temp.isel(time=date_idx, depth=depth_idx)
        temp_interp = temp_time_selected.interp(lat=('points', lats), lon=('points', lons))


        # Salinity
        sal_time_selected = self.sal.isel(time=date_idx, depth=depth_idx)
        sal_interp = sal_time_selected.interp(lat=('points', lats), lon=('points', lons))

        if not transect_loc:
            def_fig = go.Figure(layout=go.Layout(height=self.styles.fig_height, margin=self.styles.margins))
            fig_temp_trans = def_fig
            fig_sal_trans = def_fig
        else:
            # --------------- TEMP Transect -------------------
        # zoom, pan, select, lasso, orbit, turntable, zoomInGeo, zoomOutGeo, autoScale2d, resetScale2d, hoverClosestCartesian, hoverClosestGeo, hoverClosestGl2d, hoverClosestPie, toggleHover, resetViews, toggleSpikelines, resetViewMapbox

            # Temperature
            fig_temp_trans = go.Figure(
                data=[go.Heatmap(z=np.rot90(temp_interp, 2), 
                                 x=dist[::-1],
                                 y=temp_interp.depth.values[::-1],
                                 colorscale=self.styles.cmocean_to_plotly(cm.thermal,256), 
                                 hovertemplate='Temp: %{z:.1f} °C<extra></extra>',
                                 showscale=True,
                                 colorbar=dict(title='Temperature [°C]'))], 
                layout=go.Layout(title=f"Synthetic T Transect", 
                                 xaxis=dict(title="Distance (km)"),
                                 yaxis=dict(title="Depth (m)", autorange="reversed"),
                                 dragmode="pan", 
                                 height=int(self.styles.fig_height*1.1),
                                 margin=self.styles.margins,
                             ),
            )

            # Salinity
            fig_sal_trans = go.Figure(
                data=[go.Heatmap(z=np.rot90(sal_interp, 2),
                                 x=dist[::-1],
                                 y=temp_interp.depth.values[::-1],
                                 colorscale=self.styles.cmocean_to_plotly(cm.haline,256), 
                                 hovertemplate='Sal: %{z:.1f} PSU<extra></extra>',
                                 showscale=True,
                                 colorbar=dict(title='Salinity [PSU]'))], 
                layout=go.Layout(title=f"Synthetic S Transect", 
                                 xaxis=dict(title="Distance (km)"),
                                 yaxis=dict(title="Depth (m)", autorange="reversed"),
                                 dragmode="pan", 
                                 height=int(self.styles.fig_height*1.1),
                                 margin=self.styles.margins,
                             ),
            ) 
            return [fig_temp_trans, fig_sal_trans] 