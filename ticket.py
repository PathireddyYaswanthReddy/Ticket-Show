from flask import Flask , render_template , request
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
import os
from sqlalchemy import exc
import datetime
from datetime import datetime
import pytz
import calendar
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__ , template_folder='templates', static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_dir, "ticketshow.sqlite3")

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

'''Model for Database'''

class user(db.Model):
    __tablename__ = 'user'
    username  = db.Column(db.String, nullable = False)
    email = db.Column(db.String , primary_key = True , nullable = False)
    password = db.Column(db.String , nullable = False)

class admin(db.Model):
    __tablename__ = 'admin'
    username  = db.Column(db.String, nullable = False)
    email = db.Column(db.String , primary_key = True , nullable = False)
    password = db.Column(db.String , nullable = False)

class venue(db.Model):
    __tablename__ = 'venue'
    venue_id = db.Column(db.String, primary_key = True)
    venue_name = db.Column(db.String , nullable = False)
    location = db.Column(db.String , nullable = False)
    address = db.Column(db.String , nullable = False)
    city = db.Column(db.String , nullable = False)
    state = db.Column(db.String , nullable = False)
    admin_email = db.Column(db.String , db.ForeignKey("admin.email") , nullable = False)

class show(db.Model):
    __tablename__ = 'show'
    show_id = db.Column(db.Integer, primary_key = True , autoincrement = True)
    show_name = db.Column(db.String , nullable = False)
    capacity = db.Column(db.Integer , nullable = False)
    time = db.Column(db.String , nullable = False)
    date = db.Column(db.String , nullable =False)
    screen = db.Column(db.String , nullable = True)
    venue_id = db.Column(db.String , db.ForeignKey("venue.venue_id"), nullable = False , primary_key = True)
    film_certificate = db.Column(db.String , nullable = False)
    genre = db.Column(db.String , nullable = False)
    price  = db.Column(db.Integer , nullable = False)
    format = db.Column(db.String , nullable = False)
    language = db.Column(db.String , nullable = False)
    booked_seats = db.Column(db.Integer , nullable = False , default = 0)
    show_rating = db.Column(db.Integer)

