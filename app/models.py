from app.exceptions import ValidationError
from . import db


class Wine(db.Model):
	__tablename__='Wine'
	wid = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	vintage = db.Column(db.Integer)
	winery = db.Column(db.String(255))
	varietal = db.Column(db.String(255))
	color = db.Column(db.Enum(['red','white','rose']))
	price = db.Column(db.Float)
	description = db.Column(db.String(1000))
	image = db.Column(db.String(255))

	def __repr__(self):
		return '<Wine %r>' % self.name


			
