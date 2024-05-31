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


def _get_coord_data(lat_idx, lon_idx, season, ssp):
    from_recorded = recorded["temperature"][0:1980].isel(latitude=lat_idx, longitude=lon_idx).values
    from_predicted = predicted[ssp]["temperature"].isel(latitude=lat_idx, longitude=lon_idx).values
    
    combined_temperature_list = np.concatenate((from_recorded, from_predicted))
    
    if season:
        season_indices = config.SEASONS[season]
        seasonal_temperatures = [combined_temperature_list[i] for i in range(len(combined_temperature_list)) if i % 12 in season_indices]
        data = [np.nanmean(seasonal_temperatures[i * 3:(i + 1) * 3]) for i in range((len(seasonal_temperatures) + 2) // 3 )] 
    else:
        data = [np.nanmean(combined_temperature_list[i * 12:(i + 1) * 12]) for i in range((len(combined_temperature_list) + 11) // 12 )] 

    data = [None if np.isnan(x) else float(x) for x in data]

    result = {
        "avg": data,
    }

    return result

def _get_continent_data(continent, season, ssp):
    if season is None:
        season = "Yearly"
    
    annual_avg = cached_stat[ssp][f"{continent}_Avg_{season}"].tolist()
    annual_max = cached_stat[ssp][f"{continent}_Max_{season}"].tolist()
    annual_min = cached_stat[ssp][f"{continent}_Min_{season}"].tolist()
    
    result = {
        "avg": annual_avg,
        "max": annual_max,
        "min": annual_min,
    }
    
    return result


def get_data(continent, latitude, longitude, season, ssp):
    if continent:
        result = _get_continent_data(continent, season, ssp)
    else:
        lat_idx = (latitude + 90) % 180
        lon_idx = (longitude + 180) % 360
        result = _get_coord_data(lat_idx, lon_idx, season, ssp)

    return result
