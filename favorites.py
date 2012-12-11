from __future__ import with_statement
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy import MetaData, Column, Table
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from contextlib import closing
import urllib
import urllib2
import json
import os
import sys
import getopt

geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

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
	Column('zip', Integer),
)

metadata.create_all()

@app.route('/')
def show_favorites():
	cur = select([favorites_table]).order_by(favorites_table.columns.id.desc()).execute()
	entries = [dict(id=row[0], name=row[1], lat=row[2], lng=row[3], street=row[4], city=row[5], state=row[6], zip=row[7]) for row in cur.fetchall()]
	return render_template('show_favorites.html', entries=entries)
	
@app.route('/get_coords')
def get_coords():
	cur = select([favorites_table]).order_by(favorites_table.columns.id.desc()).execute()
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
	
	result = favorites_table.insert().execute(name=name, street=street, city=city, state=state, zip=zip, lat=lat, lng=lng)
	return redirect(url_for('show_favorites'))
	
@app.route('/add')
def view_favorites():
	return render_template('add_favorites.html')
	
@app.route('/update_list/<id>')
def get_update_entry(id):
	cur = select([favorites_table], favorites_table.columns.id = id).execute()
	#cur = g.db.execute('select id, name, lat, lng, street, city, state, zip from favorites where id = ?', id)
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

def get_port(args):
	try:                                
		opts, args = getopt.getopt(args, "p:", ["port="]) 
	except getopt.GetoptError:                      
		sys.exit(2)
	
	port = 5000
	for opt, arg in opts:          
		if opt in ("-p", "--port"):
			port = arg
	return port
	
if __name__ == '__main__':
	print 'inside main'
	port = int(get_port(sys.argv[1:]))
	host = '0.0.0.0'
	app.run(host=host, port=port)
