
import json
from flask import make_response
from flask.ext.restful import Resource
from flask.ext.restful import reqparse
from flask.ext.restful import abort

from sqlalchemy import create_engine
from settings import DB_URI
from db import session
from models import Temperature
from models import compile_query
from pandas.io.sql import read_sql

parser = reqparse.RequestParser()
parser.add_argument('year', type=str)

class TemperatureResource(Resource):
    """placeholder for individual resource endpoint"""
    pass

class TemperatureListResource(Resource):
    def get(self):
        temperatures = read_sql(compile_query(session.query(Temperature)),
                                create_engine(DB_URI))
        res = make_response(temperatures.to_json(orient='records'))
        res.mimetype = 'application/json'
        return res

    def post(self):
        parsed_args = parser.parse_args()
        temperature = Temperature(task=parsed_args['year'])
        session.add(temperature)
        session.commit()
        return temperature.serialize, 201

class TemperatureListRSResource(Resource):
    """An endpoint for accommodating rickshaw-specific JSON formatting"""
    def get(self):
        temperatures = read_sql(compile_query(session.query(Temperature)),
                                create_engine(DB_URI))
        temperatures.set_index('year', inplace=True)
        data = []
        for name, series in temperatures.iterkv():
            df = series.reset_index()
            df['x'] = df.pop('year')
            df['y'] = df.pop(name)
            data.append({'data': df.to_dict(outtype='records'), 'name': name})
        response = make_response(json.dumps(data))
        response.mimetype = 'application/json'
        return response

