import xarray as xr
import geopandas as gpd
import regionmask
import pandas as pd
import numpy as np

import config

recorded = xr.open_dataset(config.RECORD_PATH)
# recorded_avg = pd.read_csv(config.RECORD_AVG_PATH)
predicted = {ssp: xr.open_dataset(path) for ssp, path in config.PREDICT_PATH_MAP.items()}
# predicted_avg = {ssp: pd.read_csv(path) for ssp, path in config.PREDICT_AVG_PATH_MAP.items()}

# Load world shapefile using deprecated method (for now)
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Dissolve the world data by 'continent' to get continent polygons
continents = world.dissolve(by='continent')

# Add a numeric ID for each continent
continents['continent_id'] = range(len(continents))

def convert_data(ds, continent):
    if continent == 'World':
        masked_data = ds['temperature']
    else:
        # Create masks for continents over your dataset grid (using original coordinates)
        if continent == 'Antartica':
            # Create an empty mask with the same shape as your dataset
            continent_mask = xr.DataArray(np.nan, coords=[ds.latitude, ds.longitude], dims=['latitude', 'longitude'])
            
            # Set the mask values to 1 (or any non-NaN value) for Antarctica's latitude indices from 0 to 25
            continent_mask.loc[dict(latitude=ds.latitude[0:26])] = 1
        else:
            mask = regionmask.mask_geopandas(continents, ds.longitude, ds.latitude, numbers='continent_id')
            
            # Extract the mask for the given continent (assuming the continent name is valid and in 'continents')
            continent_id = continents.index.get_loc(continent)
            continent_mask = mask.where(mask == continent_id)

        # Apply the Asia mask to the temperature data
        masked_data = ds['temperature'].where(continent_mask.notnull())

    # Calculate the mean temperature over the masked region, along the spatial dimensions (latitude and longitude)
    mean_temperature = masked_data.mean(dim=['latitude', 'longitude'], skipna=True)

    # Convert the mean temperature data to a DataFrame
    mean_temperature_df = mean_temperature.to_dataframe().reset_index()

    return mean_temperature_df


# convert_data()

def save_average_data():
    # save recorded average data
    recorded_df = pd.DataFrame()
    
    for continent in config.CONTINENTS:
        result = convert_data(recorded, continent)
        recorded_df[continent] = result['temperature']
        
    recorded_df.to_csv(config.RECORD_AVG_PATH, index=False)
    
    # save predicted average data
    for ssp, ds in predicted.items():
        predicted_df = pd.DataFrame()
        
        for continent in config.CONTINENTS:
            result = convert_data(ds, continent)
            predicted_df[continent] = result['temperature']
            
        predicted_df.to_csv(config.PREDICT_AVG_PATH_MAP[ssp], index=False)