class bookings(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    user_email = db.Column(db.String , db.ForeignKey("user.email") , nullable = False)
    show_id = db.Column(db.Integer , db.ForeignKey("show.show_id") , nullable = False)
    venue_id = db.Column(db.String , db.ForeignKey("venue.venue_id") , nullable = False)
    no_of_seats = db.Column(db.Integer , nullable  = False)
    screen = db.Column(db.String , db.ForeignKey("show.screen"))
    rating = db.Column(db.Integer)



'''Password encryption and decryption'''
def password_encrypt(passw):
    ph = PasswordHasher()
    enc_pass = ph.hash(passw)
    return enc_pass

def password_decrypt(passw):
    ph = PasswordHasher()
    try :
        ph.verify(passw , request.form["password"])
        return True
    except :
        return False   
    
'''Routing for different pages'''

@app.route("/" , methods = ["GET" , "POST"])

def selectuser():
    if request.method == "GET" :
        return render_template("selectuser.html")
    


@app.route("/userlogin" , methods = ["GET" , "POST"])

def userlogin():
    if request.method == "GET" :
        return render_template("userlogin.html")

    if request.method == "POST" :
        email = request.form["email"]
        
        logincheck = user.query.filter(user.email == email).first()

        if logincheck and password_decrypt(logincheck.password):
            name = user.query.filter(user.email == email).first()
            username = name.username
            d1 = datetime.today().strftime("%Y-%m-%d")
            IST = pytz.timezone('Asia/Kolkata')
            t1 = datetime.now(IST).strftime('%H:%M')
            shows = show.query.with_entities(show.show_name , show.genre , show.date , show.time).filter(show.date >= d1).distinct().all()
            shows1 = show.query.filter(show.date >= d1).distinct().all()
            shows2 = show.query.distinct().all()
            rate = bookings.query.all()
            bookingrating = {}
            for i in rate :
                bookingrating[i.show_id] = []
                
            for i in rate :
                if i.rating != None :
                    bookingrating[i.show_id].append(i.rating)
            for i in bookingrating :
                if len(bookingrating[i]) != 0:
                    bookingrating[i] = sum(bookingrating[i])/len(bookingrating[i])
            
            for i in shows2:
                if i.show_id in bookingrating and bookingrating[i.show_id] != []:
                    i.show_rating = bookingrating[i.show_id]
            db.session.commit()
            
            lang = {}
            movieformat = {}
            movierating = {}


            for i in shows1:
                lang[i.show_name] = ""
                movieformat[i.show_name] = ""
                movierating[i.show_name] = []
            for i in shows1:
                if i.language not in lang[i.show_name]:
                    lang[i.show_name] = lang[i.show_name] + i.language + " "
                if i.format not in movieformat[i.show_name] and i.date >= d1:
                        movieformat[i.show_name] = movieformat[i.show_name] + i.format + " "
                if i.show_rating != None:
                    movierating[i.show_name].append(i.show_rating)
            for i in movierating:
                if len(movierating[i]) != 0:
                    movierating[i] = sum(movierating[i])/len(movierating[i])

            venues = venue.query.all()
            locset = set()
            for i in venues:
                locset.add(i.city)
            setval = 0
            searchlocation = ""
            return render_template("userhomepage.html" , username = username , email= email , venues = venues , shows = shows , lang = lang , movieformat = movieformat , locset = locset , setval = setval , searchlocation = searchlocation , t1 = t1 , d1 = d1 , movierating = movierating)
        else:
            i = 1
            return render_template("userlogin.html" , i=i , email = email)



@app.route("/adminlogin" , methods = ["GET" , "POST"])

def adminlogin():
    if request.method == "GET" :
        return render_template("adminlogin.html")
    
    if request.method == "POST" :
        email = request.form["email"]
        
        logincheck = admin.query.filter(admin.email == email).first()
        if logincheck and password_decrypt(logincheck.password):
            username = logincheck.username
            venues = venue.query.filter(venue.admin_email == email).all()
            shows = show.query.all()
            return render_template("adminhomepage.html" , username = username , email = email , venues = venues , shows = shows)
        
        else:
            i = 1
            return render_template("adminlogin.html" , i=i)
    


@app.route("/usersignup" , methods = ["GET" , "POST"])

def usersignup():
    if request.method == "GET" :
        return render_template("usersignup.html")
    
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        emailcheck = user.query.filter(user.email == email).first()
        if emailcheck:
            return render_template("usersignup.html" , emailcheck = emailcheck)
        
        else:
            userdetails = user(username = username , email = email , password = password_encrypt(password))
            db.session.add(userdetails)
            db.session.commit()
            name = user.query.filter(user.email == email).first()
            username = name.username
            d1 = datetime.today().strftime("%Y-%m-%d")
            IST = pytz.timezone('Asia/Kolkata')
            t1 = datetime.now(IST).strftime('%H:%M')
            shows = show.query.with_entities(show.show_name , show.genre , show.date , show.time).filter(show.date >= d1).distinct().all()
            shows1 = show.query.filter(show.date >= d1).distinct().all()
            shows2 = show.query.distinct().all()
            rate = bookings.query.all()
            bookingrating = {}
            for i in rate :
                bookingrating[i.show_id] = []
                
            for i in rate :
                if i.rating != None :
                    bookingrating[i.show_id].append(i.rating)
            for i in bookingrating :
                if len(bookingrating[i]) != 0:
                    bookingrating[i] = sum(bookingrating[i])/len(bookingrating[i])
            
            for i in shows2:
                if i.show_id in bookingrating and bookingrating[i.show_id] != []:
                    i.show_rating = bookingrating[i.show_id]
            db.session.commit()
            
            lang = {}
            movieformat = {}
            movierating = {}


            for i in shows1:
                lang[i.show_name] = ""
                movieformat[i.show_name] = ""
                movierating[i.show_name] = []
            for i in shows1:
                if i.language not in lang[i.show_name]:
                    lang[i.show_name] = lang[i.show_name] + i.language + " "
                if i.format not in movieformat[i.show_name] and i.date >= d1:
                        movieformat[i.show_name] = movieformat[i.show_name] + i.format + " "
                if i.show_rating != None:
                    movierating[i.show_name].append(i.show_rating)
            for i in movierating:
                if len(movierating[i]) != 0:
                    movierating[i] = sum(movierating[i])/len(movierating[i])

            venues = venue.query.all()
            locset = set()
            for i in venues:
                locset.add(i.city)
            setval = 0
            searchlocation = ""
            return render_template("userhomepage.html" , username = username , email= email , venues = venues , shows = shows , lang = lang , movieformat = movieformat , locset = locset , setval = setval , searchlocation = searchlocation , t1 = t1 , d1 = d1 , movierating = movierating)




@app.route("/adminsignup" , methods = ["GET" , "POST"])

def adminsignup():
    if request.method == "GET" :
        return render_template("adminsignup.html")
    
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        emailcheck = admin.query.filter(admin.email == email).first()
        if emailcheck:
            return render_template("adminsignup.html" , emailcheck = emailcheck)
        
        else:
            admindetails = admin(username = username , email = email , password = password_encrypt(password))
            db.session.add(admindetails)
            db.session.commit()
            venues = venue.query.filter(venue.admin_email == email).all()
            shows = show.query.all()
            return render_template("adminhomepage.html" , venues = venues , username = username , email = email , shows = shows)
        
    
@app.route('/user/<string:email>/home' , methods = ["GET" , "POST"])

def userhome(email):
    if request.method == "GET" :
        name = user.query.filter(user.email == email).first()
        username = name.username
        d1 = datetime.today().strftime("%Y-%m-%d")
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        shows = show.query.with_entities(show.show_name , show.genre , show.date , show.time).filter(show.date >= d1).distinct().all()
        shows1 = show.query.filter(show.date >= d1).distinct().all()
        shows2 = show.query.distinct().all()
        rate = bookings.query.all()
        bookingrating = {}
        for i in rate :
            bookingrating[i.show_id] = []
            
        for i in rate :
            if i.rating != None :
                bookingrating[i.show_id].append(i.rating)
        for i in bookingrating :
            if len(bookingrating[i]) != 0:
                bookingrating[i] = sum(bookingrating[i])/len(bookingrating[i])
        
        for i in shows2:
            if i.show_id in bookingrating and bookingrating[i.show_id] != []:
                i.show_rating = bookingrating[i.show_id]
        db.session.commit()
        
        lang = {}
        movieformat = {}
        movierating = {}


        for i in shows1:
            lang[i.show_name] = ""
            movieformat[i.show_name] = ""
            movierating[i.show_name] = []
        for i in shows1:
            if i.language not in lang[i.show_name]:
                lang[i.show_name] = lang[i.show_name] + i.language + " "
            if i.format not in movieformat[i.show_name] and i.date >= d1:
                    movieformat[i.show_name] = movieformat[i.show_name] + i.format + " "
            if i.show_rating != None:
                movierating[i.show_name].append(i.show_rating)
        for i in movierating:
            if len(movierating[i]) != 0:
                movierating[i] = sum(movierating[i])/len(movierating[i])

        venues = venue.query.all()
        locset = set()
        for i in venues:
            locset.add(i.city)
        setval = 0
        searchlocation = ""
        return render_template("userhomepage.html" , username = username , email= email , venues = venues , shows = shows , lang = lang , movieformat = movieformat , locset = locset , setval = setval , searchlocation = searchlocation , t1 = t1 , d1 = d1 , movierating = movierating)
    
    if request.method == "POST" :
        searchname = request.form["movie"]
        searchlocation = request.form["selectcity"]
        setval = 2
        if searchlocation != '':
            setval = 1
        name = user.query.filter(user.email == email).first()
        username = name.username
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        d1 = datetime.today().strftime("%Y-%m-%d")
        if searchname == "" and searchlocation == "":
            shows = show.query.with_entities(show.show_name , show.genre , show.date , show.time).filter(show.date >= d1).distinct().all()
            shows1 = show.query.filter(show.date >= d1).distinct().all()
        elif searchname != "" and searchlocation == "":
            shows = show.query.with_entities(show.show_name , show.genre , show.date , show.time).filter(show.date >= d1 , show.show_name == searchname.title()).distinct().all()
            shows1 = show.query.filter(show.date >= d1 , show.show_name == searchname.title()).distinct().all()
        elif searchname == "" and searchlocation != "":
            shows = show.query.join(venue).with_entities(show.show_name , show.genre , show.date , show.time).filter(show.venue_id == venue.venue_id , show.date >= d1 , venue.city == searchlocation.title()).distinct().all()
            shows1 = show.query.filter(show.venue_id == venue.venue_id , show.date >= d1 , venue.city == searchlocation.title()).distinct().all()
        else :
            shows = show.query.join(venue).with_entities(show.show_name , show.genre , show.date, show.time).filter(show.venue_id == venue.venue_id , show.date >= d1 , show.show_name == searchname.title() , venue.city == searchlocation.title()).distinct().all()
            shows1 = show.query.join(venue).filter(show.venue_id == venue.venue_id , show.date >= d1 , show.show_name == searchname.title() , venue.city == searchlocation.title()).distinct().all()
        
        shows2 = show.query.distinct().all()
        rate = bookings.query.all()
        bookingrating = {}
        for i in rate :
            bookingrating[i.show_id] = []
            
        for i in rate :
            if i.rating != None :
                bookingrating[i.show_id].append(i.rating)
        for i in bookingrating :
            if len(bookingrating[i]) != 0:
                bookingrating[i] = sum(bookingrating[i])/len(bookingrating[i])
        
        for i in shows2:
            if i.show_id in bookingrating and bookingrating[i.show_id] != []:
                i.show_rating = bookingrating[i.show_id]
        db.session.commit()
        
        lang = {}
        movieformat = {}
        movierating = {}


        for i in shows1:
            lang[i.show_name] = ""
            movieformat[i.show_name] = ""
            movierating[i.show_name] = []
        for i in shows1:
            if i.language not in lang[i.show_name]:
                lang[i.show_name] = lang[i.show_name] + i.language + " "
            if i.format not in movieformat[i.show_name] and i.date >= d1:
                    movieformat[i.show_name] = movieformat[i.show_name] + i.format + " "
            if i.show_rating != None:
                movierating[i.show_name].append(i.show_rating)
        for i in movierating:
            if len(movierating[i]) != 0:
                movierating[i] = sum(movierating[i])/len(movierating[i])

        venues = venue.query.all()
        locset = set()
        for i in venues:
            locset.add(i.city)
        i = 0
        if not shows or not venues:
            i = 1
        return render_template("userhomepage.html" , username = username , email= email , venues = venues , shows = shows , lang = lang , movieformat = movieformat , searchname = searchname , searchlocation = searchlocation , i = i , locset = locset , setval = setval , t1 = t1 , d1 = d1 , movierating = movierating)




@app.route('/admin/<string:email>/home' , methods = ["GET" , "POST"])
def adminhome(email):
    if request.method == "GET" :
        name = admin.query.filter(admin.email == email).first()
        username = name.username
        venues = venue.query.filter(venue.admin_email == email).all()
        shows = show.query.all()
        return render_template("adminhomepage.html" , venues = venues , username = username, email=email , shows = shows)
    
    if request.method == "POST":
        name = admin.query.filter(admin.email == email).first()
        username = name.username
        venues = venue.query.filter(venue.admin_email == email).all()
        return render_template("adminhomepage.html" , email = email , username = username)
    


@app.route('/admin/<string:email>/venue' , methods = ["GET" , "POST"])

def adminvenue(email):
    if request.method == "GET" :
        return render_template("venue.html" , email=email)
    if request.method == "POST":
        try :
            venueid = request.form["venueid"]
            venuename = request.form["venuename"]
            location = request.form["location"].title()
            address = request.form["address"]
            city = request.form["city"]
            state = request.form["state"]
            emailid = email
            venuedetails = venue(venue_id = venueid , venue_name = venuename , location = location , address = address , city = city , state = state , admin_email = emailid)
            db.session.add(venuedetails)
            db.session.commit()
            venues = venue.query.filter(venue.admin_email == email).all()
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            shows = show.query.all()
            return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows)
        except exc.SQLAlchemyError:
            i = 1
            return render_template("venue.html" , i = i)




