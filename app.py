#!/usr/bin/env python

from flask import Flask
import json
from flask import jsonify
from flask import make_response
from flask import render_template
from flask.ext.restful import Api

app = Flask(__name__)
api = Api(app)

# VIEWS

@app.route('/')
def index():
    return render_template('base.html')

from models import Temperature
from utils import get_n_hex_colors

@app.route('/rickshaw')
def rs():
    # skip index
    columns = Temperature.__table__.columns.keys()[1:]
    colors = get_n_hex_colors(len(columns))
    series = [{'name': k, 'color': v} for k, v in zip(columns, colors)]
    return render_template('rs.html', series=series)

# Generate chart

from io import BytesIO
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from models import compile_query
from db import session
from sqlalchemy import create_engine
from settings import DB_URI

@app.route('/pic.png')
def pic2():
    """generate matplotlib png from sql query"""
    temperatures = read_sql(compile_query(session.query(Temperature)),
                            create_engine(DB_URI))
    temperatures.set_index('year', inplace=True)
    temperatures.plot()
    with BytesIO() as buffer:
        plt.gcf().savefig(buffer, format='png')
        response = make_response(buffer.getvalue())
    response.mimetype = 'image/png'
    return response

# API endpoints

from resources import TemperatureListResource
from resources import TemperatureResource
from resources import TemperatureListRSResource

api.add_resource(TemperatureListResource, '/temperatures')
api.add_resource(TemperatureResource, '/temperatures/<string:temperature_id>')
api.add_resource(TemperatureListRSResource, '/temperaturesrs')

if __name__ == '__main__':
    app.run(debug=True)
