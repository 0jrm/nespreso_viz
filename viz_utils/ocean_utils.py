import gsw
import numpy as np

def get_density(S, T, p):
    """
    Calculate the density of seawater using the Gibbs-SeaWater (GSW) toolbox.
    
    Arguments:
    S -- Absolute Salinity, g/kg
    T -- Conservative Temperature (ITS-90), degrees C
    p -- Sea pressure (absolute pressure minus 10.1325 dbar), dbar
    
    Returns:
    rho -- in-situ density kg/m
    """
    
    return gsw.density.rho(S, T, p)

def get_mld(salinity, temperature, pressure, temp_threshold=0.2, density_threshold=0.125):
    """
    Calculate the mixed layer depth (MLD) using two criteria: temperature and density.
    
    Arguments:
    salinity -- Absolute Salinity, g/kg (4D array: time, lat, lon, depth)
    temperature -- Conservative Temperature (ITS-90), degrees C (4D array: time, lat, lon, depth)
    pressure -- Sea pressure (absolute pressure minus 10.1325 dbar), dbar (4D array: time, lat, lon, depth)
    temp_threshold -- Temperature threshold for the temperature criterion, degrees C
    density_threshold -- Density threshold for the density criterion, kg/m^3
    
    Returns:
    mld_temp_criteria -- MLD calculated using the temperature criterion, dbar (3D array: time, lat, lon)
    mld_density_criteria -- MLD calculated using the density criterion, dbar (3D array: time, lat, lon)
    """
    
import numpy as np

def get_density(temperature, salinity, pressure):
    # Placeholder function for calculating density.
    # Replace with the actual function for calculating density.
    return 1027 + 0.2 * (temperature - 15) + 0.8 * (salinity - 35) + 0.05 * pressure

def get_mld(salinity, temperature, pressure, temp_threshold=0.2, density_threshold=0.125):
    """
    Calculate the mixed layer depth (MLD) using two criteria: temperature and density.
    
    Arguments:
    salinity -- Absolute Salinity, g/kg (4D array: time, lat, lon, depth)
    temperature -- Conservative Temperature (ITS-90), degrees C (4D array: time, lat, lon, depth)
    pressure -- Sea pressure (absolute pressure minus 10.1325 dbar), dbar (4D array: time, lat, lon, depth)
    temp_threshold -- Temperature threshold for the temperature criterion, degrees C
    density_threshold -- Density threshold for the density criterion, kg/m^3
    
    Returns:
    mld_temp_criteria -- MLD calculated using the temperature criterion, dbar (3D array: time, lat, lon)
    mld_density_criteria -- MLD calculated using the density criterion, dbar (3D array: time, lat, lon)
    """
    
    density = get_density(temperature, salinity, pressure)
    surface_temperature = temperature[:, :, :, 0]
    surface_density = density[:, :, :, 0]

    temp_diff = np.abs(temperature - surface_temperature)
    mask_temp = temp_diff <= temp_threshold
    last_index_temp = mask_temp[..., ::-1].argmax(axis=-1)  # Find last True index from bottom
    mld_temp_criteria = pressure.shape[-1] - 1 - last_index_temp
    
    density_diff = np.abs(density - surface_density)
    mask_density = density_diff <= density_threshold
    last_index_density = mask_density[..., ::-1].argmax(axis=-1)  # Find last True index from bottom
    mld_density_criteria = pressure.shape[-1] - 1 - last_index_density

    # Initialize the result arrays with NaNs
    mld_temp_result = np.full(surface_temperature.shape, np.nan)
    mld_density_result = np.full(surface_density.shape, np.nan)

    # Create boolean masks for valid indices
    valid_temp_mask = last_index_temp != -1
    valid_density_mask = last_index_density != -1

    # Flatten the arrays
    valid_temp_mask_flat = valid_temp_mask.values.flatten()
    valid_density_mask_flat = valid_density_mask.values.flatten()

# Initialize result arrays with NaNs
    mld_temp_result = np.full(surface_temperature.shape, np.nan)
    mld_density_result = np.full(surface_density.shape, np.nan)

    # Create a meshgrid for indexing
    time_indices, lat_indices, lon_indices = np.meshgrid(
        np.arange(temperature.shape[0]),
        np.arange(temperature.shape[1]),
        np.arange(temperature.shape[2]),
        indexing='ij'
    )
    # Flatten the indices for advanced indexing
    time_indices_flat = time_indices.flatten()
    lat_indices_flat = lat_indices.flatten()
    lon_indices_flat = lon_indices.flatten()
    mld_temp_criteria_flat = mld_temp_criteria.values.flatten()
    mld_density_criteria_flat = mld_density_criteria.values.flatten()

    # Initialize result arrays with NaNs
    mld_temp_result = np.full(surface_temperature.shape, np.nan)
    mld_density_result = np.full(surface_density.shape, np.nan)

    # Use advanced indexing to assign values to result arrays
    mld_temp_result_flat = mld_temp_result.flatten()
    mld_density_result_flat = mld_density_result.flatten()

    # Assign the values using flattened indices and boolean masks
    mld_temp_result_flat[valid_temp_mask_flat] = pressure[
        time_indices_flat[valid_temp_mask_flat], 
        lat_indices_flat[valid_temp_mask_flat], 
        lon_indices_flat[valid_temp_mask_flat], 
        mld_temp_criteria_flat[valid_temp_mask_flat]
    ]

    mld_density_result_flat[valid_density_mask_flat] = pressure[
        time_indices_flat[valid_density_mask_flat], 
        lat_indices_flat[valid_density_mask_flat], 
        lon_indices_flat[valid_density_mask_flat], 
        mld_density_criteria_flat[valid_density_mask_flat]
    ]

    # Reshape the result arrays back to the original shape
    mld_temp_result = mld_temp_result_flat.reshape(surface_temperature.shape)
    mld_density_result = mld_density_result_flat.reshape(surface_density.shape)
    return mld_temp_result, mld_density_result

