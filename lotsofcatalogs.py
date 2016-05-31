from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_catalog_setup import Category, Base, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
# User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
#              picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
# session.add(User1)
# session.commit()

# Catalog and their items
# Category 1
category1 = Category(name="Surf - Pacific")

session.add(category1)
session.commit()

catalogItem1= Item(name="Surf RollaCoaster", description="Made of oak tree,"
              " this surf table will be your best friend in Hawaii.",
              category = category1)
session.add(catalogItem1)
session.commit()

catalogItem2= Item(name="Surf Hola Hola", description="Made of ceiba tree, "
              "this surf table will be your best friend in Cancun.",
              category = category1)
session.add(catalogItem2)
session.commit()

# Category 2

category2 = Category(name="BMX - Extreme")

session.add(category2)
session.commit()

catalogItem3= Item(name="Shawn Mcintosh", description="The Fit Mac V2 frame"
       " is Shawn McIntosh's signature model handmade in the USA from a butted"
       " Super Therm tubeset for maximum strength.", category = category2 )
session.add(catalogItem3)
session.commit()

catalogItem4= Item(name="Chase Element Pro Bike", description="The 2015 Chase Element"
       "Pro race bike features a 7005-T6 aluminum frame with integrated headset, 20mm"
       " Elevn PUL chromoly fork, and Chase topload stem.", category = category2)
session.add(catalogItem4)
session.commit()


print "Added catalog and catalog items!"