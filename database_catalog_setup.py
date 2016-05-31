from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
 
Base = declarative_base()

# User table/class.
# class User(Base):
# 	__tablename__ = 'user'

# 	id = Column(Integer, primary_key=True)
# 	name = Column(String(250), nullable=False)
# 	email = Column(String(250), nullable=False)
# 	picture = Column(String(250))

# Category table/class.
class Category(Base):
	__tablename__='category'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	# user_id = Column(Integer,ForeignKey('user.id'))
	# user= relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializable formart."""
		return {
		'Category_id': self.id,	
		'Category_name' : self.name,		
		'Items': [i.serialize for i in self.items],		
		}

# Item table/class.
class Item(Base):
	__tablename__='item'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	description = Column(String(250), nullable=False)
	# user_id = Column(Integer,ForeignKey('user.id'))
	# user= relationship(User)
	category_id = Column(Integer,ForeignKey('category.id'))
	category = relationship(Category, backref=backref('items'))

	@property
	def serialize(self):
		"""Return object data in easily serializable formart."""
		return {
		'item_id': self.id,
		'item_name' : self.name,
		'description': self.description,
		}

engine = create_engine('sqlite:///catalog.db')
 
Base.metadata.create_all(engine)