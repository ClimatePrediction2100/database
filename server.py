import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'processor'))
import gc
import logging
from flask import Flask, request, jsonify
import processor.handle_data as datahandler
from multiprocessing import Pool, Manager, current_process
import signal

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

manager = Manager()
shared_data = manager.dict()
pool = None

def initialize_shared_data():
    shared_data['data'] = datahandler.load_all_data()

def initialize_pool():
    global pool
    gc.collect()
    if pool is None:
        pool = Pool(processes=os.cpu_count())
        logger.info("Initialized multiprocessing pool with %d processes", os.cpu_count())

def process_data(continent, latitude, longitude, season, ssp):
    process_id = current_process().pid
    logger.info("Process %d is handling the task", process_id)

    processed_data = datahandler.get_data(shared_data['data'], continent, latitude, longitude, season, ssp)
    return processed_data

@app.route('/data', methods=['GET'])
def get_data():
    continent = request.args.get('continent', None)
    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)
    season = request.args.get('season', default=None)
    ssp = request.args.get('ssp')

    if latitude and longitude:
        latitude = int(latitude)
        longitude = int(longitude)

    if pool is None:
        initialize_pool()

    result = pool.apply_async(process_data, (continent, latitude, longitude, season, ssp))
    data = result.get()

    return jsonify(data)

def shutdown_pool(signum, frame):
    global pool
    logger.info("Received signal %d: shutting down pool", signum)
    if pool is not None:
        pool.close()
        pool.join()
    os._exit(0)

if __name__ == '__main__':
    initialize_shared_data()
    initialize_pool()

    signal.signal(signal.SIGINT, shutdown_pool)
    signal.signal(signal.SIGTERM, shutdown_pool)

    app.run(debug=False, port=8001)