@app.route('/admin/<string:email>/<string:venueid>/show' , methods = ["GET" , "POST"])

def addshow(email,venueid):
    if request.method == "GET":
        return render_template("show.html" , venueid = venueid , email = email)
    
    if request.method == "POST":
        showname = request.form["showname"].title()
        capacity = request.form["capacity"]
        time1 = request.form["time"]
        date1 = request.form["date"]
        screen = request.form["screen"]
        filmcertificate = request.form["filmcertificate"].upper()
        genre = request.form["genre"].title()
        price = request.form["price"]
        format = request.form["format"].upper()
        language = request.form["language"].title()
        d1 = datetime.today().strftime("%Y-%m-%d")
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        if d1 > date1 or ((t1[0:2] <= '12' and time1[0:2] <= '12') or(t1[0:2] > '12' and time1[0:2] > '12')) and t1 > time1:
            i = 1
            return render_template("show.html" , venueid = venueid , email=email , i=i)
        if d1 == date1 and t1[0:2] > time1[0:2]:
            i = 1
            return render_template("show.html" , venueid = venueid , email=email , i=i)
        elif filmcertificate not in ['U/A' , 'U' , 'A' , 'S']:
            i = 3
            return render_template("show.html" , venueid = venueid , email=email , i=i)
        else:
            for i in language.split(','):
                for j in format.split(','):
                    showdetails = show(show_name = showname , capacity = capacity , time = time1 , date = date1 , screen = screen , venue_id = venueid , film_certificate = filmcertificate , genre = genre ,price = price , format = j , language = i)
                    db.session.add(showdetails)
            db.session.commit()
            venues = venue.query.filter(venue.admin_email == email).all()
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            shows = show.query.all()
            return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows)




