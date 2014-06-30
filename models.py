#!/usr/bin/env python

# https://stackoverflow.com/questions/6290162/how-to-automatically-reflect-database-to-sqlalchemy-declarative
# https://pypi.python.org/pypi/sqlacodegen/1.1.4

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Temperature(Base):
    __tablename__ = u'temperatures'

    year = Column(Integer, primary_key=True)
    cccma_cgcm3_1 = Column(Float)
    csiro_mk3_0 = Column(Float)
    gfdl_cm2_1 = Column(Float)
    miroc3_2_medres = Column(Float)
    mpi_echam5 = Column(Float)
    ncar_ccsm3_0 = Column(Float)
    ukmo_hadcm3 = Column(Float)


# https://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
from sqlalchemy.sql import compiler
from psycopg2.extensions import adapt as sqlescape
# or use the appropiate escape function from your db driver

def compile_query(query):
    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = {}
    for k,v in comp.params.iteritems():
        if isinstance(v, unicode):
            v = v.encode(enc)
        params[k] = sqlescape(v)
    return (comp.string.encode(enc) % params).decode(enc)

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from settings import DB_URI
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
