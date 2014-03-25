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
    categories = model.session.query(model.RecipeCategory).all()
    categorized_recipes = {}

    # Sort all recipes in database into categories
    for category in categories:
        common_category = category.common_category.name
        recipe = category.recipe
        if common_category not in categorized_recipes:
            categorized_recipes[common_category] =[recipe]
        else:
            categorized_recipes[common_category].append(recipe)

    page_title = "Browse Recipes"
    button_label = "Save to Recipe Box"
   
    return render_template("recipe_thumbnails.html", username=username, categorized_recipes=categorized_recipes,
                            page_title=page_title, button_label=button_label)

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

    return redirect(url_for("browse_recipes", username=username))

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

# TODO: Create template for individual recipe page once database is fixed.

@app.route("/<username>/recipe/<recipe_name>")
def view_recipe(username, recipe_name):
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).one()
    recipe_id = recipe.id

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
    list = category_list[:-2]

    return render_template("recipe.html", username=username, recipe=recipe, ingredient_list=ingredient_list, 
                           category_list=list)

@app.route("/<username>/recipe/<recipe_name>", methods=["POST"])
def rate_recipe(username, recipe_name):
    # Get user rating data from form.
    rating = int(request.form['rating-input-1'])
    recipe = model.session.query(model.Recipe).filter_by(name=recipe_name).one()
    recipe_id = recipe.id

    user = model.session.query(model.User).filter_by(username=username).first()
    user_id = user.id

    saved_recipe = model.session.query(model.SavedRecipe).filter_by(user_id=user_id, recipe_id=recipe_id).one()
    saved_recipe.rating = rating
    model.session.commit()

    return redirect(url_for("view_recipe", username=username, recipe_name=recipe_name))


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug = True)