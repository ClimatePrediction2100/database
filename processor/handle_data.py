import xarray as xr
import pandas as pd
import numpy as np
from dataclasses import dataclass
import config

@dataclass
class TemperatureData:
    recorded: xr.Dataset
    predicted: dict[str, xr.Dataset]
    recorded_stat: pd.DataFrame
    predicted_stat: dict[str, pd.DataFrame]
    cached_stat: dict[str, pd.DataFrame]

def load_all_data():
    return TemperatureData(
        recorded=xr.open_dataset(config.RECORD_PATH, decode_times=False, cache=False),

        predicted={ 
            ssp: xr.open_dataset(path, decode_times=False, cache=False) for ssp, path in config.PREDICT_PATH_MAP.items()
        },

        recorded_stat=pd.read_csv(config.RECORD_STAT_PATH).replace({np.nan: None}),

        predicted_stat={ 
            ssp: pd.read_csv(path).replace({np.nan: None}) for ssp, path in config.PREDICT_STAT_PATH_MAP.items() 
        },

        cached_stat={
            ssp: pd.read_csv(path).replace({np.nan: None}) for ssp, path in config.ANNUAL_STAT_PATH_MAP.items()
        }
    )

def _get_coord_data(temp_data, lat_idx, lon_idx, season, ssp):
    from_recorded = temp_data.recorded["temperature"][0:1980].isel(latitude=lat_idx, longitude=lon_idx).values
    from_predicted = temp_data.predicted[ssp]["temperature"].isel(latitude=lat_idx, longitude=lon_idx).values
    
    combined_temperature_list = np.concatenate((from_recorded, from_predicted))
    
    if season == "Yearly":
        data = np.nanmean(combined_temperature_list.reshape(-1, 12), axis=1)
    else:
        season_indices = config.SEASONS[season]
        seasonal_temperatures = combined_temperature_list[np.isin(np.arange(len(combined_temperature_list)) % 12, season_indices)]
        data = np.nanmean(seasonal_temperatures.reshape(-1, 3), axis=1)
    
    data = np.where(np.isnan(data), None, data).tolist()

    result = {
        "avg": data,
    }

    return result

def _get_continent_data(temp_data, continent, season, ssp):
    annual_avg = temp_data.cached_stat[ssp][f"{continent}_Avg_{season}"].tolist()
    annual_max = temp_data.cached_stat[ssp][f"{continent}_Max_{season}"].tolist()
    annual_min = temp_data.cached_stat[ssp][f"{continent}_Min_{season}"].tolist()
    
    result = {
        "avg": annual_avg,
        "max": annual_max,
        "min": annual_min,
    }
    
    return result


def get_data(temp_data, continent, latitude, longitude, season, ssp):
    if continent:
        result = _get_continent_data(temp_data, continent, season, ssp)
    else:
        lat_idx = (latitude + 90) % 180
        lon_idx = (longitude + 180) % 360
        result = _get_coord_data(temp_data, lat_idx, lon_idx, season, ssp)

    return result
