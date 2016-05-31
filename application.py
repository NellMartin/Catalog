# Import libraries from Flask and SQlalchemy
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_catalog_setup import Base, Item, Category
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
	category_of_item = session.query(Category).filter_by(id=item_tobe_Edited.category_id).one()
	categories = session.query(Category).all()
	if request.method == 'GET':
		return render_template('edit_item.html', item_tobe_Edited=item_tobe_Edited, category_of_item=category_of_item, categories=categories)
	if request.method == 'POST':
		return 'Edit selected category.'

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
        return redirect(url_for('home'))
# Delete
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
		return render_template('category_items.html', items=allItems_Category, category_name = category.name , category_id=category.id)

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

