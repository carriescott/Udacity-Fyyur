#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
import logging
import sys
import collections
import collections.abc

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.app_context().push()

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='Venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='Artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  places = Venue.query.distinct(Venue.city, Venue.state).all()
  venues = Venue.query.all()
  areas = []

  for place in places:
    temp_venues = []
    for venue in venues:
        if venue.city == place.city and venue.state == place.state:
            num_shows = 0
            for show in venue.shows:
                if show.start_time > datetime.now():
                    num_shows += 1
            temp_venues.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_shows
            })
        areas.append({
        "city": venue.city,
        "sate": venue.state,
        "venues": temp_venues
        })

  print('areas', areas)

#   data=[{
#     "city": "San Francisco",
#     "state": "CA",
#     "venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }, {
#     "city": "New York",
#     "state": "NY",
#     "venues": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }]

  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  print('search_term', search_term)

  response = {}
  response['data'] = []
  formatted_input = '%{0}%'.format(search_term)
  venues = Venue.query.filter(Venue.name.ilike(formatted_input)).all()
  response['count'] = len(venues)

  for venue in venues:
    num_shows = 0
    for show in venue.shows:
        if show.start_time > datetime.now():
            num_shows += 1
    venue_item = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_shows
    }
    response['data'].append(venue_item)

  print('response', response)

#   response={
#     "count": 1,
#     "data": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  setattr(venue, "genres", venue.genres.split(","))
  venue.genres[0] = venue.genres[0].replace("{", "")
  venue.genres[len(venue.genres)-1] = venue.genres[len(venue.genres)-1].replace("}", "")
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    if show.start_time > datetime.now():
        show_item = {}
        show_item["artist_id"] = show.Artist.id
        show_item["artist_name"] = show.Artist.name
        show_item["artist_image_link"] = show.Artist.image_link
        show_item["start_time"] = show.start_time
        upcoming_shows.append(show_item)
    else:
        show_item = {}
        show_item["artist_id"] = show.Artist.id
        show_item["artist_name"] = show.Artist.name
        show_item["artist_image_link"] = show.Artist.image_link
        show_item["start_time"] = show.start_time
        past_shows.append(show_item)

  setattr(venue, "upcoming_shows", upcoming_shows)
  setattr(venue, "past_shows", past_shows)
  setattr(venue, "upcoming_shows_count", len(upcoming_shows))
  setattr(venue, "past_shows_count", len(past_shows))

  print('upcoming shows', venue.upcoming_shows)
  print('past shows', venue.past_shows)

  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  form = VenueForm(request.form)
  print('form', form.name.data)

  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    genres = form.genres.data
    website = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

    venue = Venue(
    name = name,
    city = city,
    state = state,
    address = address,
    phone = phone,
    image_link = image_link,
    facebook_link = facebook_link,
    genres = genres,
    website = website,
    seeking_talent = seeking_talent,
    seeking_description = seeking_description)
    db.session.add(venue)
    db.session.commit()

  except:
    error = True
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Venue ' + form.name.data + ' was successfully listed!')
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Venue could not be deleted.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
     abort(500)
  else:
    flash('Venue ' + form.name.data + ' was successfully listed!')
    return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  artist_list = []

  for artist in artists:
    artist_item = {
        "id": artist.id,
        "name": artist.name
    }
    artist_list.append(artist_item)

  print('list', artist_list)

