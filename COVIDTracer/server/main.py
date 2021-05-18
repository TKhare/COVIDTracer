from flask import Flask, render_template, url_for, redirect
from flask_socketio import SocketIO, send
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from tracer import Tracer
import json
import datetime


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'jtpdoerenjaraedsk'
socketio = SocketIO(app)
db = SQLAlchemy(app)


@socketio.on('tracing')
def sendMessage(location):
    send(location)

class User(db.Model):
    address = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    adjList = db.Column(db.String(1000), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    covid = db.Column(db.Boolean, nullable=False)
    def __repr__(self):
        return f'"address": "{self.address}", "name": "{self.name}", "adjList": {self.adjList}, "lat": {self.lat}, "lng": {self.lng}, "covid" : {int(self.covid)}'
db.create_all()
post_parser = reqparse.RequestParser()
post_parser.add_argument('type', type=int, help='No post type given', required = True)
post_parser.add_argument('name', type=str, help='No name given')
post_parser.add_argument('lat', type=float, help='No lat given')
post_parser.add_argument('lng', type=float, help='No lng given')
post_parser.add_argument('day', type=int, help='No Day given')
post_parser.add_argument('month', type=int, help = 'No Month Given')
post_parser.add_argument('year', type=int, help = 'No Year Given')
post_parser.add_argument('list', type=str, help = 'No help given')
post_parser.add_argument('covid', type=bool, help='No covid boolean given')

resource_fields = {
    'address' : fields.String,
    'name' : fields.String,
    'adjList' : fields.String,
    'lat' : fields.Float,
    'lng' : fields.Float, 
    'covid' : fields.Boolean
}
tracer = Tracer(len(User.query.all()))

def sendWarning(ad):
    result = User.query.filter_by(address = ad).first()
    result.covid = True
    db.session.commit()

class DataBase(Resource):

    @marshal_with(resource_fields)
    def get(self, a):
        result = User.query.filter_by(address=a).first()
        if not result:
            abort(404, message='Address does not exists')
        return result

    @marshal_with(resource_fields)
    def post(self, a):
        args = post_parser.parse_args()
        result = User.query.filter_by(address=a).first()
        if args['type'] == 1:
            if result:
                abort(409, message='Address already exists')
            user = User(address = a, name = args['name'], adjList='{ }', lat = args['lat'], lng = args['lng'], covid=False)
            tracer.addAccount(user.address, user.name, int(user.covid))
            tracer.loadGraph()
            db.session.add(user)
            result = user
        elif args['type'] == 2:
            if not result:
                abort(404, message='User Address does not exists')
            al = json.loads(result.adjList)
            result.lat = args['lat']
            result.lng = args['lng']
            for ad in args['list'].split(','):
                person = User.query.filter_by(address=ad).first()
                if person:
                    li = json.loads(person.adjList)
                    al[ad] = {'day':args['day'], 'month' : args['month'], 'year' : args['year'], 'lat' : args['lat'], 'lng' : args['lng']}
                    li[a] = {'day':args['day'], 'month' : args['month'], 'year' : args['year'], 'lat' : args['lat'], 'lng' : args['lng']}
                    person.adjList = json.dumps(li)
                    tracer.addInteraction(a, ad, args['lat'], args['lng'], args['day'], args['month'], args['year'])
                    tracer.loadGraph()
            result.adjList = json.dumps(al)
        elif args['type'] == 3:
            if not result:
                abort(404, message='User Address does not exists')
            if args['covid'] is None:
                abort(404, message='No covid boolean given')
            result.covid = args['covid']
            if result.covid:
                li , ci = tracer.getConnections(a)
                for usr in li:
                    sendWarning(usr)
        db.session.commit()
        return result
    
    def delete(self, a):
        result = User.query.filter_by(address=a).first()
        if not result:
            abort(404, message='Address does not exists')
        db.session.delete(result)
        db.session.commit()

api.add_resource(DataBase, '/database/<string:a>')

@app.route('/')
def home():
    users = User.query.all()
    data = "{ }|"
    for usr in users:
        data += f'{ {usr} }|'
    data +="{ }"
    print(data)
    return render_template('index.html', data=data)

@app.route('/login')
def login():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')

