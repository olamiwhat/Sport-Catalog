from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

from flask import session as login_session
import random, string

#Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#JSON API to view all categories
@app.route('/JSON')
@app.route('/catalog/JSON')
def CategoriesJSON():
	categories = session.query(Category).all()
	return jsonify(categories=[i.serialize for i in categories])


#JSON API to view Category Items Information
@app.route('/catalog/<category_name>/JSON')
@app.route('/catalog/<category_name>/items/JSON')
def categoryItemJSON(category_name):
	#the .ilike used here helps with case-insensitive comparisons
	#so whether a category was entered with a lower or upper case returns the same result
	category = session.query(Category).filter(Category.name.ilike(category_name)).one()
	items = session.query(CategoryItem).filter_by(category_id=category.id).all()
	return jsonify(categoryItem=[i.serialize for i in items])


#JSON API to view specific item Information
@app.route('/catalog/<category_name>/<item_name>/JSON')
def itemInfoJSON(category_name, item_name):
	category = session.query(Category).filter(Category.name.ilike(category_name)).one()
	itemToShow = session.query(CategoryItem).filter_by(id=category.id).one()
	return jsonify(itemInfo=itemToShow.serialize)
	

#Homepage - shows all categories in catalog
@app.route('/')
@app.route('/catalog/')
def showCategories():
	categories = session.query(Category).order_by(asc(Category.name))
	#renders a template from the template folder with the given context
	return render_template('catalog.html', categories=categories)

#Create a new category
@app.route('/catalog/new-category/', methods=['GET','POST'])
def newCategory():
	if request.method =='POST':
		newCat = Category(name=request.form['name'])
		session.add(newCat)
		session.commit()
		flash("New Category '%s' Added!" % newCat.name)
		return redirect(url_for('showCategories'))
	else:
		return render_template('newcategory.html')

#Edit a category
@app.route('/catalog/<category_name>/edit/', methods=['GET','POST'])
def editCategory(category_name):
	catToEdit = session.query(Category).filter(Category.name.ilike(category_name)).one()
	category = catToEdit
	if request.method == 'POST':
		if request.form['name']:
			category.name = request.form['name']
			flash("Category successfully edited")
			return redirect(url_for('showCategories'))
	else:
		return render_template('editcategory.html', category=category, category_name=category_name)

#Delete a category
@app.route('/catalog/<category_name>/delete/', methods=['GET','POST'])
def deleteCategory(category_name):
	catToDelete = session.query(Category).filter(Category.name.ilike(category_name)).one()
	category = catToDelete
	if request.method == 'POST':
		session.delete(catToDelete)
		session.commit()
		flash("Category '%s' deleted!" % catToDelete.name)
		return redirect(url_for('showCategories'))
	return render_template('deletecategory.html', category=category, category_name=category_name)

#Show a category with the category items
@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/items/')
def showCategoryItem(category_name):
	category = session.query(Category).filter_by(name=category_name).one()
	items = session.query(CategoryItem).filter_by(category_id=category.id).all()
	return render_template('showcatitem.html', items=items, category=category, category_name=category_name)

#Add new item to a category
@app.route('/catalog/<category_name>/new-item/', methods=['GET','POST'])
def newCategoryItem(category_name):
	category = session.query(Category).filter(Category.name.ilike(category_name)).one()
	if request.method == 'POST':
		itemToAdd = CategoryItem(name=request.form['name'], description=request.form['description'], category_id=category.id)
		session.add(itemToAdd)
		session.commit()
		flash("New Item '%s' Added!" % itemToAdd.name)
		return redirect(url_for('showCategoryItem', category_name=category_name))
	return render_template('newcatitem.html', category=category, category_name=category_name)


#Dsiplay Item
@app.route('/catalog/<category_name>/<item_name>/')
def displayCategoryItem(category_name, item_name):
	category = session.query(Category).filter(Category.name.ilike(category_name)).one()
	item = session.query(CategoryItem).filter_by(name=item_name).one()
	return render_template('displaycatitem.html', category_name=category_name, item_name=item_name, item=item)


#edit a category item
@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET','POST'])
def editCategoryItem(category_name, item_name):
	category = session.query(Category).filter(Category.name.ilike(category_name)).one()
	itemToEdit = session.query(CategoryItem).filter_by(name=item_name).one()
	if request.method == 'POST':
		if request.form['name']:
			itemToEdit.name = request.form['name']
		if request.form['description']:
			itemToEdit.description = request.form['description']
		session.add(itemToEdit)
		session.commit()
		flash("Category item successfully edited")
		return redirect(url_for('showCategoryItem', category_name=category_name))
	return render_template('editcatitem.html', category_name=category_name, item_name=itemToEdit.name, item=itemToEdit)

#edelete an item
@app.route('/catalog/<category_name>/<item_name>/delete/', methods=['GET','POST'])
def deleteCategoryItem(category_name, item_name):
	category = session.query(Category).filter(Category.name.ilike(category_name)).one()
	itemToDelete = session.query(CategoryItem).filter_by(name=item_name).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("'%s' successfully deleted" % itemToDelete.name)
		return redirect(url_for('showCategoryItem', category_name=category_name))
	return render_template('deletecatitem.html', category_name=category_name, item_name=itemToDelete.name, item=itemToDelete)


if __name__ == '__main__':
  app.secret_key = 'my_super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)