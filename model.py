from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import TINYTEXT, MEDIUMTEXT

# import correlation

Base = declarative_base()

ENGINE = create_engine("sqlite:///ratings.db", echo=True)
Session = sessionmaker(bind=ENGINE)

session=Session()

### Class declarations go here
class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False)
	email = Column(String(100), nullable=False)
	password = Column(String(64), nullable=False)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    orig_URL = Column(String(240), nullable=False)
    image_URL = Column(String(240), nullable=True)
    serving_size = Column(Integer, nullable=True)
    directions = Column(String(12000000), nullable=False)

class SavedRecipe(Base):
    __tablename__ = "savedrecipes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    rating = Column(Integer, nullable=True)

    user = relationship("User", backref=backref("savedrecipes", order_by=id))
    recipe = relationship("Recipe", backref=backref("savedrecipes", order_by=id))

class CommonIngredient(Base):
    __tablename__ = "common_ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True)
    amount = Column(String(50), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    common_ingredient_id = Column(Integer, ForeignKey('common_ingredients.id'))

    recipe = relationship("Recipe", backref=backref("recipe_ingredients", order_by=id))
    common_ingredient = relationship("CommonIngredient", backref=backref("recipe_ingredients", order_by=id))

class CommonCategory(Base):
    __tablename__ = "common_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class RecipeCategory(Base):
    __tablename__ = "recipe_categories"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    common_category_id = Column(Integer, ForeignKey('common_categories.id'))

    recipe = relationship("Recipe", backref=backref("recipe_categories", order_by=id))
    common_category = relationship("CommonCategory", backref=backref("common_categories", order_by=id))


# def main():
#     """In case we need this for something"""
#     pass

# if __name__ == "__main__":
#     main()