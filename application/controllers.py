from flask import Flask, redirect, render_template, request, current_app as app, make_response,jsonify
from flask_login import login_required, current_user, login_user, logout_user
from application.models import User, db,Venue,show,Review
from application.models import booking
from datetime import datetime
@app.route('/admin')
def admin():
    return render_template('adminlogin.html')

# @app.route('/adminauth',methods=['POST'])
# def adminauth():
#     if request.method=='POST':
# @app.route('/admindasboard',methods=['GET'])
# def admindashboard():
#     if request.method=='GET':
#         venuelist=Venue.query.all()
#         return render_template('addashboard.html',venues=venuelist)
@app.route('/userlogin')
def userlogin():
	return render_template('userlogin.html')

@app.route('/login',methods=['POST','GET'])
def login():
     if request.method=='POST':
        req=request.json
        email = req["email"]
        user = User.query.filter_by(email = email).first()
        if user and user.password==req["password"] :
            # login_user(user)
            if user.isAdmin:
                
                return make_response(jsonify({"email":email,"username":user.username}),200) 
            
                
            return make_response(jsonify({"email":email,"username":user.username,"user_id":user.id}),200) 
        return make_response(jsonify({"credentials":"invalid"}),401)     
 


@app.route('/userregister', methods=['POST', 'GET'])
def userregister():
     
    if request.method == 'POST':
        req=request.json
        email = req['email']
        username = req['username']
        password = req['password']
 
        # if User.query.filter_by(email=email):
        #     return ('Email already Present')
             
        user = User(email=email, username=username, password=password, name=username,isAdmin=False)
        # user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({"email":email,"username":user.username}),200)
    
	

# @app.route('/userregister')
# def userregister():
# 	return render_template('userregister.html') 


@app.route("/", methods=["GET", "POST"])
def dashboard():
    wel={"wel": "Show-Booking"}
    return make_response(jsonify(wel),200)
    

#@app.route("/articles_by/<user_name>", methods=["GET", "POST"])
#@login_required
#def articles_by_author(user_name):
    #articles = Article.query.filter(Article.authors.any(username=user_name))
    #return render_template("articles_by_author.html", articles=articles, username=user_name)

@app.route("/getshow/",methods=['GET'])
def getshow():
   vDB=Venue.query.all()
   vdict=[]
   for thisv in vDB:
       Slist=show.query.filter_by(venue_Id=thisv.id)
       curr_venue = {"id": thisv.id,"name": thisv.name, "capacity": thisv.capacity, "place": thisv.place,"shows": []}
       for thisS in Slist:
            curr_show = {"id": thisS.id, "name": thisS.name, "ticket_price": thisS.ticket_price, "tags": thisS.tags}
            curr_venue['shows'].append(curr_show)
       vdict.append(curr_venue)
   return make_response(jsonify(vdict), 200)    

@app.route("/get_single_show/<int:show_id>",methods=['GET'])
def get_single_show(show_id):
    thisS = show.query.get_or_404(show_id)
    show_OUT = {"id": thisS.id, "name": thisS.name, "ticket_price": thisS.ticket_price, 
                "tags": thisS.tags, "start_time": thisS.startTime, 
                "end_time": thisS.endTime}
    return make_response(jsonify(show_OUT))

@app.route("/get_single_venue/<int:venue_id>",methods=['GET'])
def get_single_venue(venue_id):   
    thisV =  Venue.query.get_or_404(venue_id)
    Venue_OUT={"place": thisV.place, "name": thisV.name, 
    "capacity": thisV.capacity, "id": thisV.id}
    return make_response(jsonify(Venue_OUT))

@app.route("/create_venue",methods=['POST'])
def createVenue():
    req = request.json
    place = req['place']
    name = req['name']
    capacity = req['capacity']
    userID=req['user_ID']
    new_V = Venue(name=name, place= place, capacity=capacity, user_Id=userID)
    db.session.add(new_V)
    db.session.commit()
    return make_response(jsonify({"place": place, "name": name, "capacity": capacity, "id": new_V.id}))
@app.route("/edit_venue/<int:venue_id>/",methods=["PATCH"])
def editVenue(venue_id):
    thisV = Venue.query.get_or_404(venue_id)
    req = request.json
    if "name" in  req:
        thisV.name = req["name"]
    if "place" in req:
        thisV.address = req["place"]
    if "capacity" in req:
        thisV.capacity = req["capacity"]    
    db.session.commit()
    return make_response(jsonify({"name": thisV.name, "address": thisV.address, 
                                  "capacity": thisV.capacity, "id": thisV.id}))
@app.route("/delete_venue/<int:venue_id>/",methods=["DELETE"])
def deleteVenue(venue_id):
    thisV = Venue.query.get_or_404(venue_id)
    shows_list = show.query.all()
    bookings_list = booking.query.all()
    for thisS in shows_list:
        if thisS.venue_Id == thisV.id:
            for thisbooking in bookings_list:
                if thisbooking.show_id == thisS.id:
                    db.session.delete(thisbooking)
            db.session.delete(thisS)
    db.session.delete(thisV)
    db.session.commit()
    return make_response(jsonify({"delete": "successful"}))
