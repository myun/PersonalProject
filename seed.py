import model
import csv

# Seeds database with recipe data scraped from BigOven.com
def load_recipes(session):
    with open("seed_data/recipes.csv") as f:
        print "I am here!"
        reader = csv.reader(f)
        for row in reader:
            ingredient_names, name, orig_URL, orig_rating, num_ratings, image_URL, directions, serving_size, ingredient_amounts, categories = row
            print "Ingredient names are:", ingredient_names
            print "Recipe name is", name
            print "Original URL is", orig_URL
            print "Image URL is", image_URL
            print "directions are", directions
            print "serving size is", serving_size
            print "ingredient amounts are", ingredient_amounts
            print "categories are", categories
            # load_common_ingredients(ingredient_names)
            # load_recipe_ingredients(name, ingredients)
            # load_common_categories(categories)
            recipe = model.Recipe(name=name,
                                  orig_site="Big Oven",
                                  orig_URL=orig_URL,
                                  orig_rating=orig_rating,
                                  num_ratings=num_ratings,
                                  image_URL=image_URL,
                                  serving_size=serving_size,
                                  directions=directions)
            model.session.add(recipe)
        model.session.commit()

def load_common_ingredients(session, ingredient_names):
    common_ingredients = []
    for ingredient in ingredient_names:
        if ingredient not in common_ingredients:
            common_ingredients.append(ingredient)
            new_ingredient = model.CommonIngredient(name=ingredient)
            session.add(new_ingredient)
    session.commit()

def load_recipe_ingredients(session, recipename, ingredients):
    recipe = session.query(model.Recipe).filter_by(name=recipename).first()
    recipe_id = recipe.id
    for ingredient in ingredients:
        ingredient_id = session.query(model.CommonIngredient).filter_by(name=ingredient).first().id
        ingredient_amount = ingredients[ingredient]
        recipe_ingredient = model.RecipeIngredient(amount=ingredient_amount,
                                                   recipe_id=recipe_id,
                                                   common_ingredient_id=ingredient_id)
        session.add(recipe_ingredient)
    session.commit()



    # name = Column(String(150), nullable=False)
    # orig_site = Column(String(150), nullable=False)
    # orig_URL = Column(String(240), nullable=False)
    # orig_rating = Column(Integer, nullable = True)
    # num_ratings = Column(Integer, nullable = True)
    # image_URL = Column(String(240), nullable=True)
    # serving_size = Column(String(100), nullable=True)
    # directions = Column(String(12000000), nullable=False)

# def load_users(session):
#     with open("seed_data/u.user") as f:
#         reader = csv.reader(f, delimiter="|")
#         for row in reader:
#             id, age, gender, occupation, zipcode = row
#             id = int(id)
#             age = int(age)
#             u = model.User(id=id,
#                            email=None,
#                            password=None,
#                            age=age,
#                            zipcode=zipcode)
#             session.add(u)
#         session.commit()

def main(session):
    load_recipes(model.session)
    # load_common_ingredients(session)

if __name__ == "__main__":
#     s=model.connect()
    main(model.session)