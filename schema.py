class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    lat = db.Column(db.Float(5))
    lng = db.Column(db.Float(5))
    street = db.Column(db.String(40))
    city = db.Column(db.String(40))
    state = db.Column(db.String(20))
    zip = db.Column(db.Integer)

    def __init__(self, name, street, city, state, zip, lat, lng):
        self.name = name
        self.street = street
		self.city = city
		self.state = state
		self.zip = zip
		self.lat = lat
		self.lng = lng

    def __repr__(self):
        return '<Name %r>' % self.name