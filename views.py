from flask import Flask, session, render_template, redirect, request, flash, url_for
import model
import string

app = Flask(__name__)
app.config.from_object('config')
import forms

import random

@app.route("/", methods=['GET', 'POST'])
def index():

    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and not form.validate():
        flash ('All fields are required and passwords must match. Please try again!')
        return redirect(url_for("index"))

    elif request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Prevent users from having the same usernames; usernames should be unique.
        isExisting = model.session.query(model.User).filter_by(username=username).first()
        if isExisting:
            flash('This username already exists. Please select another one!')
            return redirect(url_for("index"))

        # Creates a new user account as long as the username is unique.
        newuser = model.User(username=username, email=email, password=password)
        model.session.add(newuser)
        model.session.commit()
        flash('Your account has been created!')
        return redirect(url_for("login"))

    return render_template("register.html", title = "Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.LoginForm(request.form)
    if request.method == 'POST' and not form.validate():
        flash("All fields are required. Please try again!")
        return redirect(url_for("login"))
    elif request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data

        user = model.session.query(model.User).filter_by(email=email).first()

        if not user or user.password != password:
            flash("Incorrect username or password. Please try again!")
            return redirect(url_for("login"))

        session['user_email'] = email
        username = user.username
        return redirect(url_for("browse_recipes", username=username))

    return render_template("login.html", form=form)

# Display (by category) all recipes in database for user browsing purposes.
@app.route("/<username>/browse_recipes")
def browse_recipes(username):
    alphabetized_recipes = []
    alphabet = string.ascii_uppercase

    # Creating bucket at index 0 for recipes that start with a number. 
    alphabetized_recipes.append({"0-9":[]})

    # Create buckets for letters a-z.
    for letter in alphabet:
        alphabetized_recipes.append({letter:[]})
    
    recipes = model.session.query(model.Recipe).all()
    for recipe in recipes:
        name = recipe.name.strip()
        first_char = name[0]
        
        # For recipes beginning with quotes, find first letter to determine which bucket to put the recipe in.
        if first_char == "\'" or first_char == "\"":
            for i in range(0, len(name)):
                if first_char not in alphabet:
                    first_char = name[i]

        # For the first letter of the name, find its corresponding index in the alphabetized_recipes list.
        # ordinal of 'A' is 65

        if first_char in alphabet:
            index = ord(first_char) - 64
            alphabetized_recipes[index][first_char].append(recipe)
        else:
            # If the first character is not in alphabet, it is a number. Put recipe into the 0-9 bucket
            index = 0
            alphabetized_recipes[index]["0-9"].append(recipe)

    return render_template("browse_recipes.html", alphabetized_recipes=alphabetized_recipes, username=username)

@app.route("/<username>/search", methods=["POST"])
def search_recipes(username): 
    search_query = request.form["search_query"].lower()

    if search_query == "":
        categorized_recipes = {}
        flash("Please enter a valid search query.")
    else:
        all_ingredient_queries = []
        all_title_queries = []

        if search_query[-1] == "s":
            single_version = search_query[:-1]
            plural_version = search_query
        else:
            single_version = search_query
            plural_version = search_query + "s"

        # Use the single (not plural) version of the search query to find related ingredients and title names. 
        # I.e. a search query of 'beef' would return both recipes containing the ingredient 'ground beef' and 
        # recipes with titles like 'beef stroganoff'.
        ingredient_results = model.session.query(model.CommonIngredient).filter(model.CommonIngredient.name.like("%" + single_version + "%")).all()
        title_results = model.session.query(model.Recipe).filter(model.Recipe.name.like("%" + single_version + "%")).all()

        categorized_ingredient_recipes = recipes_by_ingredients(ingredient_results)
        categorized_title_recipes = categorize_recipes(title_results)

        combined_recipes = combine_dictionaries(categorized_ingredient_recipes, categorized_title_recipes)

        if combined_recipes == {}:
            flash("No recipes found!")

    page_title = "Search Results: \"" + search_query + "\""
   
    return render_template("recipe_thumbnails.html", username=username, categorized_recipes=combined_recipes,
                            page_title=page_title)

def recipes_by_ingredients(ingredients):
    matching_recipes = []

    for ingredient in ingredients:
        ingredient_id = ingredient.id
        matching_recipe_ingredients = model.session.query(model.RecipeIngredient).filter_by(common_ingredient_id=ingredient_id).all()
        
        for recipe_ingredient in matching_recipe_ingredients:
            recipe = recipe_ingredient.recipe
            matching_recipes.append(recipe)

    # Sort all queried recipes into categories.
    categorized_recipes = categorize_recipes(matching_recipes)

    return categorized_recipes

@app.route("/<username>/save_recipes", methods=["POST"])
def save_recipes(username): 
    user_id = get_user_id(username)

    recipes = request.form.getlist('recipe_checkbox')
    for recipe in recipes:
        recipe_id = int(recipe)

        # Only save the new recipe to the user's recipe box if it is unique (not already existing in the box).
        try:
            model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).one()
        except:
            new_recipe = model.SavedRecipe(user_id=user_id, recipe_id=recipe_id)
            model.session.add(new_recipe)
            model.session.commit()

    flash ("Successfully saved to your recipe box!")

    return redirect(url_for("recipebox", username=username))

