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
        model.Session.add(newuser)
        model.Session.commit()
        flash('Your account has been created!')
        # ------------------------  TODO: Update new user's homepage (where to direct user after logging in.)
        # return redirect ---------------------

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

        if not user:
            flash("Incorrect username.")
            return redirect(url_for("login"))

        # ------------------------ TODO: Encrypt user's password when account first created, decrypt when logging in.
        if user.password != password:
            flash("Incorrect password.")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)

# TODO: Update route to /recipebox/<username> once database is fixed.
# TODO: Create template for individual recipe page once database is fixed.
@app.route("/recipebox")
def recipebox():
    return render_template("recipebox.html")

@app.route("/browse_recipes")
def browse_recipes():
    return render_template("browse_recipes.html")

@app.route("/recipe/<recipename>")
def view_recipe(recipename):
    return render_template("recipe.html", recipename = recipename)

@app.route("/logout")
def logout():
    # flash("You are now logged out")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug = True)