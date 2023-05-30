from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms.validators import Required
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,PasswordField,
                     RadioField,SubmitField)
from wtforms.validators import InputRequired, Length,Email,URL
from wtforms import *
from flask_bootstrap import Bootstrap
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
all_books = []
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.app_context().push()
##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///my-movies-collection.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
API_key="[api_Key]"

class MovieForm(FlaskForm):
    ratings= StringField('Your rating out of 10,e.g 7.5', validators=[InputRequired()])
    rev=StringField('Your Review',validators=[InputRequired()])
    submit=SubmitField('Edit Info')

class AddForm(FlaskForm):
    add_movie=StringField('Movie Title')
    submit=SubmitField('Add movie')
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250),nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Float)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'
db.create_all()
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
lists=Movie.query.all()
movie_ranking = Movie.query.order_by(Movie.rating.asc())

@app.route("/")
def home():
    count=0
    for c in movie_ranking:
        count+=1
    for i in range(0,count):
        movie_ranking[i].ranking=count
        count-=1
    db.session.commit()
    return render_template("index.html",movies=lists,movie_ranking=movie_ranking)

@app.route("/edit/<var>",methods=['GET','POST'])
def edit(var):
    form=MovieForm()
    results = Movie.query.filter_by(id=var).first()
    print(results.rating)
    if form.validate_on_submit():
        results.rating=form.ratings.data
        results.review=form.rev.data
        try:
            db.session.commit()
        finally:
            db.session.close()
        return redirect(url_for('home'))
    return render_template("edit.html",form=form)

@app.route("/del/<int:id>")
def delete_movie(id):
    result=Movie.query.get(id)
    db.session.delete(result)
    try:
        db.session.commit()
    finally:
        db.session.close()
    return redirect(url_for('home'))

@app.route("/add",methods=['POST','GET'])
def add_movie():
    form = AddForm()
    if form.validate_on_submit():
        parameters = {
            "api_key": API_key,
            "query": f"{form.add_movie.data}",
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=parameters)
        response.raise_for_status()
        data1 = response.json()
        data = data1['results']
        movie_to_add=form.add_movie.data
        return render_template("select.html",movie=data)
    return render_template('add.html',form=form)

@app.route("/select/<int:id>")
def select(id):
    movie_id=id
    parameters = {
        "api_key": API_key,
        "id": f"{id}",
    }
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_key}&language=en-US", params=parameters)
    response.raise_for_status()
    data = response.json()
    print(data['poster_path'])
    new_book = Movie(title=data['original_title'], img_url=f"https://image.tmdb.org/t/p/original/{data['poster_path']}", year=data['release_date'],description=data['overview'])
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
