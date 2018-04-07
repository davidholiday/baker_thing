

from flask import Flask, request, render_template
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
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(42), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    checkins = db.Column(db.Integer, nullable=False, default=0)
    last_checkin = db.Column(db.DateTime) # TODO make sure all times are GMT!

    def __repr__(self):
        return '<phone_number %r>' % self.phone_number



"""
ROUTES
"""

# constant defining what version to insert into all the api routes
API_AND_VERSION = '/api/v1'

# landing page
#
@app.route('/')
def hello_world():
    app.logger.info('foo')
    return render_template('index.html', tag='fuckface')


checkin_route = API_AND_VERSION + '/checkin'
@app.route(checkin_route, methods=['POST'])
def checkin():
    # there's a much more sophisticated library to handle this sort of thing - but it's out of scope for this exercise.
    # here we'll assume we're dealing with vanilla US numbers 555-555-5555 -- no special characters.


    # validate caller supplied parameter(s)
    #
    phone_number = ""
    try:
        phone_number = str(request.json['phone_number'])
    except:
        app.logger.error('missing phone_number key in payload or payload is not json')
        raise BadRequest #TODO you're not going to use the built-in pages for this in the end...

    if len(phone_number) != 10 or phone_number.isdigit() == False:
        app.logger.error('phone_number must be ten digits with no special characters')
        raise BadRequest

    # check to see if user is in db
    #
    customers_row_object = Customers.query \
                                    .filter_by(phone_number=phone_number) \
                                    .first()

    app.logger.info('customers_row_object is: {}'.format(customers_row_object))

    return phone_number



"""
ENGAGE!
https://www.youtube.com/watch?v=TCqH26PzUvA
"""
if __name__ == '__main__':

    # non-destructively create db table(s) if they don't exist
    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    db.create_all()
    app.run(debug=True,host='0.0.0.0')

