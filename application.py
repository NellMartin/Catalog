﻿#!/usr/bin/python

from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_catalog_setup import Base, User, Item, Category
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Global dictionary to parse credentials for client_secrets.json file.

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Catalog'

# Connect to Database and create database session

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    """Creates a token when user visits /login URL.

    Returns:
        Renderized template login.html and the token/state
        """

    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# --- Facebook OAuth Code Handling ---

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Creates a Facebook authentication and 
       saves user information in session.

    Returns:
        Confirmation or status of user authentication.
    """

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'
                                 ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
    print 'access token received %s ' % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r'
                        ).read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r'
                            ).read())['web']['app_secret']
    url = \
        'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' \
        % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API

    userinfo_url = 'https://graph.facebook.com/v2.4/me'

    # strip expire tag from access token

    token = result.split('&')[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' \
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result

    data = json.loads(result)
    print data
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in the login_session in order to properly logout,
    # let's strip out the information before the equals sign in our token

    stored_token = token.split('=')[1]
    login_session['access_token'] = stored_token

    # Get user picture

    url = \
        'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' \
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

    # see if user exists

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += \
        ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash('Now logged in as %s' % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """ Function to disconnect Facebook authenticated user.

    Returns:
        Terminal confirmation of logged status of the user.
    """

    facebook_id = login_session['facebook_id']

    # The access token must me included to successfully logout

    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'you have been logged out'


# Function to disconnect user authenticated with Google.

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Creates a Google authentication and 
       saves user information in session.

    Returns:
        Confirmation or status of user authentication.
    """

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'
                                 ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = \
            make_response(json.dumps('Failed to upgrade the authorization code.'
                          ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.

    login_session['credentials'] = credentials.access_token  # Just add access token
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = \
            make_response(json.dumps("Token's user ID doesn't match given user ID."
                          ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token's client ID does not match app's."
                          ), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get crendentials, and validation for already signed in user.

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'
                          ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # add provider to login session

    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one.

    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += \
        ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    return output


# User Helper Functions to manage user creation, and user details access.

def createUser(login_session):
    """Creates an user in login session.
    Args:
        Login session object
    Returns:
        User identification
    """

    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Get user information from login session.

    Args: 
        User id

    Returns:
        User identification
    """

    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Creates an user in login session.
    Args:
        Email
    Returns:
        User identification or None.
    """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    """Revoke a current user's token and reset their login_session

    Returns:
        Response.
    """

    # Only disconnect a connected user.

    credentials = login_session.get('credentials')
    if credentials is None:
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':

        # For whatever reason, the given token was invalid.

        response = \
            make_response(json.dumps('Failed to revoke token for given user.'
                          , 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# --- JSON Handling ---

@app.route('/catalog.json')
def categoriesJSON():
    """JSON function

    Returns:
        Shows the categories and their items..
    """

    categories = session.query(Category).all()

    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog_categories.json')
def allcategoriesJSON():
    """JSON function

    Returns:
        Retrieves all the available categories.
    """

    categories = session.query(Category).all()

    return jsonify(Categories=[c.serializeCategoryNames for c in
                   categories])


@app.route('/catalog/home.json')
def latest_itemsJSON():
    """JSON function

    Returns:
        Searches for latest added items in home page.
    """

    items = session.query(Item).order_by(asc('id')).limit(10)

    return jsonify(Latest_Items=[i.serializeItemSimple for i in items])


@app.route('/catalog/<int:category_id>/<int:item_id>/item.json')
def itemJSON(category_id, item_id):
    """JSON function

    Returns:
        Retrieves JSON of Category Item - description - name - and creator.
    """

    single_item = session.query(Item).filter_by(id=item_id,
            category_id=category_id).one()

    return jsonify(Item=single_item.serialize)


@app.route('/catalog/<int:category_id>/category.json')
def items_each_CategoryJSON(category_id):
    """JSON function

    Returns:
        Retrieves all items in category selected.
    """

    category = session.query(Category).filter_by(id=category_id).one()

    return jsonify(category=category.serialize)


# --- Routing ALL Pages ---

# HOME page.

@app.route('/')
@app.route('/home')
def showAll():
    """Show all categories with latest items.

    Returns:
        Renderize template.
    """

    categories = session.query(Category).all()
    items = session.query(Item).order_by(asc('id')).limit(10)
    if 'username' not in login_session:
        return render_template('public_categories.html',
                               categories=categories, items=items)
    else:
        return render_template('categories.html',
                               categories=categories, items=items)


@app.route('/catalog/<int:category_id>/items/')
def catalog_Items_All(category_id):
    """Show all categories with latest items.

    Args:  
        Cateogry id.

    Returns:
        Renderize template with lists of objects.
    """

    allItems_Category = \
        session.query(Item).filter_by(category_id=category_id).all()

    category = session.query(Category).filter_by(id=category_id).first()

    # If username is not in the session, renderize public page.

    if 'username' not in login_session:
        return render_template('public_category_items.html',
                               items=allItems_Category,
                               category_name=category.name,
                               category_id=category.id)
    else:
        return render_template('category_items.html',
                               items=allItems_Category,
                               category_name=category.name,
                               category_id=category.id)


@app.route('/catalog/<int:item_id>/edit/', methods=['GET', 'POST'])
def item_Edit(item_id):
    """ Edit item in category.

    Args:  
        Item id.

    Returns:
        Renderize template with lists of objects.
    """

    item_tobe_Edited = session.query(Item).filter_by(id=item_id).one()
    categories = session.query(Category).all()
    creator = \
        session.query(User).filter_by(id=item_tobe_Edited.user_id).one()
    if 'username' not in login_session:
        return redirect('/login')

    # If user entering wasn't the one that created it, send a message
    # they cannot edit the item.

    if item_tobe_Edited.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'GET':
        return render_template('edit_item.html', item=item_tobe_Edited,
                               category_of_item=item_tobe_Edited.category_id,
                               categories=categories, creator=creator)

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


@app.route('/catalog/items/new/', methods=['GET', 'POST'])
def item_Add():
    """ Add a new item in category.

    Returns:
        Renderize template with lists of objects.
    """

    if 'username' not in login_session:
        return redirect('/login')

    categories = session.query(Category).all()

    if request.method == 'GET':
        return render_template('new_item.html', categories=categories)

    if request.method == 'POST':

        # Get all the categories to populate the drop down list

        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=login_session['user_id'])
    session.add(newItem)
    session.commit()
    flash('You successfully added an item.')
    return redirect(url_for('catalog_Items_All',
                    category_id=newItem.category_id))


@app.route('/catalog/<int:item_id>/delete/', methods=['GET', 'POST'])
def item_Delete(item_id):
    """Delete an item in category.

    Args:  
        Item id.

    Returns:
        Renderize template with lists of objects.
    """

    item_tobe_Deleted = session.query(Item).filter_by(id=item_id).one()

    if 'username' not in login_session:
        return redirect('/login')

    # User that didn't created the item cannot delete it.

    creator = getUserInfo(item_tobe_Deleted.user_id)
    item_creator = \
        session.query(User).filter_by(id=item_tobe_Deleted.user_id).one()
    if 'username' not in login_session or creator.id \
        != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()''>"

    if request.method == 'GET':

        item_category = \
            session.query(Category).filter_by(id=item_tobe_Deleted.category_id).one()

        return render_template('delete_item.html',
                               item=item_tobe_Deleted,
                               item_category=item_category)

    if request.method == 'POST':

        delete_item = session.query(Item).filter_by(id=item_id).one()
        item_category = \
            session.query(Category).filter_by(id=delete_item.category_id).one()
        session.delete(delete_item)
        session.commit()
        allItems_Category = \
            session.query(Item).filter_by(category_id=item_category.id).all()
        category = \
            session.query(Category).filter_by(id=item_category.id).first()
        flash('You successfully deleted an item.')
        return redirect(url_for('catalog_Items_All',
                        category_id=category.id))
    else:
        return redirect(url_for('catalog_Items_All',
                        category_id=category.id))


@app.route('/catalog/<int:category_id>/<int:item_id>/')
def catalog_Items_Description(category_id, item_id):
    """Description for item within a category.

    Args:  
        Category and Item id.

    Returns:
        Renderize template with lists of objects.
    """

    itemList = session.query(Item).filter_by(id=item_id,
            category_id=category_id).one()
    item_category = \
        session.query(Category).filter_by(id=category_id).one()

    creator = getUserInfo(itemList.user_id)
    item_creator = \
        session.query(User).filter_by(id=itemList.user_id).one()
    if 'username' not in login_session or creator.id \
        != login_session['user_id']:
        return render_template('public_item_description.html',
                               item=itemList,
                               item_category=item_category,
                               item_creator=item_creator)
    else:
        return render_template('item_description.html', item=itemList,
                               item_category=item_category,
                               item_creator=item_creator)


@app.route('/disconnect/')
def disconnect():
    """Disconnect - Revoke a current user's token and 
       reset their login_session
        
        Returns:
            Renderize template with lists of objects.
    """

    if 'provider' in login_session:
        print 'provider'
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully been logged out.')
        return redirect(url_for('showAll'))
    else:
        print 'not logged in'
        flash('You were not logged in')
        return redirect(url_for('showAll'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
    app.config['JSON_SORT_KEYS'] = False