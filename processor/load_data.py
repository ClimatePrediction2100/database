import xarray as xr
import pandas as pd
import numpy as np

import config

recorded = xr.open_dataset(config.RECORD_PATH)
recorded_avg = pd.read_csv(config.RECORD_AVG_PATH)
predicted = {ssp: xr.open_dataset(path) for ssp, path in config.PREDICT_PATH_MAP.items()}
predicted_avg = {ssp: pd.read_csv(path) for ssp, path in config.PREDICT_AVG_PATH_MAP.items()}


def compute_annual_average(monthly_data):
    num_complete_years = len(monthly_data) // 12
    valid_length = num_complete_years * 12
    reshaped_data = np.reshape(monthly_data[:valid_length], (num_complete_years, 12))
    annual_average = np.mean(reshaped_data, axis=1)
    return annual_average

def get_coord_data(lat_idx, lon_idx, season, ssp):
    from_recorded = recorded['temperature'][0:1980].isel(latitude=lat_idx, longitude=lon_idx).values
    from_predicted = predicted[ssp]['temperature'].isel(latitude=lat_idx, longitude=lon_idx).values
    combined_temperature_list = np.concatenate((from_recorded, from_predicted))
    
    if season:
        result = combined_temperature_list[config.SEASONS[season]::12]
    else:
        result = compute_annual_average(combined_temperature_list)
    
    return result

def get_continent_data(continent, season, ssp):
    from_recorded = recorded_avg[continent].tolist()[0:1980]
    from_predicted = predicted_avg[ssp][continent].tolist()
    combined_temperature_list = np.concatenate((from_recorded, from_predicted))
    
    if season:
        result = combined_temperature_list[config.SEASONS[season]::12]
    else:
        result = compute_annual_average(combined_temperature_list)
    
    return result

def get_data(continent, latitude, longitude, season, ssp):
    if continent:
        result = get_continent_data(continent, season, ssp)
    else:
        lat_idx = (latitude + 90) % 180
        lon_idx = (longitude + 180) % 360
        result = get_coord_data(lat_idx, lon_idx, season, ssp)

    return result