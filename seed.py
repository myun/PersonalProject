import model
import csv
import re

# Seeds database with recipe data scraped from BigOven.com
def load_recipes(session):
    with open("seed_data/recipes.csv") as f:
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
            print "original rating is ", orig_rating

            # # Process ingredient names. 
            # ingredient_names = process_ingredients(ingredient_names)

            # Process rating. Example of original format of rating: '4.5 avg'. Needs to rounded and converted to an integer for simplicity.
            rating_number = orig_rating.split()[0]
            rounded_rating = round(float(rating_number))
            orig_rating = int(rounded_rating)

            # Process number of ratings. Example of original format: '1 review(s)'. Needs to be converted to a single integer. 
            num_ratings = int(num_ratings.split()[0])

            # Convert the name, ingredient names, and directions of the recipe in case foreign characters were originally used. 
            name = name.decode("latin-1")
            ingredient_names = ingredient_names.decode("latin-1")
            directions = directions.decode("latin-1")
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

def process_ingredients(ingredient_names):
    # Example of original format of each ingredient name: '<span itemprop="name" class="name">regular <a href="/glossary/all-purpose%20flour" class="glosslink">all-purpose flour</a></span>''
    ingredient_list = []
    for ingredient in ingredient_names:
        # Extract only the text between tags '>' and '<'; results in a list of words that make up the full ingredient name
        extracted_words = re.findall(r'>[a-zA-ZS0-9() _]+<', ingredient)
        full_name = ""
        for word in extracted_words:
            word = word.strip(' ><')

            # Add all the individual words together to form the complete ingredient name
            full_name += word

            # Add a space between each word in the name
            full_name += " "

        # Leave off the trailing space after the last word when appending to the final ingredient list
        ingredient_list.append(full_name[:-1])
    return ingredient_list

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