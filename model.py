# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import sessionmaker, scoped_session
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship, backref

# ENGINE = None
# Session = None

# Base = declarative_base()

# class User(Base):
# 	__tablename__= "users"

# 	id = Column(Integer, primary_key=True)
# 	username = Column(String(64), nullable=False)
# 	email = Column(String(64), nullable=False)
# 	password = Column(String(64), nullable=False)

# def connect():
# 	global ENGINE
# 	global Session

# 	ENGINE = create_engine("sqlite:///ratings.db", echo=True)
# 	Session = sessionmaker(bind=ENGINE)

# 	return Session()

# def main():
# 	pass

# if __name__ == "__main__":
# 	main()

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

ENGINE = None
Session = None

Base = declarative_base()

### Class declarations go here
class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False)
	email = Column(String(64), nullable=False)
	password = Column(String(64), nullable=False)

### End class declarations

def connect():
	global ENGINE
	global Session

	ENGINE = create_engine("sqlite:///ratings.db", echo=True)
	Session = sessionmaker(bind=ENGINE)

	return Session()

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()