from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_catalog_setup import Base, User, Item, Category
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import pickle


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Oauth routes handling.
# Create a state token to prevent request forgery.
# Store it in the sessioni for later validation.
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
	                for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)
	# return render_template('login.html')
    # return render_template('login.html')


# G connect route.
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
	    response = make_response(json.dumps('Invalid state parameter.'), 401)
	    response.headers['Content-Type'] = 'application/json'
	    return response
	# Obtain authorization code
	code = request.data

	try:
	    # Upgrade the authorization code into a credentials object
	    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
	    oauth_flow.redirect_uri = 'postmessage'
	    credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
	    response = make_response(
	        json.dumps('Failed to upgrade the authorization code.'), 401)
	    response.headers['Content-Type'] = 'application/json'
	    return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
	       % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
	    response = make_response(json.dumps(result.get('error')), 500)
	    response.headers['Content-Type'] = 'application/json'

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
	    response = make_response(
	        json.dumps("Token's user ID doesn't match given user ID."), 401)
	    response.headers['Content-Type'] = 'application/json'
	    return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != '252801180042-amf5nc4quei4qjokni865bmi9aisnbun.apps.googleusercontent.com':
	    response = make_response(
	        json.dumps("Token's client ID does not match app's."), 401)
	    print "Token's client ID does not match app's."
	    response.headers['Content-Type'] = 'application/json'
	    return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
	    response = make_response(json.dumps('Current user is already connected.'),
	                             200)
	    response.headers['Content-Type'] = 'application/json'
	    return response

	# Store the access token in the session for later use.
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output


# Home.  Display all categories with latest items.
# This page serves as the home page.
@app.route('/')
@app.route('/catalog/')
def home():
	categories = session.query(Category).all()
	items = session.query(Item).order_by(asc('id')).limit(10)

	return render_template('index.html', categories=categories, items=items)

# Show all the items in respective category.
@app.route('/catalog/<int:category_id>/items/')
def catalog_Items_All(category_id):
	allItems_Category = session.query(Item).filter_by(category_id=category_id).all()
	category = session.query(Category).filter_by(id=category_id).first()
	return render_template('category_items.html', items=allItems_Category, category_name = category.name , category_id=category.id)

# JSON that shows the categories and their items.
@app.route('/catalog.json')
def categoriesJSON():
	categories = session.query(Category).all()
	print categories

	return jsonify(Categories=[c.serialize for c in categories])

# EDIT items.
@app.route('/catalog/<int:item_id>/edit/', methods=['GET', 'POST'])
def item_Edit(item_id):

	item_tobe_Edited = session.query(Item).filter_by(id=item_id).one()
	categories = session.query(Category).all()

	if request.method == 'GET':
		return render_template('edit_item.html', item_tobe_Edited=item_tobe_Edited, 
								category_of_item=item_tobe_Edited.category_id, 
								categories=categories)

	if request.method == 'POST':
		if request.form['name']:
		    item_tobe_Edited.name = request.form['name']
		if request.form['description']:
		    item_tobe_Edited.description = request.form['description']
		if request.form['category_id']:
		    item_tobe_Edited.category_id = request.form['category_id']

        session.add(item_tobe_Edited)
        session.commit()
        flash('You successfully edited an item')
        return redirect(url_for('catalog_Items_All', 
        						category_id=item_tobe_Edited.category_id))


# Add a new catalog item.  
@app.route('/catalog/items/new/', methods=['GET', 'POST'])
def item_Add():

	categories = session.query(Category).all()

	if request.method == 'GET':
		return render_template('new_item.html', categories=categories)

	if request.method == 'POST':
		# Get all the categories to populate the drop down list.
		newItem = Item(
			name=request.form['name'], 
			description=request.form['description'],
			category_id=request.form['category_id']
			)
        session.add(newItem)
        session.commit()
        flash('You successfully added an item.')
        return redirect(url_for('catalog_Items_All', 
        						category_id=newItem.category_id))
# Delete an item.
@app.route('/catalog/<int:item_id>/delete/',  methods=['GET', 'POST'])
def item_Delete(item_id):

	if request.method =='GET':
		item_tobe_Deleted = session.query(Item).filter_by(id = item_id).one()
		item_category = session.query(Category).filter_by(id = item_tobe_Deleted.category_id).one()
		
		return render_template('delete_item.html', item = item_tobe_Deleted, item_category=item_category)

	if request.method =='POST':
		delete_item = session.query(Item).filter_by(id = item_id).one()
		item_category = session.query(Category).filter_by(id = delete_item.category_id).one()
		session.delete(delete_item)
		session.commit()
		allItems_Category = session.query(Item).filter_by(category_id=item_category.id).all()
		category = session.query(Category).filter_by(id=item_category.id).first()
		flash('You successfully deleted an item.')
		return redirect(url_for('catalog_Items_All', 
        						category_id=category.id))

# Description for item within a category.
@app.route('/catalog/<int:category_id>/<int:item_id>/')
def catalog_Items_Description(category_id, item_id):
	itemList = session.query(Item).filter_by(id = item_id, category_id = category_id).one()
	item_category = session.query(Category).filter_by(id=category_id).one()
	return render_template('item_description.html', item_description = itemList, item_category=item_category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
    app.config["JSON_SORT_KEYS"] = False

