from flask import Flask
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand


# Create a new Flask application
app = Flask(__name__)

# Initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345678@localhost/apikaram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate=Migrate(app, db)
manager=Manager(app)
manager.add_command('db',MigrateCommand)

# Define a class for the Artist table
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    birth_year = db.Column(db.Integer)
    genre = db.Column(db.String(80))

# Define the Artwork table
class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'))
    artist = db.relationship('Artist',backref=db.backref('artworks'))

# Create the table
#db.create_all()

class ArtistSchema(Schema):
    class Meta:
        type_ = 'artist'
        self_view = 'artist_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'artist_many'

    id = fields.Integer()
    name = fields.Str(required=True)
    birth_year = fields.Integer(load_only=True)
    genre = fields.Str()
    artworks = Relationship(self_view = 'artist_artworks',
        self_view_kwargs = {'id': '<id>'},
        related_view = 'artwork_many',
        many = True,
        schema = 'ArtworkSchema',
        type_ = 'artwork')

class ArtworkSchema(Schema):
    class Meta:
        type_ = 'artwork'
        self_view = 'artwork_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'artwork_many'

    id = fields.Integer()
    title = fields.Str(required=True)
    artist_id = fields.Integer(required=True)

class ArtworkMany(ResourceList):
    schema = ArtworkSchema
    data_layer = {'session': db.session,
                  'model': Artwork}

class ArtworkOne(ResourceDetail):
    schema = ArtworkSchema
    data_layer = {'session': db.session,
                  'model': Artwork}

class ArtistArtwork(ResourceRelationship):
    schema = ArtistSchema
    data_layer = {'session': db.session,
                  'model': Artist}


class ArtistMany(ResourceList):
    schema = ArtistSchema
    data_layer = {'session': db.session,
                  'model': Artist}

class ArtistOne(ResourceDetail):
    schema = ArtistSchema
    data_layer = {'session': db.session,
                  'model': Artist}



api = Api(app)
api.route(ArtistMany, 'artist_many', '/artists')
api.route(ArtistOne, 'artist_one', '/artists/<int:id>')
api.route(ArtworkOne, 'artwork_one', '/artworks/<int:id>')
api.route(ArtworkMany, 'artwork_many', '/artworks')
api.route(ArtistArtwork, 'artist_artworks','/artists/<int:id>/relationships/artworks')

# main loop to run app in debug mode
if __name__ == '__main__':
    manager.run()