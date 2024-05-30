import xarray as xr
import pandas as pd
import numpy as np

import config

recorded = xr.open_dataset(config.RECORD_PATH)
recorded_avg = pd.read_csv(config.RECORD_AVG_PATH)
predicted = {ssp: xr.open_dataset(path) for ssp, path in config.PREDICT_PATH_MAP.items()}
predicted_avg = {ssp: pd.read_csv(path) for ssp, path in config.PREDICT_AVG_PATH_MAP.items()}


def getCoordData(lat_idx, lon_idx, season, ssp):
    from_recorded = recorded['temperature'][0:1980].isel(latitude=lat_idx, longitude=lon_idx).values
    from_predicted = predicted[ssp]['temperature'].isel(latitude=lat_idx, longitude=lon_idx).values
    combined_temperature_list = from_recorded + from_predicted
    
    if season:
        result = combined_temperature_list[config.SEASONS[season]::12]
    else:
        result = combined_temperature_list
    
    return result

def getContinentData(continent, season, ssp):
    from_recorded = recorded_avg[continent].tolist()[0:1980]
    from_predicted = predicted_avg[ssp][continent].tolist()
    combined_temperature_list = from_recorded + from_predicted
    
    if season:
        result = combined_temperature_list[config.SEASONS[season]::12]
    else:
        result = combined_temperature_list
    
    return result