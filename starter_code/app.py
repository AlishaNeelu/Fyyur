#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config. 
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database (done)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from model import *

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
  try:
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    results = db.session.query(Venue.city,Venue.state).distinct(Venue.city,Venue.state).all()
    data = []
    for result in results:
      city = result.city
      state = result.state
      filtered_venue = Venue.query.filter(Venue.state==state).filter(Venue.city==city).all()
      venue_data = []
      data.append({
          'city': result.city,
          'state': result.state,
          'venues': []
        })
      for venue in filtered_venue:
        num_upcoming_shows_count = len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
        data[-1]["venues"].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_upcoming_shows_count
        })
  except:
    db.session.rollback()
    flash("Something went wrong. Please try again.")
    return render_template("pages/home.html")
  finally:
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {
    "count": len(results),
    "data": results
  }
  return render_template('pages/search_venues.html', results=response, 
  search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue_data = Venue.query.get(venue_id)
  genres = []
  genres = venue_data.genres.replace('}','').replace('{','').split(',')
  shows_data = venue_data.show
  past_shows = []
  upcoming_shows = []

  for show in shows_data:
    show_details = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time > datetime.now():
      upcoming_shows.append(show_details)
    else:
      past_shows.append(show_details)


  data = {
    "id": venue_data.id,
    "name": venue_data.name,
    "genres": genres,
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website": venue_data.website,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead (done)
  # TODO: modify data to be the data object returned from db insertion (done)
  form = VenueForm()
  error = False
  if form.validate_on_submit():
    print('validated')
  else:
    for error in form.errors:
      flash('{0} is invalid.'.format(error))
      error = True
  if error == False:
    try:
      is_checked = True if 'seeking_talent' in request.form else False
      newvenue = Venue(name = request.form['name'], city = request.form['city'], state = request.form['state'],
      address = request.form['address'], phone = request.form['phone'], genres = request.form.getlist('genres'),
      image_link = request.form['image_link'], facebook_link = request.form['facebook_link'], 
      website = request.form['website_link'], seeking_talent = is_checked,
      seeking_description = request.form['seeking_description'])
      db.session.add(newvenue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue : {0} was successfully listed!'.format(newvenue.name))
      # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
      db.session.rollback()
      flash('An error occurred creating the Venue. Error: {0} '.format(e))
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.close()
    return render_template('pages/home.html')
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. (done)
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    flash('Venue : {0} was successfully deleted!'.format(venue.name))
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    flash('An error occurred deleting the Venue : {0}. Error : {1} '.format(venue.name,e))
  finally:
    db.session.close()
  return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #(done)
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  
  for result in results:
    upcoming_count = len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all())
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": upcoming_count,
    })
  
  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist_data = Artist.query.get(artist_id)
  shows_data = artist_data.show
  genres = []
  genres = artist_data.genres.replace('}','').replace('{','').split(',')
  past_shows = []
  upcoming_shows = []
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  for show in shows_data:
    show_details = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time > datetime.now():
      upcoming_shows.append(show_details)
    else:
      past_shows.append(show_details)
  
  data = {
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Artist : {0} was successfully updated!'.format(artist.name))
  except Exception as e: 
    db.session.rollback()
    flash('An error occurred. Artist : {0} could not be updated. Error : {1}'.format(artist.name,e))
  finally: 
    db.session.close()
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  genres = []
  genres = venue.genres.replace('}','').replace('{','').split(',')
 
  form['name'].data = venue.name
  form['genres'].data= genres
  form['address'].data= venue.address
  form['city'].data= venue.city
  form['state'].data= venue.state
  form['phone'].data= venue.phone
  form['website_link'].data= venue.website
  form['facebook_link'].data= venue.facebook_link
  form['seeking_talent'].data= venue.seeking_talent
  form['seeking_description'].data= venue.seeking_description
  form['image_link'].data= venue.image_link
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)

    is_checked = True if 'seeking_talent' in request.form else False

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_talent = is_checked
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Venue : {0} was successfully updated!'.format(venue.name))
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Venue : {0} could not be updated at this time. Error : {1}'.format(venue.name,e))
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead (done)
  # TODO: modify data to be the data object returned from db insertion (done)
  form = ArtistForm()
  error = False
  if form.validate_on_submit():
    print('validated')
  else:
    for error in form.errors:
      flash('{0} is invalid.'.format(error))
      error = True
  if error == False:
    try: 
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      website = request.form['website_link']
      seeking_venue = True if 'seeking_venue' in request.form else False
      seeking_description = request.form['seeking_description']

      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, 
              facebook_link=facebook_link, image_link=image_link, website=website, 
              seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()
      flash('Artist : {0} was successfully listed!'.format(artist.name))
    except Exception as e: 
      db.session.rollback()
      flash('An error occurred. Artist could not be listed. Error : {0}'.format(e))
    finally: 
      db.session.close()
    return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. (done)
  data = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

  response = []
  for show in data:
    response.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=response)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except: 
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally: 
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
