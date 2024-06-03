import xarray as xr
import geopandas as gpd
import regionmask
import pandas as pd
import numpy as np

import config

recorded = xr.open_dataset(config.RECORD_PATH, decode_times=False)
predicted = {
    ssp: xr.open_dataset(path, decode_times=False) for ssp, path in config.PREDICT_PATH_MAP.items()
}

# Load world shapefile using deprecated method (for now)
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# Dissolve the world data by 'continent' to get continent polygons
continents = world.dissolve(by="continent")

# Add a numeric ID for each continent
continents["continent_id"] = range(len(continents))


def _calculate_continental_statistics_monthly(ds, continent):
    if continent == "World":
        masked_data = ds["temperature"]
    else:
        # Create masks for continents over your dataset grid (using original coordinates)
        if continent == "Antarctica":
            # Create an empty mask with the same shape as your dataset
            continent_mask = xr.DataArray(np.nan, coords=[ds.latitude, ds.longitude], dims=["latitude", "longitude"])

            # Set the mask values to 1 (or any non-NaN value) for Antarctica's latitude indices from 0 to 25
            continent_mask.loc[dict(latitude=ds.latitude[0:26])] = 1
        else:
            mask = regionmask.mask_geopandas(continents, ds.longitude, ds.latitude, numbers="continent_id")

            # Extract the mask for the given continent (assuming the continent name is valid and in 'continents')
            continent_id = continents.index.get_loc(continent)
            continent_mask = mask.where(mask == continent_id)

        # Apply the Asia mask to the temperature data
        masked_data = ds["temperature"].where(continent_mask.notnull())

    # Calculate the mean temperature over the masked region, along the spatial dimensions (latitude and longitude)
    temperature_mean = masked_data.mean(dim=["latitude", "longitude"], skipna=True)
    temperature_max = masked_data.max(dim=["latitude", "longitude"], skipna=True)
    temperature_min = masked_data.min(dim=["latitude", "longitude"], skipna=True)

    continental_df = pd.DataFrame(
        {
            "temperature_avg": temperature_mean,
            "temperature_max": temperature_max,
            "temperature_min": temperature_min,
        }
    )

    return continental_df


def _save_continental_statistics_monthly():
    # save recorded average data
    recorded_df = pd.DataFrame()

    for continent in config.CONTINENTS:
        result = _calculate_continental_statistics_monthly(recorded, continent)
        recorded_df[f"{continent}_Avg"] = result["temperature_avg"]
        recorded_df[f"{continent}_Max"] = result["temperature_max"]
        recorded_df[f"{continent}_Min"] = result["temperature_min"]

    recorded_df.to_csv(config.RECORD_STAT_PATH, index=False)

    # save predicted average data
    for ssp, ds in predicted.items():
        predicted_df = pd.DataFrame()

        for continent in config.CONTINENTS:
            result = _calculate_continental_statistics_monthly(ds, continent)
            predicted_df[f"{continent}_Avg"] = result["temperature_avg"]
            predicted_df[f"{continent}_Max"] = result["temperature_max"]
            predicted_df[f"{continent}_Min"] = result["temperature_min"]

        predicted_df.to_csv(config.PREDICT_STAT_PATH_MAP[ssp], index=False)


def _save_continental_statistics_yearly():
    recorded_stat = pd.read_csv(config.RECORD_STAT_PATH)
    predicted_stat = {
        ssp: pd.read_csv(path) for ssp, path in config.PREDICT_STAT_PATH_MAP.items()
    }
    
    for ssp in config.SSP_SCENARIOS:
        combined_stat = pd.concat([recorded_stat, predicted_stat[ssp]])
        processed_data = pd.DataFrame()
        
        for start in range(0, len(combined_stat), 12):
            end = start + 12
            if end > len(combined_stat):
                break
            
            year_data = combined_stat.iloc[start:end]
            year_dict = {}
            
            for column in combined_stat.columns:
                if '_Avg' in column:
                    # Calculate yearly and seasonal averages
                    year_dict[column + '_Yearly'] = year_data[column].mean()
                    for season, months in config.SEASONS.items():
                        year_dict[column + '_' + season] = year_data.iloc[months][column].mean()
                elif '_Max' in column:
                    # Calculate yearly and seasonal maximums
                    year_dict[column + '_Yearly'] = year_data[column].max()
                    for season, months in config.SEASONS.items():
                        year_dict[column + '_' + season] = year_data.iloc[months][column].max()
                elif '_Min' in column:
                    # Calculate yearly and seasonal minimums
                    year_dict[column + '_Yearly'] = year_data[column].min()
                    for season, months in config.SEASONS.items():
                        year_dict[column + '_' + season] = year_data.iloc[months][column].min()
        
            processed_data = pd.concat([processed_data, pd.DataFrame([year_dict])], ignore_index=True)
        
        processed_data.to_csv(config.ANNUAL_STAT_PATH_MAP[ssp], index=False)

def preprocess_data():
    _save_continental_statistics_monthly()
    _save_continental_statistics_yearly()
    
if __name__ == '__main__':
    preprocess_data()