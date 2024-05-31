from flask import Flask, request, jsonify
import processor.load_data as dataloader
import processor.convert_data as dataconverter

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_data():
    continent = request.args.get('continent', None)

    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)

    if not continent:
        latitude = int(latitude)
        longitude = int(longitude)

    season = request.args.get('season', default=None)
    ssp = request.args.get('ssp')

    data = dataloader.get_data(continent, latitude, longitude, season, ssp)

    return jsonify(data.tolist())

is_data_converted = False

@app.route('/data/convert', methods=['GET'])
def convert_data():
    if not is_data_converted:
        dataconverter.save_average_data()
        is_data_converted = True
    return True


if __name__ == '__main__':
    app.run(debug=True, port=8001)
