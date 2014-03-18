from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

import correlation

Base = declarative_base()

ENGINE = create_engine("sqlite:///ratings.db", echo=True)
Session = sessionmaker(bind=ENGINE)

session=Session()

### Class declarations go here
class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False)
	email = Column(String(64), nullable=False)
	password = Column(String(64), nullable=False)

# class Recipe(Base):
#     __tablename__ = "recipes"

#     id = Column(Integer, primary_key=True)
#     name = Column(String(300), nullable=False)
#     picture = Column(String(500), nullable=True)


# class Rating(Base):
    # __tablename__ = "ratings"

    # id = Column(Integer, primary_key=True)
    # recipe_id = Column(Integer, ForeignKey('recipes.id'))
    # user_id = Column(Integer, ForeignKey('users.id'))
    # rating = Column(Integer, nullable=False)
	
def authenticate(username, password):
    query = """SELECT id FROM Users WHERE username = ? AND password = ?""" 
    DB.execute(query, (username, password))
    row = DB.fetchone()
    if row:
        return row[0]
    else:
        return None

# def main():
#     """In case we need this for something"""
#     pass

# if __name__ == "__main__":
#     main()