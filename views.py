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
        return redirect(url_for("browse_recipes"))

    return render_template("login.html", form=form)

# TODO: Update route to /recipebox/<username> once database is fixed.
# TODO: Create template for individual recipe page once database is fixed.
@app.route("/recipebox")
def recipebox():
    return render_template("recipebox.html")

# Display (by category) all recipes in database for user browsing purposes.
@app.route("/browse_recipes")
def browse_recipes():
    categories = model.session.query(model.RecipeCategory).all()
    categorized_recipes = {}

    # Sort all recipes in database into categories
    for category in categories:
        common_category = category.common_category.name
        recipe = category.recipe
        if common_category not in categorized_recipes:
            categorized_recipes[common_category] = [recipe]
            # [[recipe], [], []]
        else:

            # For each category, evenly divide the recipes into sets of three for easier 
            # displaying purposes. Will display recipes horizontally (3 columns) for each category.
            
            curr_recipe_list = categorized_recipes[common_category]
            
            new_recipe_list = curr_recipe_list.append(recipe)

            # first_column = curr_recipe_list[0]
            # second_column = curr_recipe_list[1]
            # third_column = curr_recipe_list[2]

            # if len(second_column) < len(first_column):
            #     second_column.append(recipe)
            # elif len(third_column) < len(second_column):
            #     third_column.append(recipe)
            # else: 
            #     first_column.append(recipe)
   
    return render_template("browse_recipes.html", categorized_recipes=categorized_recipes)

@app.route("/recipe/<recipename>")
def view_recipe(recipename):
    return render_template("recipe.html", recipename = recipename)

@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug = True)