from flask import Flask, session, render_template, redirect, request, flash, url_for
import model

app = Flask(__name__)
app.config.from_object('config')
import forms

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

    # # category = model.session.query(model.CommonCategory).filter_by(name='desserts').first()
    # categories = model.session.query(model.RecipeCategory).all()
    # categorized_recipes = {}
    # # final_list = []
    # # category_id = category.id
    # # blahrecipes = model.session.query(model.RecipeCategory).filter_by(common_category_id=category_id).all()
    # # for blahrecipe in blahrecipes:
    # #     recipe = blahrecipe.recipe
    # #     final_list.append(recipe)
    # # categorized_recipes['desserts'] = final_list

    # # Sort all recipes in database into categories
    # for category in categories:
    #     common_category = category.common_category.name
    #     recipe = category.recipe
    #     if common_category not in categorized_recipes:
    #         categorized_recipes[common_category] =[recipe]
    #     else:
    #         categorized_recipes[common_category].append(recipe)

    # page_title = "Browse Recipes"
    # button_label = "Save to Recipe Box"
   
    return render_template("browse_recipes.html", username=username)

@app.route("/<username>/gridtest")
def gridtest(username):
  
    category = model.session.query(model.CommonCategory).filter_by(name='desserts').first()
    # categories = model.session.query(model.RecipeCategory).all()
    categorized_recipes = {}
    final_list = []
    category_id = category.id
    blahrecipes = model.session.query(model.RecipeCategory).filter_by(common_category_id=category_id).all()
    for blahrecipe in blahrecipes:
        recipe = blahrecipe.recipe
        final_list.append(recipe)
    categorized_recipes['desserts'] = final_list

    # Sort all recipes in database into categories
    # for category in categories:
    #     common_category = category.common_category.name
    # recipe = category.recipe
    # if common_category not in categorized_recipes:
    #     categorized_recipes[common_category] =[recipe]
    # else:
    #     categorized_recipes[common_category].append(recipe)

    page_title = "Browse Recipes"
    button_label = "Save to Recipe Box"
   
    return render_template("gridtest.html", username=username, categorized_recipes=categorized_recipes,
                            page_title=page_title, button_label=button_label)

def recipes_by_ingredient(ingredient):
    categorized_recipes = {}
    matching_recipes = []

    try:
        matching_common_ingredient = model.session.query(model.CommonIngredient).filter_by(name=ingredient).first()
        ingredient_id = matching_common_ingredient.id

        #use the common ingredient to find the matching recipe ingredient
        matching_recipe_ingredients = model.session.query(model.RecipeIngredient).filter_by(common_ingredient_id=ingredient_id).all()
        for recipe_ingredient in matching_recipe_ingredients:
            recipe = recipe_ingredient.recipe
            matching_recipes.append(recipe)

        #the matching recipe ingredient should have links to the recipes that contain it

        # matching_recipes = model.session.query(model.Recipe).filter_by(id=matching_recipe_ingredient.recipe_id).all()

        # Sort all queried recipes into categories.
        for recipe in matching_recipes:
            recipe_categories = model.session.query(model.RecipeCategory).filter_by(recipe_id=recipe.id).all()
            
            for category in recipe_categories:
                category_name = category.common_category.name
                if category_name not in categorized_recipes:
                    categorized_recipes[category_name] =[recipe]
                else:
                    categorized_recipes[category_name].append(recipe)
    except:
        pass

    return categorized_recipes

@app.route("/<username>/search", methods=['POST'])
def search_recipes(username): 
    # user = model.session.query(model.User).filter_by(username=username).first()
    # user_id = user.id

    searched_ingredient = request.form['searched_ingredient'].lower()
    # Edit search to look up plural/single versions of the ingredient, plus account for uppercase
    if searched_ingredient[-1] == 's':
        additional_query = searched_ingredient[:-1]
    else:
        additional_query = searched_ingredient + "s"

    categorized_recipes = recipes_by_ingredient(searched_ingredient)
    categorized_recipes_additional_query = recipes_by_ingredient(additional_query)
   
    for category in categorized_recipes:
        if category in categorized_recipes_additional_query:
            categorized_recipes_additional_query[category].extend(categorized_recipes[category])
        else:
            categorized_recipes_additional_query[category] = categorized_recipes[category]

    if categorized_recipes_additional_query == {}:
        flash("No recipes found!")

    page_title = "Search Results"
    button_label = "Save to Recipe Box"
   
    return render_template("recipe_thumbnails.html", username=username, categorized_recipes=categorized_recipes_additional_query,
                            page_title=page_title, button_label=button_label)

