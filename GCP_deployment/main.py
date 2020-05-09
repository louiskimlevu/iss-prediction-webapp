#!/usr/bin/env python
from flask import Flask, render_template, flash, request, jsonify, Markup
import sys
import matplotlib
import matplotlib.pyplot as plt
import io, os, base64
import numpy as np
import requests

# get path directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# instantiate the Flask server
app = Flask(__name__)

# get the location of ISS
def get_space_station_location():

    space_station_longitude = None
    space_station_latitude = None
    try:
        r = requests.get(url='http://api.open-notify.org/iss-now.json')
        space_station_location = (r.json())

        space_station_longitude = float(space_station_location['iss_position']['longitude'])
        space_station_latitude = float(space_station_location['iss_position']['latitude'])

    except:
        # log error
        print('Request not working')
    return (space_station_longitude, space_station_latitude)


def translate_geo_to_pixels(longitude, latitude, max_x_px, max_y_px):
    # y = -90 to 90
    # x = -180 to 180
    scale_x = abs(((longitude + 180) / 360) * max_x_px)
    scale_y = abs(((latitude - 90) / 180) * max_y_px) # substract as y scale is flipped

    return scale_x, scale_y

@app.route("/", methods=['POST', 'GET'])
def ISS_Tracker():

    # set an initial plot size
    plt.figure(figsize=(16, 8))
    # load the image from web server
    img = os.path.join(BASE_DIR, 'world-map-backround.png')
    img = plt.imread(img)
    img = plt.imshow(img)

    if request.method == 'POST':
        # get the location of the ISS
        iss_location = get_space_station_location()
        # translate the geo-coordinates to pixels
        translated_iss_location = translate_geo_to_pixels(
            iss_location[0],
            iss_location[1],
            2000, 1000)

        # add position to plot
        plt.scatter(x=[translated_iss_location[0]], y=[translated_iss_location[1]],
                    c='blue', s=500, marker="P")

    plt.axis('off')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('iss-page.html',
        forecast_plot = Markup('<img src="data:image/png;base64,{}" style="width:100%;vertical-align:top">'.format(plot_url))
        )

if __name__=='__main__':
    app.run(debug=True)