@app.route("/<username>/recipebox")
def recipebox(username):
    user_id = get_user_id(username)

    saved_recipes = model.session.query(model.SavedRecipe).filter_by(user_id=user_id).all()
    recipes = []
    for saved_recipe in saved_recipes:
        recipe_data = saved_recipe.recipe
        recipes.append(recipe_data)
    
    # Sort all user's recipes into categories.
    categorized_recipes = categorize_recipes(recipes)
    
    return render_template("recipebox.html", username=username, categorized_recipes=categorized_recipes)

@app.route("/<username>/recipebox", methods=["POST"])
def delete_recipes(username):
    user_id = get_user_id(username)

    recipes = request.form.getlist('recipe_checkbox')
    for recipe in recipes:
        recipe_id = int(recipe)

        new_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).one()
        model.session.delete(new_recipe)
        model.session.commit()

    flash ("Successfully deleted from your recipe box!")

    return redirect(url_for("recipebox", username=username))

@app.route("/<username>/recipe/<recipe_name>")
def view_recipe(username, recipe_name):
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).first()
    recipe_id = recipe.id
    user_id = get_user_id(username)

    ingredient_list = {}
    ingredients = model.session.query(model.RecipeIngredient).filter_by(recipe_id=recipe_id).all()
    for ingredient in ingredients:
        ingredient_name = ingredient.common_ingredient.name 
        ingredient_amount = ingredient.amount 
        ingredient_list[ingredient_name] = ingredient_amount

    category_list = get_recipe_categories(recipe_id)

    saved_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if saved_recipe:

        # Line breaks (\r\n) prevent proper javascript parsing when editing notes later, so replace all instances of \r\n.
        notes = saved_recipe.user_notes
        if notes:
            notes.replace("\r\n", ' ')
        else:
            notes = "empty"

        user_rating = saved_recipe.user_rating
        if not user_rating:
            user_rating = "empty"
    else:
        user_rating = "empty"
        notes = "empty"

    processed_directions = process_directions(recipe.directions)

    return render_template("recipe.html", username=username, recipe=recipe, ingredient_list=ingredient_list, 
                           category_list=category_list, user_rating=user_rating, processed_directions=processed_directions, notes=notes)

def get_recipe_categories(recipe_id):
    category_list = ""
    recipe_categories = model.session.query(model.RecipeCategory).filter_by(recipe_id=recipe_id).all()
    for category in recipe_categories:
        category_name = category.common_category.name
        category_list += category_name + ", "

    # Remove the very last ", " from the end of the list
    category_list = category_list[:-2]

    return category_list

