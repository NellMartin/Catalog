from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_catalog_setup import Category, Base, Item, User

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
if len(session.query(User).all()) == 0:
    users = (
        {
              'username': u'Nelitza_Martin',  # id=1
              'last_name': u'Martin',
              'first_name': u'Nelitza',
              'email': u'mnelitza@gmail.com',
              'picture': u'''https://lh3.googleusercontent.com/jp09Ya_jB7Opmq_'
                     '7EMXfiA8M62UcLsCxCllvkzSSm2v6LA71ipwv-NwtmVhm4xqkPunRCSS3Aw=w1366-h768-rw-no'''
        },
    )

    for u in users:
        user = User(username=u['username'],
                    last_name=u['last_name'],
                    first_name=u['first_name'],
                    email=u['email'],
                    picture=u['picture'])
        session.add(user)
    session.commit()

# Populate into database all the pre-fixed categories.
if len(session.query(Category).all()) == 0:

    categories = (
        {
            'name': u'BMX'  # id=1
        },
        {
            'name': u'Caribbean Surf'  # id=2
        },
        {
            'name': u'Snowboard'  # id=3
        },
        {
            'name': u'Skateboarding'  # id=4
        },
        {
            'name': u'Sky-Diving'  # id=5
        }
    )

    for each in categories:
        category = Category(name=each['name'])
        session.add(category)
    session.commit()

# Add items to respective categories

if len(session.query(Item).all()) == 0:
    # Add some items as fixtures to start with
    items = (
        {
            'name': u'2015 Cult Hawk Sig Bike',
            'description': (
                u'''The 2015 Cult Hawk Sig bike is Chase Hawk's signature
                 model featuring a full chromoly frame with integrated 
                 headtube, chromoly fork, Cult Salvation topload stem, 9"
                  chromoly bars, Cult Faith grips made by ODI in the USA, 
                  alloy U-brake and lever, removable brake mounts, 3-pc 
                  heat-treated chromoly cranks with sealed Mid BB, 25T 
                  Cult Member style alloy sprocket, 14mm sealed cassette 
                  hub with 9T driver, 3/8" sealed FA front hub, 36H 
                  single-wall front and double-wall rear rims, 2.4" 
                  Odyssey Hawk tires, Cult 510 chain, Cult Tripod seat 
                  and Cult PC pedals.'''),
            'category_id': 1,
            'user_id': 1
        },
        {
            'name': u'2015  Redline Flight Pro Bike',
            'description': (
                u'''The 2015 Redline Flight Pro race bike features an R7 
                formed butted aluminum frame with 1-1/8" integrated headtube,
                 BOX X carbon fork, Redline Flight frontload stem, 7.5" 
                 Redline chromoly bars, Redline Flight Lock-on grips, Promax
                  V-brake and lever, 175mm Redline Flight Hollow Forged 2-pc
                   cranks with 24mm spindle and sealed BB-86 bottom bracket,
                    44T alloy 4-bolt chainring, 15mm Redline Flight sealed 
                    cassette hub with 16T cog, 3/8" Redline Flight sealed 
                    front hub, 36H Alienation Malice TCS double-wall rims, 
                    Tioga Powerband 20x1.85" front and Powerblock 1.75" rear
                    tires, Tioga D-Spyder Pivotal seat, alloy platform pedals
                     and Redline chain adjusters. (19.3 lbs w/o pedals)'''),
            'category_id': 1,
            'user_id': 1
        },
        {
            'name': u'Adventure Paddleboarding all Rounder X1 Sup',
            'description': (
                u'''As the name suggests the Adventure Paddleboarding All 
                Rounder Stand Up Paddleboard (SUP) does it all. This is a
                very functional SUP suited to flat water cruising, yet its
                  also versatile enough to take in the surf. Available in 
                  multiple sizes to suit all weight and age paddlers, this 
                  is an affordable SUP thats rich in design features and 
                  performance.'''),
            'category_id': 2,
            'user_id': 1
        },
        {
            'name': u'The Seaglass Project Albacore Finless Surfboard',
            'description': (
                u'''The Seaglass Project Albacore is the simplest finless surfboard
                 in the world. It makes the thrill of finless surfing fun, easy and
                  user friendly. The feeling the Ancient Hawaiians had as they rode
                   their finless Alaia surfboards is now more attainable to more 
                   surfers. The Albacore surfs much like a thin wood alaia because
                    of flex, yet it is soft and paddles very well and easily.'''),
            'category_id': 2,
            'user_id': 1
        },
        {
            'name': u'Lib Tech T.Rice Pro C2 BTX Snowboard - BLEM 2016',
            'description': (
                u'''C2 BTX Libs favorite camber rocker blend for aggressive power
                 snowboarders. Solid tip and tail pressure for power, pop, precision
                  and end-to-end stability combined with a medium amount of pressure
                   between your feet delivers float, carving and edge hold.'''),
            'category_id': 3,
            'user_id': 1
        },

        {
            'name': u'''Burton Custom Mystery Snowboard - BLEM 2016''',
            'description': (
                u'''Fusing the lightest core technology in the world with the highly
                 coveted Custom shape, the Burton Custom Mystery Snowboard is as much
                  a scientific breakthrough as it is a tool to ride gravity down mountains.
                   An aggressive all-mountain machine that practically levitates due to 
                   it's weight (or lack thereof), the Burton Custom Mystery Snowboard is
                    packed with new era technology that can rail down groomers and surf 
                    through powder in seamless transition. *This is a factory blem board 
                    that may have slight cosmetic damage.*'''),
            'category_id': 3,
            'user_id': 1
        },
        {
            'name': u'''Primitive Biggie Twin Towers 8.0" Skateboard Deck''',
            'description': (
                u'''Cop a juicy new board to hang on your wall as art or to skate with 
                the Primitive Biggie Twin Towers skateboard deck. A unique Biggie in 
                front of the Twin Towers graphic gives this 7-ply maple deck an iconic
                 style plus a medium concave construction to give you solid pop should
                  you decide to skate it.'''),
            'category_id': 4,
            'user_id': 1
        },
        {
            'name': u'''Primitive P-Rod Chinese New Year Red Foil 8.0" Skateboard Deck''',
            'description': (
                u'''Skate in a clean candy painted red foil deck with an embossed Primitive
                 P-Rod logo graphic and a slight concave 7-ply maple construction for 
                 durable pop.'''),
            'category_id': 4,
            'user_id': 1
        }
        
    )

    # Add all items above, 'owned' by the only user currently in the database.
    for i in items:
        item = Item(name=i['name'], description=i['description'],
                    category_id=i['category_id'], user_id=i['user_id'])
        session.add(item)
    session.commit()

print "Added catalog and catalog items!"