import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


SSP_SCENARIOS = ["119", "126", "245", "370", "434", "460", "534", "585"]

DATA_PATH = "data"

RECORD_PATH = os.path.join(DATA_PATH, "recorded", "Land_and_Ocean_LatLong1.nc")
RECORD_AVG_PATH = os.path.join(DATA_PATH, "recorded", "Land_and_Ocean_LatLong1_Average.csv")

PREDICT_PATH_MAP = {
    ssp: os.path.join(DATA_PATH, "predicted", "netCDF", f"SSP{ssp}_predictions.nc")
    for ssp in SSP_SCENARIOS
}

PREDICT_AVG_PATH_MAP = {
    ssp: os.path.join(DATA_PATH, "predicted", "csv", f"SSP{ssp}_predictions_average.csv")
    for ssp in SSP_SCENARIOS
}

CONTINENTS = {
    "World": None,  # mean method 대체 가능
    "Asia": [(0, 0), (0, 1), (1, 0), (0, 2), (2, 0), (10, 10)],
    "Europe": [(90, 180)],
    "Africa": [(90, 180)],
    "North America": [(140, 359)],
    "South America": [(140, 359)],
    "Oceania": [(140, 359)],
    "Antartica": [(140, 359)],
}

SEASONS = {
    "Winter": 0,
    "Spring": 3,
    "Summer": 6,
    "Fall": 9,
    "Autumn": 9,
}