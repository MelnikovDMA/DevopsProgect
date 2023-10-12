from flask import Flask, render_template
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
application = app

ip = os.getenv('ip')
PGUSER = str(os.getenv('PGUSER'))
PGPASSWORD = str(os.getenv('PGPASSWORD'))
DATABASE = str(os.getenv('DATABASE'))

POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from models import Student, PlanOfStudy, Gradebook

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schetchik')
def schetchik():

    return render_template('schetchik.html', title='Счетчик')