def get_ohc(salinity, temperature, pressure, temp_limit=26):
    """
    Calculate the ocean heat content (OHC) above a given temperature limit.
    
    Arguments:
    salinity -- Absolute Salinity, g/kg
    temperature -- Conservative Temperature (ITS-90), degrees C
    pressure -- Sea pressure (absolute pressure minus 10.1325 dbar), dbar
    temp_limit -- Temperature limit, degrees C
    
    Returns:
    ohc -- Ocean heat content above the temperature limit, J/m^2
    """
    
    specific_heat_capacity = 3992  # J/(kg*K) for seawater
    density = get_density(temperature, salinity, pressure)
    mask = temperature >= temp_limit

    ohc = np.zeros(temperature.shape[1])  # Initialize OHC array for each profile

    for i in range(temperature.shape[1]):
        temp_above_limit = temperature[:, i][mask[:, i]]
        pressure_above_limit = pressure[:, i][mask[:, i]]
        density_above_limit = density[:, i][mask[:, i]]

        if len(temp_above_limit) > 0:
            ohc[i] = np.trapz((temp_above_limit - temp_limit) * specific_heat_capacity * density_above_limit, pressure_above_limit)

    return ohc

def get_isotherm_pressure(temperature, pressure, isotherm_temp=26):
    """
    Calculate the pressure at which the temperature exceeds a given isotherm temperature.
    
    Arguments:
    temperature -- Conservative Temperature (ITS-90), degrees C
    pressure -- Sea pressure (absolute pressure minus 10.1325 dbar), dbar
    isotherm_temp -- Isotherm temperature, degrees C
    
    Returns:
    isotherm_pressure -- Pressure at which the temperature exceeds the isotherm temperature, dbar
    """
    
    # Find the indices where temperature exceeds the isotherm temperature
    mask = temperature >= isotherm_temp
    # Initialize an array to hold the isotherm pressure for each profile
    isotherm_pressure = np.full(temperature.shape[1], np.nan)

    # Iterate over each profile
    for i in range(temperature.shape[1]):
        # Get the indices in the current profile where the temperature is above the isotherm temperature
        idx = np.where(mask[:, i])[0]
        if len(idx) > 0:
            # Get the last index where the condition is met
            isotherm_pressure[i] = pressure[idx[-1], i]

    return isotherm_pressure

def calculate_ocean_pressure(temperatures, salinities, depths, atmospheric_pressure=101325):
    """
    Calculate the pressure at various depths in the ocean given temperature and salinity arrays.
    
    Parameters:
    temperatures (array): Array of temperatures in degrees Celsius.
    salinities (array): Array of salinities in Practical Salinity Units (PSU).
    depths (array): Array of depths in meters.
    atmospheric_pressure (float): Atmospheric pressure at sea level in Pa (default is 101325 Pa).
    
    Returns:
    array: Array of pressures at the given depths in Pascals.
    """
    # Convert depths from meters to decibars (1 dbar = 1 meter approximately)
    pressures_dbar = gsw.p_from_z(-np.array(depths), np.zeros_like(depths))
    
    # Calculate in-situ density using the TEOS-10 equation of state
    densities = gsw.rho(salinities, temperatures, pressures_dbar)
    
    # Calculate hydrostatic pressure at each depth
    hydrostatic_pressures = densities * 9.81 * np.array(depths)
    
    # Total pressure is the sum of atmospheric pressure and hydrostatic pressure
    total_pressures = atmospheric_pressure + hydrostatic_pressures
    
    return total_pressures

# Example usage
# temperatures = np.array([10, 12, 14, 16, 18])  # temperatures in degrees Celsius
# salinities = np.array([35, 35, 35, 35, 35])  # salinities in PSU
# depths = np.array([0, 10, 50, 100, 200])  # depths in meters

# pressures = calculate_ocean_pressure(temperatures, salinities, depths)
# pressures_in_atm = pressures / 101325  # converting pressures to atmospheres

# for depth, pressure, pressure_atm in zip(depths, pressures, pressures_in_atm):
#     print(f"Pressure at {depth} meters: {pressure:.2f} Pascals ({pressure_atm:.2f} atm)")
