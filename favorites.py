from __future__ import with_statement
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float, MetaData, Column, Table, create_engine, \
	update, delete
from sqlalchemy.sql import select
from contextlib import closing
import urllib
import urllib2
import json
import os

### App / DB Setup
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata = MetaData(bind=engine)

favorites_table = Table('favorites', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(40)),
	Column('lat', Float(5)),
	Column('lng', Float(5)),
	Column('street', String(40)),
	Column('city', String(40)),
	Column('state', String(10)),
	Column('zip', String(5)),
)
metadata.create_all()
###

### Constants
geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?'
###

@app.route('/')
def show_favorites():
	try:
		cur = select([favorites_table]).order_by(favorites_table.c.id.desc()).execute()
		entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	except:
		print 'There was an error retrieving favorites from the database.'
		
	return render_template('show_favorites.html', entries=entries)
	
@app.route('/get_coords')
def get_coords():
	try:
		cur = select([favorites_table]).order_by(favorites_table.c.id.desc()).execute()
		entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	except:
		print 'There was an error retrieving favorites from the database.'

	return jsonify(favorites=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	name = request.form['name']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	zip = request.form['zip']
	lat, lng = geocode_address(street, city, state, zip)
	
	try:
		favorites_table.insert().execute(name=name, street=street, city=city, state=state, zip=zip, lat=lat, lng=lng)
	except:
		print 'There was an error adding this favorite to the database.'

	return redirect(url_for('show_favorites'))
	
@app.route('/add')
def view_favorites():
	return render_template('add_favorites.html')
	
@app.route('/update_list/<fav_id>')
def get_update_entry(fav_id):
	try:
		cur = select([favorites_table], favorites_table.c.id == fav_id).execute()
		entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	except:
		print 'There was an error retrieving this favorite from the database.'
		
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
	
	try:
		update(favorites_table, favorites_table.c.id == fav_id).execute(name=name, street=street, city=city, state=state, zip=zip, lat=lat, lng=lng)
	except:
		print 'There was an error updating this favorite.'

	return redirect(url_for('show_favorites'))
	
@app.route('/delete/<fav_id>')
def delete_entry(fav_id):
	try:
		delete(favorites_table, favorites_table.c.id == fav_id).execute()
	except:
		print 'There was an error deleting this favorite.'
		
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