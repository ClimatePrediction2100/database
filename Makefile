.PHONY: setup download preprocess

preprocess: download
	@echo "Preprocessing data..."
	@python3 processor/preprocess_data.py
	@echo "Preprocessing complete."

download: setup
	@echo "Downloading data..."
	@wget -O data/recorded/Land_and_Ocean_LatLong1.nc https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Global/Gridded/Land_and_Ocean_LatLong1.nc
	@wget -O data/netcdf.tar.gz https://github.com/ClimatePrediction2100/data/releases/download/netCDF4/results_by_ssp.tar.gz
	@tar -zxvf data/netcdf.tar.gz -C data/predicted
	@echo "Data download complete."

setup: 
	@echo "Setting up the environment..."
	@pip install -r requirements.txt
	@mkdir -p data/cached/csv
	@mkdir -p data/predicted/csv
	@mkdir -p data/recorded
	@echo "Environment setup complete."


