from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField,IntegerField
from passlib.hash import sha256_crypt
from functools import wraps
from wtforms_components import TimeField, SelectField, DateRange,Email
from datetime import datetime, date
from wtforms.fields.html5 import DateField

app = Flask(__name__)


# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MYSQL
mysql = MySQL(app)

@app.route('/home')
@app.route('/')
def index():
    return render_template("ui.html")


@app.route('/volunteering')
def indeccx():
    return render_template("volunteering.html")

@app.route('/cashgate')
def cashgate():
    return render_template("cashgate.html")

class DonateForm(Form):
    mask = StringField('Quantity of masks', [validators.NumberRange(max=99999)])
    ppe = StringField('Quantity of PPE', [validators.NumberRange(max=99999)])
    sanit = StringField('Quantity of Sanitisers', [validators.NumberRange(max=99999)])
    food_units = StringField('Food Units', [validators.Length(min=1,max=10)])

@app.route('/donation', methods=['GET', 'POST'])
def donation():
    form = DonateForm(request.form)
    if request.method == 'POST' and form.validate():
        mask = form.mask.data
        ppe = form.ppe.data
        sanit = form.sanit.data
        food_units = form.food_units.data

    
    return render_template("donation.html")

# Register Form class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Email()])
    city = StringField('City', [validators.Length(min=1,max=10)])
    org = StringField('Organisation', [validators.Length(min=1, max=10)])
    mobile = IntegerField('Mobile', [validators.NumberRange(max=9999999999)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

#User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        org = form.org.data
        city = form.city.data
        email = form.email.data
        mobile = form.mobile.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        #Execute query
        cur.execute("INSERT INTO users(name, org, email, city, mobile, password) VALUES(%s,%s,%s,%s,%s,%s)",(name, org, email, city, mobile, password))

        #Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form fields
        email = request.form['email']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']
            name = data['name']

            #compare Passwords
            if sha256_crypt.verify(password_candidate,password):
                session['logged_in'] = True
                session['email'] = email
                session['name'] = name

                flash('You are now logged in', 'success')
                return redirect(url_for('donate'))
            else:
                error = 'Invalid Password'
                return render_template('login.html', error=error)
            #Close connection
            cur.close()
        else:
            error = 'User not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorised, Please Login ', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    form = DonateForm(request.form)
    if request.method == 'POST' and form.validate():
        mask = form.mask.data
        ppe = form.ppe.data
        food_units = form.food_units.data
        email= session.get('email')
        
        try:
            # Create cursor
            cur = mysql.connection.cursor()

            #Execute query
            cur.execute("INSERT INTO donation(email,mask,ppe,food_units) VALUES(%s,%s,%s,%s,%s)",(email,mask,ppe,food_units))

            #Commit to DB
            mysql.connection.commit()

            #Close connection
            cur.close()

            flash('You have registered the donation', 'success')
        except Exception:
            flash("Login first","Try again")
            return render_template('login.html')
    return render_template('dashboard.html')

if __name__=='__main__':
    app.secret_key='chit'
    app.debug = True
    app.run(host = 'localhost',port=5001)

cost = {
    "ppe" : 500,
    "mask" : 20,
    "foodp" : 50,
    "sanit" : 200
}

requirement = {
  "city1": 100000,
  "city2": 200000,
  "city3": 300000
}

severity = {
    "city1" : 0.02,
    "city2" : 0.05,
    "city3" : 0.01
}


# def getestimate():
#     try:
#         # Create cursor
#         cur = mysql.connection.cursor()

#         result = cur.execute("Select * from inventory")
#         if result > 0:
#             tcost = 0
#             pmcost = cost["ppe"]+cost["mask"]*30+cost['foodp']*60+cost["sanit"]
#             for x in requirement:
#                 tcost = tcost + requirement[x]*severity[x]*tcost

            
