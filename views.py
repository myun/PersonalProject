from flask import Flask, render_template, redirect, url_for, flash, request
import forms
# import model

app = Flask(__name__)
app.config.from_object('config')

@app.route("/", methods=['GET', 'POST'])
def index():

    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username, email, password)

        # model.session.add(user)
        # model.session.commit()
        # flash('Your account has been created!')
        # return redirect

    return render_template("register.html", title = "Register", form=form)

@app.route("/login")
def login():
    form = forms.LoginForm(request.form)
    return render_template("login.html", form=form)

@app.route("/recipebox")
def recipebox():
    return render_template("recipebox.html")

@app.route("/logout")
def logout():
    # flash("You are now logged out")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug = True)