@app.route("/create_show/<int:venue_id>",methods=['POST'])
def createShow(venue_id):
    req = request.json
    thisV = Venue.query.filter_by(id=venue_id).first()
    name = req['name']
    tags =  req['tags']
    ticket_price = req['ticket_price']
    userid=req['userid']
    start_time = datetime.strptime(req['start_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    end_time = datetime.strptime(req['end_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    thisS = show(name=name, tags=tags, ticket_price=ticket_price, startTime=start_time,
                     endTime=end_time, venue_Id=thisV.id,user_Id=userid,date=start_time)
    db.session.add(thisS)
    db.session.commit()
    return make_response(jsonify({"id": thisS.id, "name": thisS.name, "ticket_price": thisS.ticket_price, 
                                  "tags": thisS.tags, "starting_time": thisS.startTime,
                                    "ending_time": thisS.endTime,}))
    
@app.route("/delete_show/<int:show_id>",methods=["DELETE"])
def deleteShow(show_id):
    thisS = show.query.get_or_404(show_id)
    b_list = booking.query.all()
    for thisB in b_list:
        if thisB.show_id == thisS.id:
            db.session.delete(thisB)
    db.session.delete(thisS)
    db.session.commit()
    return make_response(jsonify({"delete": "successful"}))

@app.route("/update_show/<int:show_id>",methods=["PATCH"])
def updateShow(show_id):
    thisS = show.query.get_or_404(show_id)
    req = request.json
    if "name" in req:
        thisS.name = req['name']
    if "tags" in req:
        thisS.tags = req['tags']
    if "ticket_price" in req:
        thisS.ticket_price = req['ticket_price']
    if "startTime" in req:
        thisS.starting_time = datetime.strptime(req['startTime'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if "endTime" in req:
        thisS.ending_time = datetime.strptime(req['endTime'], '%Y-%m-%dT%H:%M:%S.%f%z')
    db.session.commit()    
    return make_response(jsonify({"id": thisS.id, "name": thisS.name, "ticket_price": thisS.ticket_price, 
                                  "tags": thisS.tags, "startTime": thisS.startTime, 
                                  "endTime": thisS.endTime, }))


@app.route("/create_new_booking/<int:show_id>",methods=["POST"])
def booking_post(show_id):
    req = request.json
    ct = req['count']
    userid=req['userid']
    nb = booking(show_id=show_id, count=int(ct), user_id=int(userid))
    thisS = show.query.get_or_404(show_id)
    db.session.add(nb)
    db.session.commit()
    return make_response(jsonify({"booking_id": nb.id, "tickets_confirmed": nb.count}))

@app.route("/mybookings/<user_id>",methods=["GET"])
def mybookings(user_id):
    bList = booking.query.filter_by(user_id=user_id)
    showlist = {}
    for thisb in bList:
        thisS = show.query.filter_by(id=thisb.show_id).first()
        thisvenue = Venue.query.filter_by(id=thisS.venue_Id).first()
        thisreview = Review.query.filter((Review.user_Id==user_id) & (Review.show_Id == thisS.id)).count()
        rated = False
        if thisreview > 0:
            rated = True
        showlist[thisb.id] = {"show": thisS.name, "starting_time": thisS.startTime,
                               "ending_time": thisS.endTime, "ticket_count": thisb.count, 
                               "total_cost": thisb.count * thisS.ticket_price, 
                               "venue": thisvenue.name, "place": thisvenue.place, "israted": rated}
    return make_response(jsonify(showlist))
@app.route("/add_a_review/<int:show_id>",methods=["POST"])
def review_show(show_id):
    req = request.json
    review = req['review']
    userid=req['userid']
    new_rating = Review(show_Id=show_id, rating=int(review), user_Id=int(userid))
    db.session.add(new_rating)
    db.session.commit()
    return make_response(jsonify({"rating": review}))

@app.route("/ratingshow/<int:show_id>/<int:user_id>/",methods=['GET','POST'])
def ratingshow(show_id,user_id):
    if request.method=='POST':
        rating=request.form['rating']
        thisrating=Review(rating=rating,show_Id=show_id,user_Id=user_id)
        db.session.add(thisrating)
        db.session.commit()
        return render_template("thanks.html")
    else :

        return render_template('rating.html',show_id=show_id,user_id=user_id)
    
@app.route('/showanalytics/<int:show_id>/',methods=['GET'])
def showanalytics(show_id):
    if request.method=='GET':
        
        rateshow= show.query.filter_by(id=show_id).first()   
        ratingslist=Review.query.all()
        ratingoutput=[0,0,0,0,0]
        for ra in ratingslist:
            if ra.show_Id==show_id:
                ratingoutput[ra.rating-1]+=1
        return make_response(jsonify({"reviews":ratingoutput,"showname":rateshow.name}))

@app.route("/search_shows",methods=['GET'])
def search_shows():
    seshow=show.query.all()
    return render_template("search.html",showlist=seshow)     

@app.route("/search",methods=['GET','POST'])
def search():
    searchtext=request.form['search']
    search = "%{}%".format(searchtext)
    showlist = show.query.filter(show.name.like(search)).all()
    showtags = show.query.filter(show.tags.like(search)).all()
    return render_template("search.html",showlist=showlist,showtags=showtags)




