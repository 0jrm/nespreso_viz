import numpy as np
import plotly.graph_objs as go

class Profiles:
    def __init__(self, data, styles):
        # Normalize to numpy with leading time axis
        temp = data['Temperature'].values
        sal = data['Salinity'].values
        if temp.ndim == 3:
            temp = temp[np.newaxis, ...]
        if sal.ndim == 3:
            sal = sal[np.newaxis, ...]
        self.temp = temp
        self.sal = sal

        self.lats = data['lat'].values
        self.lons = data['lon'].values
        self.depths = data['depth'].values  # Add this line
        self.styles = styles# Add this line

    def update_profiles(self, prof_loc, date_idx, depth_type, cur_date_str, main_depth_idx):
        # ================================ Profiles ====================================

        if not prof_loc:
            def_fig = go.Figure(layout=go.Layout(height=self.styles.fig_height, margin=self.styles.margins))
            fig_temp_prof = def_fig
            fig_sal_prof = def_fig
        else:

            if depth_type.find('upto') != -1:
                max_depth = int(depth_type[-3:])
                depth_idx = slice(0, max_depth)
            else:
                interval = int(depth_type[-2:])
                depth_idx = slice(None, None, interval) 

            # Locate the closest index from lat and lon
            lat_idx = []
            lon_idx = []
            loc_names = []
            temp_profiles = []
            salinity_profiles = []
            for loc in prof_loc:
                lat = loc[0]
                lon = loc[1]
                loc_names.append(f'{round(lat,2)},{round(lon,2)}')
                lat_idx = np.argmin(np.abs(self.lats - lat))  # Use self.lats (numpy array)
                lon_idx = np.argmin(np.abs(self.lons - lon))  # Use self.lons (numpy array)
                temp_profiles.append(self.temp[date_idx, depth_idx, lat_idx, lon_idx])  # Use self.temp
                salinity_profiles.append(self.sal[date_idx, depth_idx, lat_idx, lon_idx])  # Use self.sal
            # --------------- Temp profile -------------------
            fig_temp_prof = go.Figure()
            for i, temp_profile in enumerate(temp_profiles):
                fig_temp_prof.add_trace(go.Scatter(x=temp_profile, y=self.depths[depth_idx], mode='markers', 
                                                   hovertemplate='Temp: %{x:.1f} °C, Depth %{y} m<extra></extra>',
                                                   name=f'{loc_names[i]}', marker=dict(color=self.styles.colors[i])))  # Use self.depths and self.colors
            
            fig_temp_prof.update_layout(
                title=f"Temperature Profiles {cur_date_str}",
                xaxis=dict(title="Temperature (°C)"),
                yaxis=dict(title="Depth (m)", autorange="reversed"),
                dragmode="pan",
                height=self.styles.fig_height,  
                margin=self.styles.margins,  
            )
            # --------------- Salinity profile -------------------
            fig_sal_prof = go.Figure()
            for i, sal_profile in enumerate(salinity_profiles):
                fig_sal_prof.add_trace(go.Scatter(x=sal_profile, y=self.depths[depth_idx], mode='markers', 
                                                  hovertemplate='Sal: %{x:.1f} PSU, Depth %{y} m<extra></extra>',
                                                  name=f'{loc_names[i]}', marker=dict(color=self.styles.colors[i])))  # Use self.depths and self.colors

            if main_depth_idx > 0:
                min_sal = np.min([np.min(sal) for sal in salinity_profiles])
                max_sal = np.max([np.max(sal) for sal in salinity_profiles])
                min_temp = np.min([np.min(temp) for temp in temp_profiles])
                max_temp = np.max([np.max(temp) for temp in temp_profiles])

                # Add a line using shapes
                fig_sal_prof.add_shape(
                    type="line",
                    x0=min_sal, y0=main_depth_idx, x1=max_sal, y1=main_depth_idx,
                    line=dict(
                        color="red",
                        width=1
                    )
                )

                fig_temp_prof.add_shape(
                    type="line",
                    x0=min_temp, y0=main_depth_idx, x1=max_temp, y1=main_depth_idx,
                    line=dict(
                        color="red",
                        width=1
                    )
                )

            fig_sal_prof.update_layout(
                title=f"Salinity Profiles {cur_date_str}",
                xaxis=dict(title="Salinity (PSU)"),
                yaxis=dict(title="Depth (m)", autorange="reversed"),
                dragmode="pan",
                height=self.styles.fig_height,  
                margin=self.styles.margins,  
            )
        
        return [fig_temp_prof, fig_sal_prof]