@app.route('/admin/<string:email>/<string:venueid>/view' , methods = ["GET" , "POST"])

def showdetails(email,venueid):
    if request.method == "GET":
        d1 = datetime.today().strftime("%Y-%m-%d")
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        venues = venue.query.filter(venue.venue_id == venueid).first()
        shows = show.query.filter(show.venue_id == venueid).all()
        ratings = bookings.query.filter(bookings.venue_id == venueid).all()
        return render_template("showdetails.html" , email = email , venueid = venueid , shows = shows , venues = venues , ratings = ratings , d1 = d1 , t1 = t1)





@app.route('/admin/<string:email>/<string:venueid>/<string:showid>/updateshow' , methods = ["GET" , "POST"])

def updateshow(email,venueid,showid):
    if request.method == "GET":
        shows = show.query.filter(show.venue_id == venueid , show.show_id == showid).first()
        i=0
        return render_template("updateshow.html" , venueid = venueid , email = email , shows = shows , showid = showid , i=i)
    
    if request.method == "POST":
        shows = show.query.filter(show.venue_id == venueid , show.show_id == showid).first()
        i = 0
        if int(request.form["capacity"]) < shows.booked_seats :
            i=1
            return render_template("updateshow.html" , venueid = venueid , email = email , shows = shows , showid = showid , i=i)
        else:
            shows.capacity = request.form["capacity"]
            shows.screen = request.form["screen"]
            shows.price = request.form["price"]
            db.session.commit()
            d1 = datetime.today().strftime("%Y-%m-%d")
            IST = pytz.timezone('Asia/Kolkata')
            t1 = datetime.now(IST).strftime('%H:%M')
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            venues = venue.query.filter(venue.venue_id == venueid).first()
            shows = show.query.filter(show.venue_id == venueid).all()
            return render_template("showdetails.html" , email = email , venueid = venueid , shows = shows , username = username , venues = venues , d1 = d1 , t1 = t1)
    




