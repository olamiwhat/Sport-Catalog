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

#JSON APIs to view Categories Items Information
@app.route('/category/<int:category_id>/items/JSON')
def categoryItemJSON(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(CategoryItem).filter_by(category_id=category_id).all()
	return jsonify(CategoryItem=[i.serialize for i in items])

#Homepage - shows all categories in catalog
@app.route('/')
@app.route('/categories/')
def showCategories():
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('categories.html', categories=categories) #renders a template from the template folder with the given context

#Create a new category
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
	if request.method =='POST':
		newCat = Category(name=request.form['name'])
		session.add(newCat)
		session.commit()
		flash("New Category %s Added!" % newCat.name)
		return redirect(url_for('showCategories'))
	else:
		return render_template('newcategory.html')

#Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
	catToEdit = session.query(Category).filter_by(id=category_id).one()
	category = catToEdit
	if request.method == 'POST':
		if request.form['name']:
			category.name = request.form['name']
			return redirect(url_for('showCategories'))
	else:
		return render_template('editcategory.html', category=category, category_id=category_id)

#Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
	catToDelete = session.query(Category).filter_by(id=category_id).one()
	category = catToDelete
	if request.method == 'POST':
		session.delete(catToDelete)
		session.commit()
		return redirect(url_for('showCategories'))
	return render_template('deletecategory.html', category=category, category_id=category.id)

#Show a category with the category items
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showCategoryItem(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(CategoryItem).filter_by(category_id=category_id).all()
	return render_template('showcatitem.html', items=items, category=category, category_id=category.id)

#Add new item to a category
@app.route('/category/<int:category_id>/item/new', methods=['GET','POST'])
def newCategoryItem(category_id):
	category = session.query(Category).filter_by(id=category_id).one()
	if request.method == 'POST':
		itemToAdd = CategoryItem(name=request.form['name'], description=request.form['description'], category_id=category_id)
		session.add(itemToAdd)
		session.commit()
		flash("New Item %s Added!" % itemToAdd.name)
		return redirect(url_for('showCategoryItem', category_id=category_id))
	return render_template('newcatitem.html', category=category, category_id=category.id)

#edit an item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit', methods=['GET','POST'])
def editCategoryItem(category_id, item_id):
	itemToEdit = session.query(CategoryItem).filter_by(id=item_id).one()
	category = session.query(Category).filter_by(id=category_id).one()	
	if request.method == 'POST':
		if request.form['name']:
			itemToEdit.name = request.form['name']
		if request.form['description']:
			itemToEdit.description = request.form['description']
		session.add(itemToEdit)
		session.commit()
		return redirect(url_for('showCategoryItem', category_id=category_id))
	return render_template('editcatitem.html', category_id=category_id, item=itemToEdit, item_id=item_id)

#edelete an item
@app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET','POST'])
def deleteCategoryItem(category_id, item_id):
	category = session.query(Category).filter_by(id=category_id).one()
	itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('showCategoryItem', category_id=category_id))
	return render_template('deletecatitem.html', category_id=category_id, item_id=itemToDelete.id, item=itemToDelete)

#Dsiplaying Item Description
@app.route('/category/<int:category_id>/item/<int:item_id>')
def displayCategoryItem(category_id, item_id):
	category = session.query(Category).filter_by(id=category_id).one()
	itemToShow = session.query(CategoryItem).filter_by(id=item_id).one()
	return render_template('displaycatitem.html', category_id=category_id, item=itemToShow, item_id=item_id)



if __name__ == '__main__':
  app.secret_key = 'my_super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)