#   data=[{
#     "id": 4,
#     "name": "Guns N Petals",
#   }, {
#     "id": 5,
#     "name": "Matt Quevedo",
#   }, {
#     "id": 6,
#     "name": "The Wild Sax Band",
#   }]

  return render_template('pages/artists.html', artists=artist_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form['search_term']
  print('search_term', search_term)

  response = {}
  response['data'] = []
  formatted_input = '%{0}%'.format(search_term)
  artists = Artist.query.filter(Artist.name.ilike(formatted_input)).all()
  response['count'] = len(artists)

  for artist in artists:
    num_shows = 0
    for show in artist.shows:
        if show.start_time > datetime.now():
            num_shows += 1
    artist_item = {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_shows
    }
    response['data'].append(artist_item)

  print('response', response)

#   response={
#     "count": 1,
#     "data": [{
#       "id": 4,
#       "name": "Guns N Petals",
#       "num_upcoming_shows": 0,
#     }]
#   }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  setattr(artist, "genres", artist.genres.split(","))
  artist.genres[0] = artist.genres[0].replace("{", "")
  artist.genres[len(artist.genres)-1] = artist.genres[len(artist.genres)-1].replace("}", "")
  past_shows = []
  upcoming_shows =[]

  for show in artist.shows:
      if show.start_time > datetime.now():
          show_item = {}
          show_item["venue_id"] = show.Venue.id
          show_item["venue_name"] = show.Venue.name
          show_item["venue_image_link"] = show.Venue.image_link
          show_item["start_time"] = show.start_time
          upcoming_shows.append(show_item)
      else:
          show_item = {}
          show_item["venue_id"] = show.Venue.id
          show_item["venue_name"] = show.Venue.name
          show_item["venue_image_link"] = show.Venue.image_link
          show_item["start_time"] = show.start_time
          past_shows.append(show_item)

  setattr(artist, "upcoming_shows", upcoming_shows)
  setattr(artist, "past_shows", past_shows)
  setattr(artist, "upcoming_shows_count", len(upcoming_shows))
  setattr(artist, "past_shows_count", len(past_shows))

  print('upcoming shows', artist.upcoming_shows)
  print('past shows', artist.past_shows)


  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  print('Artist', artist)

  artist_temp = {}
  artist_temp['id'] = artist.id
  artist_temp['name'] = artist.name
  artist_temp['genres'] = artist.genres
  artist_temp['city'] = artist.city
  artist_temp['state'] = artist.state
  artist_temp['phone'] = artist.phone
  artist_temp['website'] = artist.website
  artist_temp['facebook_link'] = artist.facebook_link
  artist_temp['seeking_venue'] = artist.seeking_venue
  artist_temp['seeking_description'] = artist.seeking_description
  artist_temp['image_link'] = artist.image_link

  print('website', artist_temp['website'])
  print('name', artist_temp['name'])

  form.name.data = artist_temp['name']
  form.genres.data = artist_temp['genres']
  form.city.data = artist_temp['city']
  form.state.data = artist_temp['state']
  form.phone.data = artist_temp['phone']
  form.website_link.data = artist_temp['website']
  form.facebook_link.data = artist_temp['facebook_link']
  form.seeking_venue.data = artist_temp['seeking_venue']
  form.seeking_description.data = artist_temp['seeking_description']
  form.image_link.data = artist_temp['image_link']

  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_temp)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  form = ArtistForm(request.form)
  print('form', form.name.data)

  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    artist = Artist(
    name=name,
    city=city,
    state=state,
    phone=phone,
    genres=genres,
    image_link=image_link,
    facebook_link=facebook_link,
    website=website,
    seeking_venue=seeking_venue,
    seeking_description=seeking_description
    )

    db.session.add(artist)
    db.session.commit()

  except:
    error = True
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Artist ' + form.name.data + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_temp = {}

  print('venue', venue)

  venue_temp['id'] = venue.id
  venue_temp['name'] = venue.name
  venue_temp['genres'] = venue.genres
  venue_temp['address'] = venue.address
  venue_temp['city'] = venue.city
  venue_temp['state'] = venue.state
  venue_temp['phone'] = venue.phone
  venue_temp['website'] = venue.website
  venue_temp['facebook_link'] = venue.facebook_link
  venue_temp['seeking_talent'] = venue.seeking_talent
  venue_temp['seeking_description'] = venue.seeking_description
  venue_temp['image_link'] = venue.image_link

  form.name.data = venue_temp['name']
  form.genres.data = venue_temp['genres']
  form.address.data = venue_temp['address']
  form.city.data = venue_temp['city']
  form.state.data = venue_temp['state']
  form.phone.data = venue_temp['phone']
  form.website_link.data = venue_temp['website']
  form.facebook_link.data = venue_temp['facebook_link']
  form.seeking_talent.data = venue_temp['seeking_talent']
  form.seeking_description.data = venue_temp['seeking_description']
  form.image_link.data = venue_temp['image_link']

  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_temp)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  form = VenueForm(request.form)
  print('form', form.name.data)

  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    genres = form.genres.data
    website = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

    venue = Venue(
    name = name,
    city = city,
    state = state,
    address = address,
    phone = phone,
    image_link = image_link,
    facebook_link = facebook_link,
    genres = genres,
    website = website,
    seeking_talent = seeking_talent,
    seeking_description = seeking_description)
    db.session.add(venue)
    db.session.commit()

  except:
    error = True
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Venue ' + form.name.data + ' was successfully listed!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  form = ArtistForm(request.form)

  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    artist = Artist(
    name=name,
    city=city,
    state=state,
    phone=phone,
    genres=genres,
    image_link=image_link,
    facebook_link=facebook_link,
    website=website,
    seeking_venue=seeking_venue,
    seeking_description=seeking_description
    )

    db.session.add(artist)
    db.session.commit()

  except:
    error = True
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Artist ' + form.name.data + ' was successfully listed!')
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.all()
  shows_list=db.session.query(Show).join(Venue,Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()
  print('shows_list', shows_list)
  data = []

  for show in shows_list:
    print('show', show)
    print('venue_id', show.venue_id)
    print('venue_name', show.Venue.name)
    print('artist_id', show.artist_id)
    print('artist_name', show.Artist.name)
    print('start_time', show.start_time)

    show_item = {
        "venue_id": show.venue_id ,
        "venue_name": show.Venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": show.start_time
        }

    data.append(show_item)

  print('data', data)

  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  form = ShowForm(request.form)

  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    show = Show(
    artist_id = artist_id,
    venue_id = venue_id,
    start_time = start_time
    )

    db.session.add(show)
    db.session.commit()

  except:
    error = True
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