@app.route('/admin/<string:email>/<string:venueid>/<string:showid>/deleteconfirm' , methods = ["GET" , "POST"])

def deleteconfirm(email,venueid,showid):
    if request.method == "GET":
        d1 = datetime.today().strftime("%Y-%m-%d")
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        shows = show.query.filter(show.venue_id == venueid , show.show_id == showid).first()
        if shows.booked_seats > 0 :
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            venues = venue.query.filter(venue.venue_id == venueid).first()
            shows = show.query.filter(show.venue_id == venueid).all()
            i = "alert"
            return render_template("showdetails.html" , email = email , venueid = venueid , shows = shows , username = username , venues = venues , i = i , t1 = t1 ,d1 = d1)

        else:
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            venues = venue.query.filter(venue.venue_id == venueid).first()
            shows = show.query.filter(show.venue_id == venueid).all()
            i = "success"
            return render_template("showdetails.html" , email = email , venueid = venueid , shows = shows , username = username , venues = venues , i = i , showid = showid , t1 = t1 , d1 = d1)
        


@app.route('/admin/<string:email>/<string:venueid>/<string:showid>/deleteshow' , methods = ["GET" , "POST"])

def deleteshow(email,venueid,showid):
    if request.method == "GET":
        d1 = datetime.today().strftime("%Y-%m-%d")
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        shows = show.query.filter(show.venue_id == venueid , show.show_id == showid).delete()
        db.session.commit()
        name = admin.query.filter(admin.email == email).first()
        username = name.username
        venues = venue.query.filter(venue.venue_id == venueid).first()
        shows = show.query.filter(show.venue_id == venueid).all()
        i = "confirmed"
        return render_template("showdetails.html" , email = email , venueid = venueid , shows = shows , username = username , venues = venues , i = i , showid = showid , t1 = t1 , d1 = d1)


@app.route('/admin/<string:email>/<string:venueid>/updatevenue' , methods = ["GET" , "POST"])

def updatevenue(email,venueid):
    if request.method == "GET":
        venues = venue.query.filter(venue.admin_email == email , venue.venue_id == venueid).first()
        return render_template("updatevenue.html" , email= email , venueid = venueid , venues = venues)
    if request.method == "POST" :
        venues = venue.query.filter(venue.admin_email == email , venue.venue_id == venueid).first()
        venues.venue_name = request.form["venuename"]
        db.session.commit()
        venues = venue.query.filter(venue.admin_email == email).all()
        name = admin.query.filter(admin.email == email).first()
        username = name.username
        shows = show.query.all()
        return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows)
    



@app.route('/admin/<string:email>/<string:venueid>/deleteconfirm' , methods = ["GET","POST"])

def deletevenueconfirm(email , venueid):
    if request.method == "GET" :
        shows = show.query.filter(show.venue_id == venueid).all()
        if len(shows) > 0:
            venues = venue.query.filter(venue.admin_email == email).all()
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            shows = show.query.all()
            i = "alert"
            return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows , i=i)
        else:
            shows = show.query.filter(show.venue_id == venueid)
            venues = venue.query.filter(venue.admin_email == email).all()
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            shows = show.query.all()
            i = 'success'
            return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows , i=i , venueid = venueid)
        



@app.route('/admin/<string:email>/<string:venueid>/deletevenue' , methods = ["GET" , "POST"])

def deletevenue(email,venueid):
    if request.method == "GET":
        venues = venue.query.filter(venue.admin_email == email , venue.venue_id == venueid).delete()
        db.session.commit()
        shows = show.query.filter(show.venue_id == venueid)
        venues = venue.query.filter(venue.admin_email == email).all()
        name = admin.query.filter(admin.email == email).first()
        username = name.username
        shows = show.query.all()
        i = 'confirmed'
        return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows , i=i , venueid = venueid)




@app.route('/admin/<string:email>/addshowhome',methods = ["GET" , "POST"])

def addshowhome(email):
    if request.method == "GET":
        venues = venue.query.filter(venue.admin_email == email).all()
        return render_template('addshow.html' , venues = venues , email = email)
    
    if request.method == "POST":
        venueslist = request.form.getlist("venueslist")
        showname = request.form["showname"].title()
        capacity = request.form["capacity"]
        time1 = request.form["time"]
        date1 = request.form["date"]
        screen = request.form["screen"]
        filmcertificate = request.form["filmcertificate"].upper()
        genre = request.form["genre"].title()
        price = request.form["price"]
        format = request.form["format"].upper()
        language = request.form["language"].title()
        d1 = datetime.today().strftime("%Y-%m-%d")
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        venues = venue.query.filter(venue.admin_email == email).all()
        if len(venueslist) == 0:
            i = 0
            return render_template("addshow.html" , email=email , i=i , venues = venues)
        if d1 > date1 or ((t1[0:2] <= '12' and time1[0:2] <= '12') or(t1[0:2] > '12' and time1[0:2] > '12')) and t1 > time1:
            i = 1
            return render_template("addshow.html" , email=email , i=i , venues = venues)
        if d1 == date1 and t1[0:2] > time1[0:2]:
            i = 1
            return render_template("addshow.html" , email=email , i=i , venues = venues)
        elif filmcertificate not in ['U/A' , 'U' , 'A' , 'S']:
            i = 3
            return render_template("addshow.html" , email=email , i=i , venues = venues)
        else:
            for k in venueslist:
                for i in language.split(','):
                    for j in format.split(','):
                        showdetails = show(show_name = showname , capacity = capacity , time = time1 , date = date1 , screen = screen , venue_id = k , film_certificate = filmcertificate , genre = genre ,price = price , format = j , language = i)
                        db.session.add(showdetails)
            db.session.commit()
            venues = venue.query.filter(venue.admin_email == email).all()
            name = admin.query.filter(admin.email == email).first()
            username = name.username
            shows = show.query.all()
            return render_template("adminhomepage.html" , venues = venues , email=email , username = username , shows = shows)
        


