from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


# Create User Table
class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email= Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'email'        : self.email,
           'picture'      : self.picture,
       }

# Create Recipe categories Table
class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
    
# Create Recipes Table   
class Recipe(Base):
    __tablename__ = 'recipe'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    preparation = Column(String(850))
    ingredients = Column(Text())
    image = Column(String(250))
    # Recipe Link with Category
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    # Recipe Link with User
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'ingredients'  : self.ingredients,
           'id'           : self.id,
           'preparation'  : self.preparation,
           'image'        : self.image,
       }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
