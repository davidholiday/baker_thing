# simple loyalty point tracker
# david holiday 08APR18


import pytz

from datetime import datetime

from flask import Flask, request, render_template, flash

from flask_mail import Mail, Message

from flask_sqlalchemy import SQLAlchemy

from flask_bootstrap import Bootstrap

from sqlalchemy_utils import database_exists, create_database, drop_database

from werkzeug.exceptions import BadRequest




"""
BARE MINIMUM FLASK APP SETUP
"""

# bootstraps the thing
app = Flask(__name__)
app.secret_key = "secret"

# db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@postgres/db1'
db = SQLAlchemy(app)

# for flask bootstrap integration
Bootstrap(app)

# for flask mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'mr.baker.1919@gmail.com'
app.config['MAIL_USERNAME'] = 'mr.baker.1919@gmail.com'
app.config['MAIL_PASSWORD'] = '' #FIXME put password here!
mail = Mail(app)




"""
DB MODEL
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
    last_checkin = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
        return '<phone_number %r>' % self.phone_number




"""
ROUTES
"""

# constant defining what version to insert into all the api routes
API_AND_VERSION = '/api/v1'


@app.route('/')
def root():
    """
    renders the index page for the caller

    :return:
    """
    return render_template('index.html')


registration_route = API_AND_VERSION + '/registration'
@app.route(registration_route, methods=['POST'])
def registration():
    """
    target for registration form submit. will redirect back to index page when complete

    :return:
    """

    # grab caller supplied parameters (relying on client to validate)
    #
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
    except:
        app.logger.error('missing k,v pair in payload or payload is not form data')
        raise BadRequest


    # check to see if user is in db
    #
    customers_row_object = Customers.query \
                                    .filter_by(phone_number=phone_number) \
                                    .first()

    app.logger.info('customers_row_object is: {}'.format(customers_row_object))


    # build response
    #

    # create the record if they aren't already in the db
    if customers_row_object == None:

        timestamp = datetime.now(pytz.utc)

        customers_row_object = Customers(first_name=first_name,
                                         last_name=last_name,
                                         email=email,
                                         phone_number=phone_number,
                                         points=50,
                                         checkins=1,
                                         last_checkin = timestamp)

        db.session.add(customers_row_object)
        db.session.commit()

        message_bg = 'bg-info'

        message = 'thanks for registering! ' \
                  'you have checked in {} times, ' \
                  'you have {} points, ' \
                  'and your last checking was at {}'.format(1, 50, timestamp )

        template = 'index.html'

        # send email
        msg = Message(message, recipients=[email])
        mail.send(msg)


    # the user can't access the registration page directly, so if they accidentally enter someone else's phone number
    # we need to tell them that.
    # FIXME make it so the phone number is pre-populated and can't be altered to prevent this situation
    else:
        message_bg = 'bg-danger'
        message = 'oops! someone is already registered with that number!'
        template = 'index.html'

    return render_template(template, message=message, message_bg=message_bg)




checkin_route = API_AND_VERSION + '/checkin'
@app.route(checkin_route, methods=['POST'])
def checkin():
    """
    target for checkin form submit. redirects either to index page or registration page depending on whether or not the
    caller is registered

    :return:
    """

    # grab caller supplied parameter(s) (relying on client to validate)
    #
    try:
        phone_number = request.form['phone_number']
    except:
        app.logger.error('missing phone_number key in payload or payload is not form data')
        raise BadRequest


    # check to see if user is in db
    #
    customers_row_object = Customers.query \
                                    .filter_by(phone_number=phone_number) \
                                    .first()

    app.logger.info('customers_row_object is: {}'.format(customers_row_object))


    # build response
    #
    message_bg = 'bg-info'

    if customers_row_object == None:
        message = 'you must be new here - welcome! please register to start earning points.'
        template = 'registration.html'
    else:

        # check time since last checkin (should be >5m)
        timestamp_now = datetime.now(pytz.utc)
        timestamp_last_checkin = customers_row_object.last_checkin
        minutes_since_last_checkin = (timestamp_now - timestamp_last_checkin).total_seconds() / 60

        if minutes_since_last_checkin >= 5:

            # update points
            customers_row_object.checkins += 1
            customers_row_object.points += 20
            customers_row_object.last_checkin = timestamp_now
            db.session.commit()


            # set message and send email
            message = 'w00t! you just earned 20 loyalty points! ' \
                      'you have checked in {} times, ' \
                      'you now have {} points, ' \
                      'and your last checking was at {}'.format(customers_row_object.checkins,
                                                                customers_row_object.points,
                                                                timestamp_now)

            msg = Message(message, recipients=[customers_row_object.email])
            mail.send(msg)

        else:
            message_bg = 'bg-danger'

            message = 'it has been {} minute(s) since you last checked in. ' \
                      'you can only check in every five minutes!'.format(int(minutes_since_last_checkin))

        template = 'index.html'

    return render_template(template, message=message, message_bg=message_bg)




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

