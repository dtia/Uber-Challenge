from __future__ import with_statement
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify
from contextlib import closing
import sqlite3
import urllib
import urllib2
import json

# configuration
DATABASE = '/tmp/favorites.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('sqlite_schema.sql') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  g.db.close()

@app.route('/')
def show_favorites():
	cur = g.db.execute('select id, name, lat, lng, street, city, state, zip from favorites order by id desc')
	entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	return render_template('show_favorites.html', entries=entries)
	
@app.route('/get_coords')
def get_coords():
	cur = g.db.execute('select id, name, lat, lng, street, city, state, zip from favorites order by id desc')
	entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	return jsonify(favorites=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	name = request.form['name']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	zip = request.form['zip']
	lat, lng = geocode_address(street, city, state, zip)

	g.db.execute('insert into favorites (name, street, city, state, zip, lat, lng) values (?, ?, ?, ?, ?, ?, ?)',
           [name, street, city, state, zip, lat, lng])
	g.db.commit()
	return redirect(url_for('show_favorites'))
	
@app.route('/add')
def view_favorites():
	return render_template('add_favorites.html')
	
@app.route('/update_list/<id>')
def get_update_entry(id):
	cur = g.db.execute('select id, name, lat, lng, street, city, state, zip from favorites where id = ?', id)
	entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	return render_template('update_favorite.html', entries=entries)
	
@app.route('/update', methods=['POST'])
def update_entry():
	fav_id = request.form['id']
	name = request.form['name']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	zip = request.form['zip']
	lat, lng = geocode_address(street, city, state, zip)

	g.db.execute('update favorites set name = ?, street = ?, city = ?, state = ?, zip = ?, lat = ?, lng = ? where id = ?',
		[name, street, city, state, zip, lat, lng, fav_id])
	g.db.commit()
	return redirect(url_for('show_favorites'))
	
@app.route('/delete/<id>')
def delete_entry(id):
	g.db.execute('delete from favorites where id = ?', id)
	g.db.commit()
	return redirect(url_for('show_favorites'))
	
def geocode_address(street, city, state, zip):
	address = get_address(street, city, state, zip)
	geocode_param = urllib.quote_plus('address=' + address)
	url = geocode_url+'address=' + geocode_param + '&sensor=false'
	resp = urllib2.urlopen(url).read()
	decoded = json.loads(resp)
	location = decoded['results'][0]['geometry']['location']
	return (location['lat'], location['lng'])

def get_address(street, city, state, zip):
	return street + ' ' + city + ' ' + state + ' ' + zip 
	
if __name__ == '__main__':
  init_db()
  app.run()