@app.route('/user/<string:email>/<string:showname>/<string:location>/bookshow' , methods = ["GET" , "POST"])

def bookshow(email,showname,location):
    if request.method == "GET" :
        set = 0
        f = 0
        shows = show.query.filter(show.show_name == showname).all()
        shows1 = show.query.filter(show.show_name == showname).first()
        venues = venue.query.all()
        lang = []
        movieformat = []
        date = []
        day = {}
        d1 = datetime.today().strftime("%Y-%m-%d")
        l = []
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        for i in shows:
            if i.date not in date and i.date >= d1:
                day[i.date] = ''
        for i in shows:
            if i.language not in lang:
                lang.append(i.language)
            if i.format not in movieformat:
                movieformat.append(i.format)
            if i.date not in date and i.date >= d1:
                date.append(i.date)
                x = datetime.strptime(i.date, '%Y-%m-%d').weekday()
                day[i.date] = calendar.day_name[x]
        theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 , venue.city == location).order_by(show.date).all()
        for tup in theatre:
            l.append(list(tup)[1:])
        return render_template('bookshow.html' , set = set , email = email , shows1 = shows1 , shows = shows , venues = venues , lang = lang  , movieformat = movieformat , showname = showname , date = date , day = day , l=l , f=f , t1 = t1 , d1 = d1 , location = location)


    if request.method == "POST":
        set = 0
        langu = request.form["selectlanguage"]
        format1 = request.form["selectformat"]
        time = request.form["selecttime"]
        showdate = request.form["selectdate"]
        if langu or format1 or time or showdate:
            set = 1
        shows = show.query.filter(show.show_name == showname ).all()
        shows1 = show.query.filter(show.show_name == showname ).first()
        venues = venue.query.all()
        lang = []
        movieformat = []
        date = []
        lang1 = []
        movieformat1 = []
        date1 = []
        d1 = datetime.today().strftime("%Y-%m-%d")
        day = {}
        day1 = {}
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        for i in shows:
            if i.date not in date and i.date >= d1:
                day[i.date] = ''
        for i in shows:
            if i.date not in date1 and i.date != showdate and i.date >= d1 :
                day1[i.date] = ''
        for i in shows:
            if i.language not in lang:
                lang.append(i.language)
            if i.format not in movieformat:
                movieformat.append(i.format)
            if i.date not in date and i.date >= d1:
                date.append(i.date)
                x = datetime.strptime(i.date, '%Y-%m-%d').weekday()
                day[i.date] = calendar.day_name[x]
        for i in shows:
            if i.language not in lang1 and i.language != langu:
                lang1.append(i.language)
            if i.format not in movieformat1 and i.format != format1:
                movieformat1.append(i.format)
            if i.date not in date1 and i.date != showdate and i.date >= d1 :
                date1.append(i.date)
                x = datetime.strptime(i.date, '%Y-%m-%d').weekday()
                day1[i.date] = calendar.day_name[x]
        l=[]
        f = 0
        count = 0
        if showdate != '' :
            f = 1
            theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 , show.date == showdate , venue.city == location).order_by(show.date)
            for tup in theatre:
                l.append(list(tup)[1:])
        if langu != '':
            f = 1
            if len(l) != 0:
                new = []
                for p in l:
                    if p[5] == langu:
                        new.append(p)
                l = new[:]
            else:
                count += 1
                theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 , show.language == langu , venue.city == location).order_by(show.date)
                for tup in theatre:
                    l.append(list(tup)[1:])
        if format1 != '':
            f = 1
            if len(l) != 0:
                new = []
                for p in l:
                    if p[4] == format1:
                        new.append(p)
                l = new[:]
            else:
                count += 1
                theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 , show.format == format1 , venue.city == location).order_by(show.date)
                for tup in theatre:
                    l.append(list(tup)[1:])
        if time != '' :
            f = 1
            if len(l) != 0:
                new = []
                for p in l:
                    if time[0] == 'M' and '00:00' <= p[2] <= '11:59':
                        new.append(p)
                    elif time[0] == 'A' and '12:00' <= p[2] <= '15:59' :
                        new.append(p)
                    elif time[0] == 'E' and '16:00' <= p[2] <= '18:59' :
                        new.append(p)
                    elif time[0] == 'N' and '19:00' <= p[2] <= '23:59' :
                        new.append(p)
                l = new[:]
            if count == 0 and len(l) == 0:
                if time[0] == 'M':
                    theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id  , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 ,  '00:00' <= show.time, show.time <= '11:59' , venue.city == location).order_by(show.date)
                    for tup in theatre:
                        l.append(list(tup)[1:])
                elif time[0] == 'A':
                    theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id  , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 ,  '12:00' <= show.time , show.time <= '15:59' , venue.city == location).order_by(show.date)
                    for tup in theatre:
                        l.append(list(tup)[1:])
                elif time[0] == 'E':
                    theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id  , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 ,  '16:00' <= show.time , show.time <= '18:59' , venue.city == location).order_by(show.date)
                    for tup in theatre:
                        l.append(list(tup)[1:])
                elif time[0] == 'N':
                    theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id  , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 ,  '19:00' <= show.time , show.time <= '23:59' , venue.city == location).order_by(show.date)
                    for tup in theatre:
                        l.append(list(tup)[1:])
        if f == 0:
            theatre = show.query.join(venue).add_columns(venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.booked_seats , show.capacity).filter(show.venue_id == venue.venue_id , show.show_name == showname , show.date >= d1 , venue.city == location).order_by(show.date)
            for tup in theatre:
                l.append(list(tup)[1:])
        return render_template('bookshow.html' , email = email , shows1 = shows1 , shows = shows , venues = venues , lang = lang  , movieformat = movieformat , showname = showname , set = set , langu = langu , format1 = format1 , time = time , lang1 = lang1 , movieformat1 = movieformat1 , date = date , date1 = date1 , showdate = showdate , day = day , day1 = day1 , l=l , f=f , t1 = t1 , d1 = d1 , location = location)



