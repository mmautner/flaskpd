
import json
from flask import make_response
from flask import request
from flask.ext.restful import Resource
from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with

from sqlalchemy import create_engine
from settings import DB_URI
from db import session
from models import Temperature
from models import compile_query_mysql
from pandas.io.sql import read_sql


# TODO: infer reqparser from SQLAlchemy model
parser = reqparse.RequestParser()
parser.add_argument('year', type=int)
parser.add_argument('cccma_cgcm3_1', type=float)
parser.add_argument('csiro_mk3_0', type=float)
parser.add_argument('gfdl_cm2_1', type=float)
parser.add_argument('miroc3_2_medres', type=float)
parser.add_argument('mpi_echam5', type=float)
parser.add_argument('ncar_ccsm3_0', type=float)
parser.add_argument('ukmo_hadcm3', type=float)

# TODO: infer serializable format from SQLAlchemy model
temperature_fields = {
    'year': fields.Integer,
    'cccma_cgcm3_1': fields.Float,
    'csiro_mk3_0': fields.Float,
    'gfdl_cm2_1': fields.Float,
    'miroc3_2_medres': fields.Float,
    'mpi_echam5': fields.Float,
    'ncar_ccsm3_0': fields.Float,
    'ukmo_hadcm3': fields.Float,
    'uri': fields.Url('temperature', absolute=True),
}

class TemperatureResource(Resource):
    """placeholder for individual resource endpoint"""
    @marshal_with(temperature_fields)
    def get(self, year):
        temperature = session.query(Temperature).filter(Temperature.year == year).first()
        if not temperature:
            abort(404, message="Temperature {} doesn't exist".format(year))
        return temperature

    def delete(self, year):
        temperature = session.query(Temperature).filter(Temperature.year == year).first()
        if not temperature:
            abort(404, message="Temperature {} doesn't exist".format(year))
        session.delete(temperature)
        session.commit()
        return {}, 204

    @marshal_with(temperature_fields)
    def put(self, year):
        parsed_args = parser.parse_args()
        temperature = session.query(Temperature).filter(Temperature.year == year).first()
        for arg in parsed_args:
            print arg
            import ipdb; ipdb.set_trace()
            temperature['arg'] = parsed_args[arg]
        session.add(temperature)
        session.commit()
        return temperature, 201


class TemperatureListResource(Resource):
    def get(self):
        """Query args spec:

        limit: integer
        offset: integer
        filters: [
            {field_name: [str], operator: [=/>/</>=/<=/!=], value: [str/int/date]}
            OR
            {operator: [AND/OR], filters: []}
        ]
        """
        query = session.query(Temperature)
        if request.args.get('limit'):
            query = query.limit(int(request.args['limit']))

        temperatures = read_sql(compile_query_mysql(query),
                                create_engine(DB_URI))
        
        res = make_response(temperatures.to_json(orient='records'))
        res.mimetype = 'application/json'
        return res

    @marshal_with(temperature_fields)
    def post(self):
        parsed_args = parser.parse_args()
        temperature = Temperature(**parsed_args)
        session.add(temperature)
        session.commit()
        return temperature, 201

class TemperatureListRSResource(Resource):
    """An endpoint for accommodating rickshaw-specific JSON formatting"""
    def get(self):
        temperatures = read_sql(compile_query_mysql(session.query(Temperature)),
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

