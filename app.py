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


@app.route('/')
def index():
    return render_template("ui.html")


@app.route('/volunteering')
def indeccx():
    return render_template("volunteering.html")



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

# @app.route('/new_user')
# def new_user():
#     return render_template('new_user.html')


# @app.route('/existing_user')
# def existing_user():
#     return render_template('existing_user.html')


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
                return redirect(url_for('dashboard'))
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

# #Logout
# @app.route('/logout')
# @is_logged_in
# def logout():
#     session.clear()
#     flash('You are now logged out', 'success')
#     return redirect(url_for('login'))




#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
        #MYSQL
        cur = mysql.connection.cursor()
        try:
            result = cur.execute("SELECT * FROM entries WHERE username=%s", [session.get('username')])
            if result > 0:
                entries = cur.fetchall()
                return render_template('dashboard.html', entries=entries)
            else:
                flash("No Entries found", 'danger')
                return render_template('dashboard.html')
        except Exception:
            return render_template('dashboard.html')

# #Add_entry form class
# class add_entryForm(Form):
#     destination = SelectField(u'Select destination', choices=[('Allahabad Station', 'Allahabad Station'), ('PVR Vinayak', 'PVR Vinayak'), ('Civil Lines', 'Civil Lines'), ('Prayag Station', 'Prayag Station')])
#     date = DateField('Date',  format='%Y-%m-%d')
#     time = TimeField('Time' )
#     trainno = IntegerField('Enter Train No if travelling by Train',[validators.optional()])




# #add Entry
# @app.route('/add_entry', methods=['GET', 'POST'])
# @is_logged_in
# def add_entry():
#     form = add_entryForm(request.form)
#     if request.method == 'POST' and form.validate():
#         destination = form.destination.data
#         date = form.date.data
#         time = form.time.data
#         trainno = form.trainno.data
#         #MySQL
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM users WHERE username=%s", [session.get('username')])
#         user = cur.fetchone()
#         cur.execute("INSERT INTO entries(name,fbusername,hostel,room,destination, date ,time ,trainno,username) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(user['name'],user['fbusername'],user['hostel'],user['room'],destination,date,time,trainno,user['username']))

#         mysql.connection.commit()
#         cur.close()

#         flash('Your entry is added', 'success')

#         return redirect(url_for('dashboard'))
#     return render_template('add_entry.html', form=form)


# #Search class
# class SearchForm(Form):
#     date = DateField(u'Enter Date',format='%Y-%m-%d')
#     destination = SelectField(u'Select destination to search for', choices=[('Allahabad Station', 'Allahabad Station'), ('PVR Vinayak', 'PVR Vinayak'), ('Civil Lines', 'Civil Lines'), ('Prayag Station', 'Prayag Station')])
#     trainno = IntegerField(u'Enter Train no', [validators.NumberRange(max=99999,message='Not a Valid Train No.'), validators.optional()], default=None)

# @app.route('/search', methods=['GET', 'POST'])
# @is_logged_in
# def search():
#     form = SearchForm(request.form)
#     if request.method == 'POST' and form.validate():
#         destination = form.destination.data
#         date = form.date.data
#         trainno = form.trainno.data
#         #MYSQL
#         cur = mysql.connection.cursor()
#         if trainno == None:
#             result = cur.execute("SELECT * FROM entries WHERE destination=%s and date=%s", [destination,date])
#             if result > 0:
#                 entries = cur.fetchall()
#                 return render_template('search_results.html', entries=entries,trainno=trainno)
#             else:
#                 flash("No Entries found satisfying your query", 'danger')
#                 return redirect(url_for('search'))
#         else:
#             result = cur.execute("SELECT * FROM entries WHERE destination=%s and date=%s and trainno=%s", [destination,date,trainno])
#             if result > 0:
#                 entries = cur.fetchall()
#                 return render_template('search_results.html', entries=entries,trainno=trainno)
#             else:
#                 flash("No Entries found satisfying your query", 'danger')
#                 return redirect(url_for('search'))
#     else:
#         return render_template('search.html', form=form)






if __name__=='__main__':
    app.secret_key='chit'
    app.debug = True
    app.run(host = 'localhost',port=5001)
