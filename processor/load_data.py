import xarray as xr
import pandas as pd
import numpy as np

import config

recorded = xr.open_dataset(config.RECORD_PATH)
recorded_stat = pd.read_csv(config.RECORD_STAT_PATH)
predicted = {
    ssp: xr.open_dataset(path) for ssp, path in config.PREDICT_PATH_MAP.items()
}
predicted_stat = {
    ssp: pd.read_csv(path) for ssp, path in config.PREDICT_STAT_PATH_MAP.items()
}

cached_stat = {
    ssp: pd.read_csv(path) for ssp, path in config.ANNUAL_STAT_PATH_MAP.items()
}

def compute_annual_average(monthly_data):
    num_complete_years = len(monthly_data) // 12
    valid_length = num_complete_years * 12
    reshaped_data = np.reshape(monthly_data[:valid_length], (num_complete_years, 12))
    annual_average = np.mean(reshaped_data, axis=1)
    return annual_average

def compute_annual_max(monthly_data):
    num_complete_years = len(monthly_data) // 12
    valid_length = num_complete_years * 12
    reshaped_data = np.reshape(monthly_data[:valid_length], (num_complete_years, 12))
    annual_average = np.max(reshaped_data, axis=1)
    return annual_average

def compute_annual_min(monthly_data):
    num_complete_years = len(monthly_data) // 12
    valid_length = num_complete_years * 12
    reshaped_data = np.reshape(monthly_data[:valid_length], (num_complete_years, 12))
    annual_average = np.min(reshaped_data, axis=1)
    return annual_average


def get_coord_data(lat_idx, lon_idx, season, ssp):
    from_recorded = (
        recorded["temperature"][0:1980].isel(latitude=lat_idx, longitude=lon_idx).values
    )
    from_predicted = (
        predicted[ssp]["temperature"].isel(latitude=lat_idx, longitude=lon_idx).values
    )
    combined_temperature_list = np.concatenate((from_recorded, from_predicted))

    if season:
        result = combined_temperature_list[config.SEASONS[season] :: 12]
    else:
        result = compute_annual_average(combined_temperature_list)

    return result


# def get_continent_data(continent, season, ssp):
#     recorded_avg = recorded_stat[f"{continent}_avg"].tolist()[0:1980]
#     predicted_avg = predicted_stat[ssp][f"{continent}_avg"].tolist()
#     combined_avg = np.concatenate((recorded_avg, predicted_avg))
    
#     recorded_max = recorded_stat[f"{continent}_max"].tolist()[0:1980]
#     predicted_max = predicted_stat[ssp][f"{continent}_max"].tolist()
#     combined_max = np.concatenate((recorded_max, predicted_max))
    
#     recorded_min = recorded_stat[f"{continent}_min"].tolist()[0:1980]
#     predicted_min = predicted_stat[ssp][f"{continent}_min"].tolist()
#     combined_min = np.concatenate((recorded_min, predicted_min))

#     if season:
#         combined_avg = combined_avg[config.SEASONS[season] :: 12]
#         combined_max = combined_max[config.SEASONS[season] :: 12]
#         combined_min = combined_min[config.SEASONS[season] :: 12]
#     else:
#         result = compute_annual_average(combined_avg)
        
#     result = {
#         "avg": combined_avg,
#         "max": combined_max,
#         "min": combined_min,
#     }

#     return result

def get_continent_data(continent, season, ssp):
    if season is None:
        season = "Yearly"
        
    season = season.lower()
    
    annual_avg = cached_stat[ssp][f"{continent}_avg_{season}"].tolist()
    annual_max = cached_stat[ssp][f"{continent}_max_{season}"].tolist()
    annual_min = cached_stat[ssp][f"{continent}_min_{season}"].tolist()
    
    result = {
        "avg": annual_avg,
        "max": annual_max,
        "min": annual_min,
    }
    
    return result


def get_data(continent, latitude, longitude, season, ssp):
    if continent:
        result = get_continent_data(continent, season, ssp)
    else:
        lat_idx = (latitude + 90) % 180
        lon_idx = (longitude + 180) % 360
        result = get_coord_data(lat_idx, lon_idx, season, ssp)

    return result