@app.route("/<username>/advancedsearch")
def display_advanced_search(username):
    return render_template("advancedsearch.html", username=username)

@app.route("/<username>/browse_recipes", methods=['POST'])
def save_recipes(username): 
    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

    recipes = request.form.getlist('recipe_checkbox')
    for recipe in recipes:
        recipe_id = int(recipe)

        # Only save the new recipe to the user's recipe box if it is unique (not already existing
        # in the box).
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
    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

    categorized_recipes = {}
    saved_recipes = model.session.query(model.SavedRecipe).filter_by(user_id=user_id).all()
    
    # Sort all user's recipes into categories.
    for saved_recipe in saved_recipes:
        recipe_data = saved_recipe.recipe
        recipe_categories = model.session.query(model.RecipeCategory).filter_by(recipe_id=recipe_data.id).all()
        
        for category in recipe_categories:
            category_name = category.common_category.name
            if category_name not in categorized_recipes:
                categorized_recipes[category_name] =[recipe_data]
            else:
                categorized_recipes[category_name].append(recipe_data)

    page_title = "My Recipe Box"
    button_label = "Delete"

    return render_template("recipe_thumbnails.html", username=username, categorized_recipes=categorized_recipes,
                            page_title=page_title, button_label=button_label)

@app.route("/<username>/recipebox", methods=["POST"])
def delete_recipes(username):
    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

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

    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

    ingredient_list = {}
    ingredients = model.session.query(model.RecipeIngredient).filter_by(recipe_id=recipe_id).all()
    for ingredient in ingredients:
        ingredient_name = ingredient.common_ingredient.name 
        ingredient_amount = ingredient.amount 
        ingredient_list[ingredient_name] = ingredient_amount

    category_list = ""
    recipe_categories = model.session.query(model.RecipeCategory).filter_by(recipe_id=recipe_id).all()
    for category in recipe_categories:
        category_name = category.common_category.name
        category_list += category_name + ", "

    # Remove the very last ", " from the end of the list
    new_list = category_list[:-2]

    # The variable user_rating will only have a true user rating value if the recipe was both 
    # saved in the user's recipe box and if the user has already input a rating value for that recipe.
    saved_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if saved_recipe:

        # Line breaks (\r\n) prevent proper javascript parsing when editing notes later. 
        # Solution: replace all instances of \r\n.
        notes = saved_recipe.user_notes.replace("\r\n", ' ')
        user_rating = saved_recipe.user_rating
        if not user_rating:
            user_rating = "empty"
        if not notes:
            notes = "empty"
    else:
        user_rating = "empty"
        note_list = "empty"

    processed_directions = process_directions(recipe.directions)

    return render_template("recipe.html", username=username, recipe=recipe, ingredient_list=ingredient_list, 
                           category_list=new_list, user_rating=user_rating, processed_directions=processed_directions, notes=notes)

def process_directions(directions):
    processed_directions=[]
    no_commas = " ".join(directions.split(","))
    no_tag = " ".join(no_commas.split("\n"))
    decomposed = no_tag.split(".")

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
    rating = int(request.form['rating-input-1'])
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).first()
    recipe_id = recipe.id

    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

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

    recipe_ingredients = model.session.query(model.RecipeIngredient).filter_by(recipe_id=recipe_id).all()
    for recipe_ingredient in recipe_ingredients:
        ingredient_id = recipe_ingredient.common_ingredient_id
        rated = model.session.query(model.RatedIngredient).filter_by(common_ingredient_id=ingredient_id).first()
        if rated:
            new_rating = ((rated.rating * rated.num_occurrences) + float(rating))/(rated.num_occurrences + 1)
            rated.num_occurrences += 1
            model.session.commit()
        else:
            ingredient_rating = model.RatedIngredient(user_id=user_id, common_ingredient_id=ingredient_id, rating=rating, num_occurrences=1)
            model.session.add(ingredient_rating)
            model.session.commit()

    return redirect(url_for("view_recipe", username=username, recipe_name=recipe_name))

