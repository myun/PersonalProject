import model
import csv
import re

# Keep track of all ingredients and categories present in the database as a whole.
common_ingredients = []
common_categories = []

# Seeds database with recipe data scraped from BigOven.com
def process_data(session):
    with open("seed_data/bigoven.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            ingredient_names, name, orig_URL, orig_rating, num_ratings, image_URL, directions, serving_size, ingredient_amounts, categories = row

            # Process rating. 
            orig_rating = process_rating(orig_rating)

            # Process number of ratings. Example of original format: '1 review(s)'. Needs to be converted to a single integer. 
            num_ratings = int(num_ratings.split()[0])

            # Convert the name, ingredient names, and directions of the recipe in case foreign characters were originally used. 
            name = name.decode("latin-1")
            name = name.upper()
            ingredient_names = ingredient_names.decode("latin-1")
            directions = directions.decode("latin-1")

            # Process ingredient names to remove all remaining html tags and get pure text. 
            ingredient_names = process_ingredients(ingredient_names)

            # Format ingredient amounts from string to list of strings.
            ingredient_amounts = process_ingredient_amounts(ingredient_amounts)

            # Format categories from string to list of strings.
            categories = process_categories(categories)

            if (len(ingredient_names) == len(ingredient_amounts)):
                load_recipes(session, name, orig_URL, orig_rating, num_ratings, image_URL, serving_size, directions)
                load_common_ingredients(session, ingredient_names)
                load_recipe_ingredients(session, name, ingredient_names, ingredient_amounts)
                load_common_categories(session, categories)
                load_recipes_categories(session, name, categories)

def load_recipes(session, name, orig_URL, orig_rating, num_ratings, image_URL, serving_size, directions):
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

# Example of original format of rating: '4.5 avg'. Needs to rounded and converted to an integer for simplicity.
def process_rating(orig_rating):
    rating_number = orig_rating.split()[0]
    rounded_rating = round(float(rating_number))
    orig_rating = int(rounded_rating)
    return orig_rating

def process_ingredients(ingredient_names):
    # Example of original format of each ingredient name: '<span itemprop="name" class="name">regular <a href="/glossary/all-purpose%20flour" class="glosslink">all-purpose flour</a></span>'
    formatted_ingredients = []
    unformatted_ingredients = ingredient_names.split(",")

    # Due to the formatting of the mixed html text, the following word endings are separated from their 
    # preceeding parent word (i.e. instead of "apples", may show up as "apple s" if "apple" is hyperlinked.)
    # Track these word endings for proper processing later.
    word_endings = ["s", "es", "ed", "ing"]

    for ingredient in unformatted_ingredients:
        # Extract only the text between tags '>' and '<'; results in a list of words that make up the full ingredient name
        extracted_words = re.findall(r'>[a-zA-ZS0-9() _]+<', ingredient)
        full_name = ""
        
        for word in extracted_words:
            word = word.strip(' ><')

            # Add all the individual words together to form the complete ingredient name
            full_name += word

            # Add a space between each word in the name only if appropriate.
            if word not in word_endings:
                full_name += " "

        # Leave off the trailing space after the last word when appending to the final ingredient list
        formatted_ingredients.append(full_name[:-1].lower())
    return formatted_ingredients

def process_ingredient_amounts(ingredient_amounts):
    ingredient_amount_list = ingredient_amounts.split(",")
    for ingredient_amount in ingredient_amount_list:
        ingredient_amount = ingredient_amount.strip()
    return ingredient_amount_list

def process_categories(categories):
    category_list = categories.split(",")
    for category in category_list:
        category = category.strip()
    return category_list

def load_common_ingredients(session, ingredient_names):
    global common_ingredients
    for ingredient in ingredient_names:
        if ingredient not in common_ingredients:
            common_ingredients.append(ingredient)
            new_ingredient = model.CommonIngredient(name=ingredient)
            session.add(new_ingredient)
    session.commit()

def load_recipe_ingredients(session, recipename, ingredient_names, ingredient_amounts):
    recipe = session.query(model.Recipe).filter_by(name=recipename).first()
    recipe_id = recipe.id
    for i in range(0, len(ingredient_names)):
        ingredient = ingredient_names[i]
        ingredient_id = session.query(model.CommonIngredient).filter_by(name=ingredient).first().id
        ingredient_amount = ingredient_amounts[i]
        if ingredient_amount != " ":

            # # Standardize spelling of 'tbsp' vs. 'tablespoon', 'tsp' vs. 'teaspoon', etc if they are present.
            # amount_sep= ingredient_amount.split()
            # if len(amount_sep) > 1:
            #     measurement = amount_sep[1]
            #     if measurement = "tbsp":
            #         measurement = "tablespoon"
            #     elif measurement = "c":
            #         measurement = "cup(s)"

            recipe_ingredient = model.RecipeIngredient(amount=ingredient_amount,
                                                       recipe_id=recipe_id,
                                                       common_ingredient_id=ingredient_id)
            session.add(recipe_ingredient)
        session.commit()

def load_common_categories(session, categories):
    global common_categories
    for category in categories:
        category = category.upper()
        if category not in common_categories:
            common_categories.append(category)
            new_category = model.CommonCategory(name=category)
            session.add(new_category)
    session.commit()

def load_recipes_categories(session, recipe_name, categories):
    recipe = session.query(model.Recipe).filter_by(name=recipe_name).first()
    recipe_id = recipe.id

    for category in categories:
        category = category.upper()
        category_id = session.query(model.CommonCategory).filter_by(name=category).first().id
        recipe_category = model.RecipeCategory(recipe_id=recipe_id, common_category_id=category_id)
        session.add(recipe_category)
    session.commit()

def main(session):
    process_data(model.session)

if __name__ == "__main__":
#     s=model.connect()
    main(model.session)