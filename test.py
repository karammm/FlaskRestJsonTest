from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema,Relationship
from marshmallow_jsonapi import fields
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList,ResourceRelationship
#from sqlalchemy.schema import Sequence

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

# Create a new Flask application
app = Flask(__name__)
app.config['DEBUG'] = True

# Initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345678@localhost/apikaram'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

migrate=Migrate(app, db)
manager=Manager(app)
manager.add_command('db',MigrateCommand)

# Define a class for the Artist table
class TOP(db.Model):#superexam parent
    __tablename__ = 'top'
    id=db.Column(db.Integer,primary_key=True, autoincrement=True, )#Sequence('Top_seq_id', start=1, increment=1))
    name=db.Column(db.String(62),unique=True)
    mid=db.relationship('MID',backref=db.backref('top'))

class MID(db.Model):#exam child
    __tablename__ = 'mid'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(62))
    Schema=db.Column(db.Integer,db.ForeignKey('top.id'))
    bottom=db.relationship('BOTTOM',backref=db.backref('mid'))

class BOTTOM(db.Model):#examsection
    __tablename__='bottom'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(62))
    mid_id=db.Column(db.Integer,db.ForeignKey('mid.id'))

# Create the table
#db.create_all()


# Create data abstraction layer
class TopSchema(Schema):
    class Meta:
        type_ = 'top'
        self_view = 'top_one'
        self_view_kwargs = {'id':'<id>'}
        self_view_many = 'top_many'

    id=fields.Integer()
    name=fields.Str(required=True)
    mid = Relationship(self_view='top_mid',
                            self_view_kwargs={'id': '<id>'},
                            related_view='mid_many',
                            related_view_kwargs={'id': '<id>'},
                            many=True,
                            schema='MidSchema',
                            type_='mid')

class MidSchema(Schema):
    class Meta:
        type_ = 'mid'
        self_view = 'mid_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'mid_many'

    id = fields.Integer()
    name = fields.Str(required=True)
    top_id=fields.Integer(required=True)
    bottom = Relationship(self_view='mid_bottom',
                            self_view_kwargs={'id': '<id>'},
                            related_view='bottom_many',
                            related_view_kwargs={'id': '<id>'},
                            many=True,
                            schema='BottomSchema',
                            type_='bottom')

class BottomSchema(Schema):
    class Meta:
        type_ = 'bottom'
        self_view = 'bottom_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'bottom_many'

    id = fields.Integer()
    name = fields.Str(required=True)
    mid_id=fields.Integer(required=True)


# Create resource managers and endpoints
""" class PersonRealationship(ResourceRelationship):
    schema = ArtistSchema
    data_layer = {'session': db.session,
                  'model': Artist} """

class TopOne(ResourceDetail):
    schema = TopSchema
    data_layer = {'session': db.session,
                  'model': TOP}

class TopMany(ResourceList):
    schema = TopSchema
    data_layer = {'session': db.session,
                  'model': TOP}

class BottomMany(ResourceList):
    schema = BottomSchema
    data_layer = {'session': db.session,
                  'model': BOTTOM}

class BottomOne(ResourceDetail):
    schema = BottomSchema
    data_layer = {'session': db.session,
                  'model': BOTTOM}

class MidMany(ResourceList):
    schema = MidSchema
    data_layer = {'session': db.session,
                  'model': MID}

class MidOne(ResourceDetail):
    schema = MidSchema
    data_layer = {'session': db.session,
                  'model': MID}

class TopMid(ResourceRelationship):
    schema = TopSchema
    data_layer = {'session': db.session,
                  'model': TOP}

class MidBottom(ResourceRelationship):
    schema = MidSchema
    data_layer = {'session': db.session,
                  'model': MID}


api = Api(app)
api.route(TopMany, 'top_many', '/top')
api.route(TopOne, 'top_one', '/top/<int:id>')

api.route(BottomMany, 'bottom_many', '/bottom')
api.route(BottomOne, 'bottom_one', '/bottom/<int:id>')

api.route(MidMany, 'mid_many', '/mid')
api.route(MidOne, 'mid_one', '/mid/<int:id>')

api.route(TopMid, 'top_mid', '/top/id:<id>/relationships/mid')
api.route(MidBottom, 'mid_bottom', '/mid/id:<id>/relationships/bottom')


# main loop to run app in debug mode
if __name__ == '__main__':
    manager.run()