@app.route('/user/<string:email>/<string:showid>/<string:location>/bookticket' , methods = ["GET" , "POST"])

def bookticket(email,showid,location):
    if request.method == "GET":
        shows = show.query.join(venue).add_columns(show.show_name , venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.film_certificate , show.capacity , show.price , show.booked_seats).filter(show.show_id == showid , show.venue_id == venue.venue_id , venue.city == location).first()
        seats = ''
        totalcost = ''
        return render_template('bookticket.html' , shows = shows , email = email , showid = showid , seats = seats , totalcost = totalcost , location = location)
    

    if request.method == "POST":
        shows = show.query.join(venue).add_columns(show.show_name , venue.venue_name , show.date , show.time , venue.location , show.format , show.language , show.show_id , show.film_certificate , show.capacity , show.price , show.booked_seats).filter(show.show_id == showid , show.venue_id == venue.venue_id , venue.city == location).first()
        seats = request.form["requiredseats"]
        totalcost = int(seats)*shows.price
        if totalcost <= 0 :
            i = 2
            return render_template('bookticket.html' , email = email , showid = showid , shows = shows , totalcost = totalcost , seats = seats , i=i , location = location)
        elif int(seats) > (shows.capacity - shows.booked_seats):
            i = 1
            return render_template('bookticket.html' , email = email , showid = showid , shows = shows , totalcost = totalcost , seats = seats , i=i , location = location)
        else:
            return render_template('confirm.html' , email = email , showid = showid , shows = shows , totalcost = totalcost , seats = seats , location = location)


@app.route('/user/<string:email>/<string:showid>/<int:seats>/success' , methods = ["GET" , "POST"])

def success(email , showid , seats):
    if request.method == "GET":
        shows = show.query.filter(show.show_id == showid).first()
        bookingdetails = bookings(user_email = email , show_id = showid , venue_id = shows.venue_id , no_of_seats = seats , screen = shows.screen)
        db.session.add(bookingdetails)
        updatedseats = show.query.filter(show.show_id == showid).first()
        updatedseats.booked_seats = updatedseats.booked_seats + seats
        db.session.commit()
        return render_template('success.html', email = email)


@app.route('/user/<string:email>/mybookings' , methods = ["GET" , "POST"])

def myshows(email):
    if request.method == "GET":
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        d1 = datetime.today().strftime("%Y-%m-%d")
        months = {'01' : 'Jan' , '02' :'Feb' , '03' :'Mar' , '04' :'Apr' , '05' :'May' , '06' :'Jun' , '07' :'Jul' , '08' :'Aug' , '09' :'Sep' , '10' :'Oct' , '11' :'Nov' , '12' :'Dec'}
        name = user.query.filter(user.email == email).first()
        username = name.username
        myticket = show.query.join(venue).join(bookings).with_entities(show.film_certificate , show.date , show.time , show.show_name , venue.city , venue.location , bookings.booking_id , bookings.screen , bookings.no_of_seats , show.language , show.format , show.genre , bookings.rating).filter(bookings.show_id == show.show_id , bookings.venue_id == venue.venue_id , bookings.user_email == email).order_by(show.date , show.time).all()
        return render_template('bookings.html' , email = email , username = username , myticket = myticket , t1 = t1 , d1 = d1 , months = months)


