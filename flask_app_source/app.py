# all in one mvp for shortlie
# know that if I had more than an hour I probably wouldn't do an all-in-one thing like this...


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database, drop_database
from werkzeug.exceptions import BadRequest


"""
BARE MINIMUM FLASK APP AND DB OBJECT CREATION
"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@postgres/db1'
db = SQLAlchemy(app)


"""
DB MODEL(S)
"""
class Customers(db.Model):
    """
    model defining customer records
    """
    phone_number = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    logins = db.Column(db.Integer, nullable=False, default=0)
    last_login = dbColumn(db.DateTime) # TODO make sure all times are GMT!

    def __repr__(self):
        return '<phone_number %r>' % self.phone_number


"""
ROUTES
"""

# constant defining what version to insert into all the api routes
API_VERSION = 1

# landing page
#
@app.route('/')
def hello_world():
    return 'Flask Dockerized'



"""
MAKE IT SO!
https://www.youtube.com/watch?v=TCqH26PzUvA
"""
if __name__ == '__main__':

    # non-destructively create db and tb tables if they don't exist
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    db.create_all()
    app.run(debug=True,host='0.0.0.0')
