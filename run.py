from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import hashlib
import os
app = Flask(__name__)

app.secret_key = "hello"
db_path = os.path.join(os.path.dirname(__file__), 'blog.sqlite')
db_uri = 'sqlite:///{}'.format(db_path)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db= SQLAlchemy(app)

class Users(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    full_name = db.Column("full_name", db.String(255))
    email = db.Column("email", db.String(255))
    password = db.Column("password", db.String(255))

    
class Categories(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    category_name = db.Column("category_name", db.String(255))

class Products(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer)
    category_id = db.Column("category_id", db.Integer)
    title = db.Column("title", db.String(255))
    location = db.Column("location", db.String(255))
    image_link = db.Column("image_link", db.String(255))
    description = db.Column("description", db.Text)
    price = db.Column("price", db.String(255))
    mobile = db.Column("mobile", db.String(255))


@app.context_processor
def inject_menu():

    # Fill in with your actual menu dictionary:
    categories=Categories.query.all()
    return dict(categories=categories)

@app.route("/")
def home():
    products = Products.query.all()
    return render_template("index.html", products=products)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["password"]
        user = Users.query.filter_by(email=email).first()
        userPassword = user.password
        hashedPassword = hashlib.md5(password.encode('utf8')).hexdigest()
        if(hashedPassword == userPassword):
            session["logged"] = 1
            session["user_id"] = user.id
            session["full_name"] = user.full_name
            return redirect(url_for('home'))
        else:
            flash('ლოგინი ან პაროლი არასწორია')
            return redirect(url_for('login'))
 


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form["email"]

        checkUser = Users.query.filter_by(email=email).count()
        if(checkUser != 0) :
            flash('მომხმარებელი უკვე არსებობს')
            return redirect(url_for('register'))

        password = request.form["password"]
        hashedPassword = hashlib.md5(password.encode('utf8')).hexdigest()

        full_name = request.form["full_name"]

        user = Users(email=email, full_name=full_name, password=hashedPassword)
        db.session.add(user)
        db.session.commit()
        

        flash('მომხმარებელი წარმატებით დარეგისტრილდა, გთხოვთ გაიაროთ ავტორიზაცია')
        return redirect(url_for('login'))

 


@app.route("/add-product", methods=["POST", "GET"])
def add_product():
    if request.method == "GET":

        categories = Categories.query.all()
        return render_template("add_product.html", categories=categories)
    else:
        title = request.form["title"]
        price = request.form["price"]
        description = request.form["description"]
        location = request.form["location"]
        mobile = request.form["mobile"]
        category_id = request.form["category"]
        image = request.files['image']

        image.save(os.path.join('static/product_images', image.filename))

        user_id = session['user_id']
    
        product = Products(title=title, price=price, category_id=category_id, description=description, location=location, mobile=mobile, image_link=image.filename, user_id=user_id)
        db.session.add(product)
        db.session.commit()
        print(session)
        flash('პროდუქტი წარმატებით დაემატა')

        return render_template("blank.html", message="პროდუქტი წარმატებით დაემატა")



@app.route("/logout")
def logout():
  session.pop('logged', None)
  session.pop('uesr_id', None)
  session.pop('full_name', None)
  return redirect(url_for('home'))

@app.route("/product/<id>")
def product(id):
    product = db.session.query(Products, Users, Categories
    ).filter(Products.user_id == Users.id
    ).filter(Products.category_id == Categories.id
    ).filter(Products.id == id).first()
    
    return render_template("details.html", product=product)

@app.route("/category/<id>")
def category(id):
    products = Products.query.filter_by(category_id=id).all()
    category = Categories.query.filter_by(id=id).first()
    return render_template("category.html", products=products, category=category)

@app.route("/profile")
def profile():
    user_id = session['user_id']
    user = Users.query.filter_by(id=user_id).first()
    products = Products.query.filter_by(user_id=user_id).all()

    return render_template("profile.html", user=user, products=products)

@app.route("/update-user", methods=["POST"])
def update_user():
    user_id = session['user_id']
    user = Users.query.filter_by(id=user_id).first()
    
    user.email = request.form["email"]
    user.full_name = request.form["full_name"]
    db.session.commit()
    flash('მონაცემები წარმატებით განახლდა')
    
    return redirect(url_for('profile'))

@app.route("/update-password", methods=["POST"])
def update_password():
    user_id = session['user_id']
    user = Users.query.filter_by(id=user_id).first()
    newHashed = hashlib.md5((request.form["new_password"]).encode('utf8')).hexdigest()
    currentHashed = hashlib.md5((request.form["current_password"]).encode('utf8')).hexdigest()
    if(request.form["new_password"] == request.form["new_password_confirm"]):
        if(currentHashed == user.password):
            user.password = newHashed
            
            flash("პაროლი წარმატებით განახლდა")
        else:
            flash('პაროლი არასწორია')

    else:
        flash('პაროლები ერთმანეთს არ ემთხვევა')

    db.session.commit()
    return redirect(url_for('profile'))

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    product = Products.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("edit.html", product=product)
    else:
        product.price = request.form["price"]
        product.title = request.form["title"]
        product.description = request.form["description"]
        product.category_id = request.form["category"]
        product.location = request.form["location"]
        product.mobile = request.form["mobile"]
        db.session.commit()

    flash('პროდუქტი წარმატებით განახლდა')
    return redirect(url_for('profile'))

@app.route("/delete/<id>")
def delete(id):
    product = Products.query.filter_by(id=id).delete()
    db.session.commit()
    flash('პროდუქტი წარმატებით წაიშალა')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)