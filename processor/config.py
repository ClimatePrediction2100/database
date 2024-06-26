import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


SSP_SCENARIOS = ("119", "126", "245", "370", "434", "460", "534", "585")

DATA_PATH = "data"

RECORD_PATH = os.path.join(DATA_PATH, "recorded", "Land_and_Ocean_LatLong1.nc")
RECORD_STAT_PATH = os.path.join(
    DATA_PATH, "recorded", "Land_and_Ocean_LatLong1_statistics.csv"
)

PREDICT_PATH_MAP = {
    ssp: os.path.join(DATA_PATH, "predicted", "netCDF", f"SSP{ssp}_predictions.nc")
    for ssp in SSP_SCENARIOS
}

PREDICT_STAT_PATH_MAP = {
    ssp: os.path.join(
        DATA_PATH, "predicted", "csv", f"SSP{ssp}_predictions_statistics.csv"
    )
    for ssp in SSP_SCENARIOS
}

ANNUAL_STAT_PATH_MAP = {
    ssp: os.path.join(
        DATA_PATH, "cached", "csv", f"SSP{ssp}_predictions_annual_statistics.csv"
    )
    for ssp in SSP_SCENARIOS
}

CONTINENTS = (
    "World",
    "Asia",
    "Europe",
    "Africa",
    "North America",
    "South America",
    "Oceania",
    "Antarctica",
)

SEASONS = {
    'Winter': [0, 1, 11],  # January, February, December
    'Spring': [2, 3, 4],   # March, April, May
    'Summer': [5, 6, 7],   # June, July, August
    'Fall': [8, 9, 10],    # September, October, November
}