@app.route('/user/<string:email>/mybookings/completed' , methods = ["GET" , "POST"])

def completedshows(email):
    if request.method == "GET":
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        d1 = datetime.today().strftime("%Y-%m-%d")
        months = {'01' : 'Jan' , '02' :'Feb' , '03' :'Mar' , '04' :'Apr' , '05' :'May' , '06' :'Jun' , '07' :'Jul' , '08' :'Aug' , '09' :'Sep' , '10' :'Oct' , '11' :'Nov' , '12' :'Dec'}
        name = user.query.filter(user.email == email).first()
        username = name.username
        myticket = show.query.join(venue).join(bookings).with_entities(show.film_certificate , show.date , show.time , show.show_name , venue.city , venue.location , bookings.booking_id , bookings.screen , bookings.no_of_seats , show.language , show.format , show.genre , bookings.rating).filter(bookings.show_id == show.show_id , bookings.venue_id == venue.venue_id , bookings.user_email == email).order_by(show.date , show.time).all()
        return render_template('completedbookings.html' , email = email , username = username , myticket = myticket , t1 = t1 , d1 = d1 , months = months)
    

@app.route('/user/<string:email>/mybookings/completed/<int:bookingid>/rating' , methods = ["GET" , "POST"])

def rating(email,bookingid):
    if request.method == "GET":
        IST = pytz.timezone('Asia/Kolkata')
        t1 = datetime.now(IST).strftime('%H:%M')
        d1 = datetime.today().strftime("%Y-%m-%d")
        months = {'01' : 'Jan' , '02' :'Feb' , '03' :'Mar' , '04' :'Apr' , '05' :'May' , '06' :'Jun' , '07' :'Jul' , '08' :'Aug' , '09' :'Sep' , '10' :'Oct' , '11' :'Nov' , '12' :'Dec'}
        name = user.query.filter(user.email == email).first()
        username = name.username
        myticket = show.query.join(venue).join(bookings).with_entities(show.film_certificate , show.date , show.time , show.show_name , venue.city , venue.location , bookings.booking_id , bookings.screen , bookings.no_of_seats , show.language , show.format , show.genre , bookings.rating).filter(bookings.show_id == show.show_id , bookings.venue_id == venue.venue_id , bookings.user_email == email).order_by(show.date , show.time).all()
        return render_template('completedbookings.html' , email = email , username = username , myticket = myticket , t1 = t1 , d1 = d1 , months = months)
    
    if request.method == "POST":
        rating = request.form["rate"]
        if rating == '':
            IST = pytz.timezone('Asia/Kolkata')
            t1 = datetime.now(IST).strftime('%H:%M')
            d1 = datetime.today().strftime("%Y-%m-%d")
            months = {'01' : 'Jan' , '02' :'Feb' , '03' :'Mar' , '04' :'Apr' , '05' :'May' , '06' :'Jun' , '07' :'Jul' , '08' :'Aug' , '09' :'Sep' , '10' :'Oct' , '11' :'Nov' , '12' :'Dec'}
            name = user.query.filter(user.email == email).first()
            username = name.username
            myticket = show.query.join(venue).join(bookings).with_entities(show.film_certificate , show.date , show.time , show.show_name , venue.city , venue.location , bookings.booking_id , bookings.screen , bookings.no_of_seats , show.language , show.format , show.genre , bookings.rating).filter(bookings.show_id == show.show_id , bookings.venue_id == venue.venue_id , bookings.user_email == email).order_by(show.date , show.time).all()
            return render_template('completedbookings.html' , email = email , username = username , myticket = myticket , t1 = t1 , d1 = d1 , months = months , rating = rating)

        else:
            rate  = bookings.query.filter(bookings.user_email == email , bookings.booking_id == bookingid).first()
            rate.rating = rating
            db.session.commit()
            IST = pytz.timezone('Asia/Kolkata')
            t1 = datetime.now(IST).strftime('%H:%M')
            d1 = datetime.today().strftime("%Y-%m-%d")
            months = {'01' : 'Jan' , '02' :'Feb' , '03' :'Mar' , '04' :'Apr' , '05' :'May' , '06' :'Jun' , '07' :'Jul' , '08' :'Aug' , '09' :'Sep' , '10' :'Oct' , '11' :'Nov' , '12' :'Dec'}
            name = user.query.filter(user.email == email).first()
            username = name.username
            myticket = show.query.join(venue).join(bookings).with_entities(show.film_certificate , show.date , show.time , show.show_name , venue.city , venue.location , bookings.booking_id , bookings.screen , bookings.no_of_seats , show.language , show.format , show.genre , bookings.rating).filter(bookings.show_id == show.show_id , bookings.venue_id == venue.venue_id , bookings.user_email == email).order_by(show.date , show.time).all()
            return render_template('completedbookings.html' , email = email , username = username , myticket = myticket , t1 = t1 , d1 = d1 , months = months , rating = rating)




if __name__ == '__main__' :
    app.run(
        host = '0.0.0.0',
        debug=True,
        port = 8080
        )
