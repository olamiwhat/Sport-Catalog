from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, CategoryItem, Base

engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#items for Soccer
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(name="Jersey", description="Apparel worn by soccer players", category=category1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name="Soccer Ball", description="A round leather object kicked about by 22 players on a soccer field", category=category1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="cleats", description="Shoes worn by soccer players", category=category1)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(name="Short", description="Apparel worn by soccer players", category=category1)

session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(name="Shin Guard", description="Protective worn to protect the shin", category=category1)

session.add(categoryItem5)
session.commit()

#items for Tennis
category2 = Category(name="Tennis")

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(name="Racket", description="A light bat using for striking the ball", category=category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name="Overgrip", description="A thin, soft, sometimes padded layer wrapped around the tennis racket's handle", category=category2)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="Tennis Balls", description="A hollow ball made of rubber with a fuzzy covering of woven Dacron, nylon or wool", category=category2)

session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(name="Tennis Shoes", description="Tennis shoes have non-marking soles, special support for the demands of aggresive tennis movement, and comfort for the heavy lateral movement", category=category2)

session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(name="Shorts", description="Apparel worn by tennis players", category=category2)

session.add(categoryItem5)
session.commit()

print "Category Items Added!"