def process_directions(directions):
    processed_directions=[]
    no_commas = " ".join(directions.split(","))
    no_tag = " ".join(no_commas.split("\n"))
    decomposed = no_tag.split(".")

    # For directions that are numbered.
    for i in range(0, len(decomposed)):
        curr = decomposed[i].strip()
        if curr.isdigit():
            new_line = decomposed[i].strip() + ". " 
            j = i+1
            while not decomposed[j].strip().isdigit() and j != (len(decomposed)-1):
                new_line += decomposed[j].strip() + ". "
                if j == len(decomposed)-1:
                    new_line = decomposed[j].strip()
                j += 1
            processed_directions.append(new_line)

    # For directions that are not numbered, divide into chunks of specified lengths.
    if not decomposed[0].strip().isdigit():
        max_paragraph_length = 6
        if len(no_tag) <= max_paragraph_length:
            processed_directions.append(no_tag)
        else: 
            new_line = ""
            for i in range(0, len(decomposed)):
                if i % max_paragraph_length != 0:
                    new_line += decomposed[i].strip() + ". "
                    if i == (len(decomposed)-1):
                        processed_directions.append(new_line[:-2])
                else:
                    processed_directions.append(new_line)
                    new_line = decomposed[i].strip() + ". "
                
    return processed_directions

@app.route("/<username>/recipe/<recipe_name>", methods=["POST"])
def rate_recipe(username, recipe_name):
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).first()
    recipe_id = recipe.id
    user_id = get_user_id(username)

    rating = int(request.form['rating-input-1'])
    saved_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if saved_recipe:
        if saved_recipe.user_rating:
            # Update overall rating of the recipe to take into account the user's rating.
            # Override user's last rating.
            old_rating = saved_recipe.user_rating
            # recipe = saved_recipe.recipe
            new_rating = ((recipe.orig_rating * recipe.num_ratings) - old_rating + float(rating))/(recipe.num_ratings)
            recipe.orig_rating = int(round(new_rating))
            saved_recipe.user_rating = rating
            model.session.commit()
            flash ("Successfully updated your rating!")
        
        else: 
            saved_recipe.user_rating = rating

            # Find the new rating using averages.
            new_rating = ((recipe.orig_rating * recipe.num_ratings) + float(rating))/(recipe.num_ratings + 1)
            # recipe = saved_recipe.recipe
            recipe.orig_rating = int(round(new_rating))
            recipe.num_ratings += 1
            model.session.commit()
            flash ("Successfully submitted your rating!")
    else:
        saved_recipe = model.SavedRecipe(user_id=user_id, recipe_id=recipe_id, user_rating=rating)
        model.session.add(saved_recipe)
        # recipe = saved_recipe.recipe
        new_rating = ((recipe.orig_rating * recipe.num_ratings) + float(rating))/(recipe.num_ratings + 1)
        recipe.orig_rating = int(round(new_rating))
        recipe.num_ratings += 1
        model.session.commit()
        flash ("Successfully saved to your recipe box and submitted your rating!")
    update_ingredient_ratings(rating, recipe_id, user_id)

    return redirect(url_for("view_recipe", username=username, recipe_name=recipe_name))

def update_ingredient_ratings(rating, recipe_id, user_id):
    recipe_ingredients = model.session.query(model.RecipeIngredient).filter_by(recipe_id=recipe_id).all()
    for recipe_ingredient in recipe_ingredients:
        ingredient_id = recipe_ingredient.common_ingredient_id
        rated = model.session.query(model.RatedIngredient).filter_by(common_ingredient_id=ingredient_id, user_id=user_id).first()
        if rated:
            new_rating = ((rated.rating * rated.num_occurrences) + float(rating))/(rated.num_occurrences + 1)
            rated.num_occurrences += 1
            model.session.commit()
        else:
            ingredient_rating = model.RatedIngredient(user_id=user_id, common_ingredient_id=ingredient_id, rating=rating, num_occurrences=1)
            model.session.add(ingredient_rating)
            model.session.commit()

@app.route("/<username>/save_notes/<recipe_name>", methods=["POST"])
def save_notes(username, recipe_name):
    recipe_id = get_recipe_id(recipe_name)
    user_id = get_user_id(username)

    note = request.form['note-form']
    saved_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if saved_recipe:
        saved_recipe.user_notes = note
        model.session.commit()
        flash ("Successfully submitted your notes!")
    else:
        saved_recipe = model.SavedRecipe(user_id=user_id, recipe_id=recipe_id, user_notes=note)
        model.session.add(saved_recipe)
        model.session.commit()
        flash ("Successfully saved recipe and submitted your notes!")

    return redirect(url_for("view_recipe", username=username, recipe_name=recipe_name))