@app.route("/<username>/save_notes/<recipe_name>", methods=["POST"])
def save_notes(username, recipe_name):
    note = request.form['note-form']
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).first()
    recipe_id=recipe.id

    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

    saved_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if saved_recipe:
        saved_recipe.user_notes = note
        model.session.commit()
        flash ("Successfully submitted your notes!")
    else:
        saved_recipe = model.SavedRecipe(user_id=user_id, recipe_id=recipe_id, user_notes=note)
        model.session.add(saved_recipe)
        model.session.commit()
        flash ("Successfully saved to your recipe box and submitted your notes!")

    return redirect(url_for("view_recipe", username=username, recipe_name=recipe_name))

@app.route("/<username>/save_individual_recipe/<recipe_name>", methods=['POST'])
def save_individual_recipe(username, recipe_name): 
    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).one()
    recipe_id=recipe.id

    # Only save the new recipe to the user's recipe box if it is unique (not already existing
    # in the box).
    
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
    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id
    
    # We will only consider recommending recipes which the user has not already rated or put in his/her recipe box.
    recipe_candidates = model.session.query(model.Recipe).all()
    candidate_ids = []
    for recipe_candidate in recipe_candidates:
        id = recipe_candidate.id
        isSaved = model.session.query(model.SavedRecipe).filter_by(recipe_id=id).first()
        if not isSaved:
            candidate_ids.append(id)

    results = []
    for candidate_id in candidate_ids:
        predicted_rating = predict_rating(candidate_id)
        if predicted_rating != "empty":
            results.append([candidate_id, predicted_rating])

    sorted_results = sorted(results, key=lambda x: x[1])

    max_display = 15
    if len(sorted_results) > max_display:
        sorted_results = sorted_results[:(max_display-1)]

    recipes = []
    for result in sorted_results:
        recipe_id = result[0]
        recipe = model.session.query(model.Recipe).filter_by(id=recipe_id).first()
        recipes.append(recipe)

    categorized_recipes = {}
    
    # Sort all user's recipes into categories.
    for recipe in recipes:
        recipe_categories = model.session.query(model.RecipeCategory).filter_by(recipe_id=recipe.id).all()
        
        for category in recipe_categories:
            category_name = category.common_category.name
            if category_name not in categorized_recipes:
                categorized_recipes[category_name] =[recipe]
            else:
                categorized_recipes[category_name].append(recipe)

    page_title = "Recommended for You"
    button_label = "Save to Recipe Box"
    
    return render_template("recipe_thumbnails.html", username=username, categorized_recipes=categorized_recipes,
                            page_title=page_title, button_label=button_label)

def predict_rating(recipe_id):
    ingredient_ratings = {}

    # Get all ingredients associated with the given recipe.
    ingredient_ids = []
    ingredients = model.session.query(model.RecipeIngredient).filter_by(recipe_id=recipe_id).all()
    for ingredient in ingredients:
        id = ingredient.common_ingredient.id
        ingredient_ids.append(id)

    # Get/derive all ratings for the ingredients.
    for ingredient_id in ingredient_ids:
        rated_ingredient = model.session.query(model.RatedIngredient).filter_by(common_ingredient_id=ingredient_id).first()
        if rated_ingredient:
            user_rating = rated_ingredient.rating
            num_occurrences = rated_ingredient.num_occurrences
        else:
            # If it is a new ingredient with no user rating, assume it has a neutral rating (3/5)
            user_rating = 3
            num_occurrences = 1
        ingredient_ratings[ingredient_id] = [user_rating, num_occurrences]

    # Calculate the average of all ingredient ratings to derive the recipe's overall rating.
    numerator = 0
    denominator = 0
    for ingredient_rating in ingredient_ratings:
        numerator += ((ingredient_ratings[ingredient_rating][0]) * (ingredient_ratings[ingredient_rating][1]))
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

if __name__ == "__main__":
    app.run(debug = True)