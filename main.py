from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1NDRkYWU2ZDE1YTdjYzIxMzM5MDBjNTg0NTFlMWRhOCIsInN1YiI6IjY0ODgxMzIzOTkyNTljMDEzOTJjZDMxNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nTCDeCeM0-dzxXMPlg4dzPJb0HtgM2_181yqnOoBczI"
}
URL = "https://api.themoviedb.org/3/search/movie?query=The%20Godfather"
NEW_URL = "https://api.themoviedb.org/3/search/movie"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
API_KEY = "544dae6d15a7cc2133900c58451e1da8"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.app_context().push()

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    # def __repr__(self):
    #     return '<User %r>' % self.username

db.create_all()

# After adding the new_movie the code needs to be commented out/deleted.
# So you are not trying to add the same movie twice.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

class MovieForm(FlaskForm):
    rating = StringField('Your Rating Out of 10', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route('/find')
def find():
    IMG = request.args.get('img_url')
    image_url = f"{IMAGE_URL}{IMG}"
    releas = request.args.get("year")
    release = int(releas.split("-")[0])
    new_movie = Movie(
        title = request.args.get("movie_tit"),
        year = release,
        img_url = image_url,
        description = request.args.get("overview")
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))
    # iden = Movie.query.filter_by(title=new_movie["title"])
    # return redirect(url_for('edit', id=iden))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    RateMovieForm = MovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if RateMovieForm.validate_on_submit():
        movie.rating = float(RateMovieForm.rating.data)
        movie.review = RateMovieForm.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", RateMovieForm=RateMovieForm)

@app.route('/delete')
def erase():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    AddMovieForm = AddMovie()
    if AddMovieForm.validate_on_submit():
        movie_title = AddMovieForm.title.data
        response = requests.get(NEW_URL, params={"api_key":API_KEY, "query":movie_title})
        response.raise_for_status()
        movies = response.json()['results'][0:10]
        # db.session.add()
        # db.session.commit()
        return render_template("select.html", movies=movies)
    return render_template("add.html", AddMovieForm=AddMovieForm)

if __name__ == '__main__':
    app.run(debug=True)