@app.route("/<username>/save_individual_recipe/<recipe_name>", methods=['POST'])
def save_individual_recipe(username, recipe_name): 
    user_id = get_user_id(username)
    recipe_id = get_recipe_id(recipe_name)

    # Only save the new recipe to the user's recipe box if it is unique (not already existing in the box).
    
    isPresent = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if not isPresent:
        new_recipe = model.SavedRecipe(user_id=user_id, recipe_id=recipe_id)
        model.session.add(new_recipe)
        model.session.commit()
        flash ("Successfully saved to your recipe box!")
    else:
        flash ("Already saved in your recipe box!")

    return redirect(url_for("view_recipe", username=username, recipe_name=recipe_name))

@app.route("/<username>/suggest_recipes")
def suggest_recipes(username):
    user_id = get_user_id(username)
    
    # We will only consider recommending recipes which the user has not already rated or put in his/her recipe box.
    recipe_candidates = model.session.query(model.Recipe).all()
    candidate_ids = []
    for recipe_candidate in recipe_candidates:
        id = recipe_candidate.id
        isSaved = model.session.query(model.SavedRecipe).filter_by(recipe_id=id, user_id=user_id).first()
        if not isSaved:
            candidate_ids.append(id)

    results = []
    for candidate_id in candidate_ids:
        predicted_rating = predict_rating(user_id, candidate_id)
        if predicted_rating != "empty":
            results.append([candidate_id, predicted_rating])

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

    max_display = 15
    if len(sorted_results) > max_display:
        sorted_results = sorted_results[:(max_display)]

    recipes = []
    for result in sorted_results:
        recipe_id = result[0]
        recipe_rating = result[1]
        recipe = model.session.query(model.Recipe).filter_by(id=recipe_id).first()
        recipes.append([recipe, recipe_rating])

    button_label = "Save to Recipe Box"
    
    return render_template("suggest_recipes.html", username=username, recipes=recipes)

def predict_rating(user_id, recipe_id):
    ingredient_ratings = {}

    # Get all ingredients associated with the given recipe.
    ingredient_ids = []
    ingredients = model.session.query(model.RecipeIngredient).filter_by(recipe_id=recipe_id).all()
    for ingredient in ingredients:
        id = ingredient.common_ingredient.id
        ingredient_ids.append(id)

    # Get/derive all ratings for the ingredients.
    for ingredient_id in ingredient_ids:
        rated_ingredient = model.session.query(model.RatedIngredient).filter_by(common_ingredient_id=ingredient_id, user_id=user_id).first()
        if rated_ingredient:
            user_rating = rated_ingredient.rating
            num_occurrences = rated_ingredient.num_occurrences
        else:
            # If it is a new ingredient with no user rating, assume it has a neutral rating (3/5)
            user_rating = 3
            num_occurrences = 1
        ingredient_ratings[ingredient_id] = user_rating

    # Calculate the average of all ingredient ratings to derive the recipe's overall rating.
    numerator = 0
    denominator = 0
    for ingredient_rating in ingredient_ratings:
        numerator += ((ingredient_ratings[ingredient_rating]))
        denominator += 1

    if numerator != 0:
        recipe_rating = numerator/denominator
    else:
        recipe_rating = "empty"
    
    return recipe_rating

@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out.")
    return redirect(url_for("login"))

def get_user_id(username):
    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id
    return user_id

def get_recipe_id(recipe_name):
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).first()
    recipe_id = recipe.id
    return recipe_id

def categorize_recipes(recipes):
    categorized_recipes = {}

    for recipe in recipes:
        recipe_categories = model.session.query(model.RecipeCategory).filter_by(recipe_id=recipe.id).all()
            
        for category in recipe_categories:
            category_name = category.common_category.name
            if category_name not in categorized_recipes:
                categorized_recipes[category_name] =[recipe]
            else:
                curr = categorized_recipes[category_name]
                if recipe not in curr:
                    categorized_recipes[category_name].append(recipe)
    return categorized_recipes

# Combining two dictionaries whose values are lists
def combine_dictionaries(dict1, dict2):
    combined_dict = dict1
    for key in dict2:
        if key not in combined_dict:
            combined_dict[key] = dict2[key]
        else: 
            for val in dict2[key]:
                if val not in combined_dict[key]:
                    combined_dict[key].append(val)

    return combined_dict

if __name__ == "__main__":
    app.run(debug = True)