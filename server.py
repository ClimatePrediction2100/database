from flask import Flask, request, jsonify
import processor.load_data as dataloader

app = Flask(__name__)

@app.route('/coord', methods=['GET'])
def get_coord_data():
    latitude = int(request.args.get('latitude'))
    longitude = int(request.args.get('longitude'))

    lat_idx = (latitude + 90) % 180
    lon_idx = (longitude + 180) % 360
    
    season = request.args.get('season', default=None)
    ssp = request.args.get('ssp')
    
    result = dataloader.get_coord_data(lat_idx, lon_idx, season, ssp)
    return jsonify(result.tolist())

@app.route('/continent', methods=['GET'])
def get_continent_data():
    continent = request.args.get('continent')
    season = request.args.get('season', default=None)
    ssp = request.args.get('ssp')
    
    result = dataloader.get_continent_data(continent, season, ssp)
    return jsonify(result.tolist())

if __name__ == '__main__':
    app.run(debug=True, port=8000)
