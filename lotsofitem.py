from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, CategoryItem, User, Base

engine = create_engine('sqlite:///catalogitemwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#dummy user
User1 = User(name="John Doe", email="johndoe@mywebsite.com", picture='https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659651__340.png')
session.add(User1)
session.commit()


#items for Soccer
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Jersey", description="Apparel worn by soccer players", category=category1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Soccer Ball", description="A round leather object kicked about by 22 players on a soccer field", category=category1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="cleats", description="Shoes worn by soccer players", category=category1)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(user_id=1, name="Short", description="Apparel worn by soccer players", category=category1)

session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(user_id=1, name="Shin Guard", description="Protective worn to protect the shin", category=category1)

session.add(categoryItem5)
session.commit()

#items for Tennis
category2 = Category(user_id=1, name="Tennis")

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Racket", description="A light bat using for striking the ball", category=category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Overgrip", description="A thin, soft, sometimes padded layer wrapped around the tennis racket's handle", category=category2)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id=1, name="Tennis Balls", description="A hollow ball made of rubber with a fuzzy covering of woven Dacron, nylon or wool", category=category2)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(user_id=1, name="Tennis Shoes", description="Tennis shoes have non-marking soles, special support for the demands of aggresive tennis movement, and comfort for the heavy lateral movement", category=category2)

session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(user_id=1, name="Shorts", description="Apparel worn by tennis players", category=category2)

session.add(categoryItem5)
session.commit()

print "Category Items Added!"