#!/usr/bin/python3

from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitemwithusers.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# create a state token to prevent request forgery.
# store it in the session for later validation.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    request.get_data()
    code = request.data.decode('utf-8')

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
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                           'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 100px; height: 100px; border-radius:150px;
               -webkit-border-radius: 150px;-moz-border-radius: 150px;"> """
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except getUserIDError:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# logout based on provider
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# JSON API to view all categories
@app.route('/JSON')
@app.route('/catalog/JSON')
def CategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


# JSON API to view Category Items Information
@app.route('/catalog/<category_name>/JSON')
@app.route('/catalog/<category_name>/items/JSON')
def categoryItemJSON(category_name):
    # the .ilike used here helps with case-insensitive comparisons
    # returns same result for lower/upper case entry
    category = session.query(Category).filter(
                        Category.name.ilike(category_name)).one()
    items = session.query(CategoryItem).filter_by(
                        category_id=category.id).all()
    return jsonify(categoryItem=[i.serialize for i in items])


# JSON API to view specific item Information
@app.route('/catalog/<category_name>/<item_name>/JSON')
def itemInfoJSON(category_name, item_name):
    category = session.query(Category).filter(
                        Category.name.ilike(category_name)).one()
    itemToShow = session.query(CategoryItem).filter_by(id=category.id).one()
    return jsonify(itemInfo=itemToShow.serialize)


# To get list of recently added items
def recentItems(num):
    getRecentItems = session.query(CategoryItem).order_by(
                             CategoryItem.category_id.desc()).limit(num)
    return getRecentItems


# Homepage - shows all categories in catalog
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('publiccatalog.html', categories=categories,
                               recentItems=recentItems(6))
    # renders a template from the template folder with the given context
    return render_template('catalog.html', categories=categories,
                           recentItems=recentItems(6))


# Show a category with the category items
@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/items/')
def showCategoryItem(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    creator = getUserInfo(category.user_id)
    items = session.query(CategoryItem).filter_by(
                    category_id=category.id).all()
    if 'username' not in login_session:
        return render_template('publicshowcatitem.html', items=items,
                               category=category,
                               category_name=category_name, creator=creator)
    else:
        return render_template('showcatitem.html', items=items,
                               category=category, category_name=category_name,
                               creator=creator)


# Create a new category
@app.route('/catalog/new-category/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCat = Category(name=request.form['name'],
                          user_id=login_session['user_id'])
        session.add(newCat)
        session.commit()
        flash("New Category '%s' Added!" % newCat.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')


# Edit a category
@app.route('/catalog/<category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    catToEdit = session.query(Category).filter(
                        Category.name.ilike(category_name)).one()
    category = catToEdit
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() { \
alert('You are not authorized to edit this category. \
Please create your own category in order to edit.'); \
window.location.href = '/catalog';}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            flash("Category successfully edited")
            return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category=category,
                               category_name=category_name)


# Delete a category
@app.route('/catalog/<category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    catToDelete = session.query(Category).filter(
                    Category.name.ilike(category_name)).one()
    category = catToDelete
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() { \
alert('You are not authorized to delete this category. \
Please create your own category in order to delete.'); \
window.location.href = '/catalog';}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(catToDelete)
        session.commit()
        flash("Category '%s' deleted!" % catToDelete.name)
        return redirect(url_for('showCategories'))
    return render_template('deletecategory.html', category=category,
                           category_name=category_name)


# Add new item to a category
@app.route('/catalog/<category_name>/new-item/', methods=['GET', 'POST'])
def newCategoryItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter(
                    Category.name.ilike(category_name)).one()
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert( \
'You are not authorized to add a new item to this category. \
Please create your own category to be able to add an item.'); \
window.location.href = '/catalog';}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        itemToAdd = CategoryItem(name=request.form['name'],
                                 description=request.form['description'],
                                 category_id=category.id,
                                 user_id=login_session['user_id'])
        session.add(itemToAdd)
        session.commit()
        flash("New Item '%s' Added!" % itemToAdd.name)
        return redirect(url_for('showCategoryItem',
                        category_name=category_name))
    return render_template('newcatitem.html', category=category,
                           category_name=category_name)


# Dsiplay Item
@app.route('/catalog/<category_name>/<item_name>/')
def displayCategoryItem(category_name, item_name):
    category = session.query(Category).filter(
                    Category.name.ilike(category_name)).one()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return render_template('publicdisplaycatitem.html',
                               category_name=category_name,
                               item_name=item_name, item=item)
    else:
        return render_template('displaycatitem.html',
                               category_name=category_name,
                               item_name=item_name, item=item)


# Edit a category item
@app.route('/catalog/<category_name>/<item_name>/edit/',
           methods=['GET', 'POST'])
def editCategoryItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter(
                   Category.name.ilike(category_name)).one()
    itemToEdit = session.query(CategoryItem).filter_by(name=item_name).one()
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() { \
alert('You are not authorized to edit this item. \
Please create your own category in order to edit.'); \
window.location.href = '/catalog';}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        flash("Category item successfully edited")
        return redirect(url_for('showCategoryItem',
                        category_name=category_name))
    return render_template('editcatitem.html', category_name=category_name,
                           item_name=itemToEdit.name, item=itemToEdit)


# Delete an item
@app.route('/catalog/<category_name>/<item_name>/delete/',
           methods=['GET', 'POST'])
def deleteCategoryItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter(
                           Category.name.ilike(category_name)).one()
    itemToDelete = session.query(CategoryItem).filter_by(name=item_name).one()
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() { \
alert('You are not authorized to delete this item. \
Please create your own category in order to delete.'); \
window.location.href = '/catalog';}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("'%s' successfully deleted" % itemToDelete.name)
        return redirect(url_for('showCategoryItem',
                        category_name=category_name))
    return render_template('deletecatitem.html', category_name=category_name,
                           item_name=itemToDelete.name, item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'my_super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
