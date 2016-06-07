from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()

# User table/class.
class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(250), nullable=False)
	last_name = Column(String(250), nullable=True)
	email = Column(String(250), nullable=False)
	picture = Column(String)

	@property
	def serialize(self):
		"""Return object data in easily serializable formart."""
		return {
		'User_id': self.id,	
		'User_name' : self.name,	
		}

# Category table/class.
class Category(Base):
	__tablename__='category'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(250), nullable=False)

	@property
	def serialize(self):
		"""Return object data in easily serializable formart."""
		return {
		'Category_id': self.id,	
		'Category_name' : self.name,		
		'Items': [i.serialize for i in self.items],		
		}

	@property
	def serializeCategoryNames(self):
		"""Return object data in easily serializable formart."""
		return {
		'Category_id': self.id,	
		'Category_name' : self.name,		
		}

# Item table/class.
class Item(Base):
	__tablename__='item'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	description = Column(String(250), nullable=False)
	user_id = Column(Integer,ForeignKey('user.id'))
	user= relationship(User, backref=backref('items', order_by=id))
	category_id = Column(Integer,ForeignKey('category.id'))
	category = relationship(Category, backref=backref('items'))

	# JSON property that returns basic Item data.
	@property
	def serialize(self):
		"""Return object data in easily serializable formart."""
		return {
		'item_id': self.id,
		'item_name' : self.name,
		'description': self.description,
		'category_id':  self.category_id,
		'user_id': self.user_id,       

		}

	# JSON property that returns basic Item data, except description field.
	@property
	def serializeItemSimple(self):
		"""Return object data in easily serializable formart."""
		return {
		'item_id': self.id,
		'item_name' : self.name,
		'category_id':  self.category_id,
		'user_id': self.user_id,       

		}

engine = create_engine('sqlite:///catalog.db')
 
Base.metadata.create_all(engine)
