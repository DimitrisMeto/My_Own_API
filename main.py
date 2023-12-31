from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean)
    has_wifi = db.Column(db.Boolean)
    has_sockets = db.Column(db.Boolean)
    can_take_calls = db.Column(db.Boolean)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random", methods=["GET"])
def get_random_cafe():
    if request.method == "GET":
        all_cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(all_cafes)
        return jsonify(cafe={
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
            "has_sockets": random_cafe.has_sockets,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "id": random_cafe.id,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "map_url": random_cafe.map_url,
            "name": random_cafe.name,
            "seats": random_cafe.seats,
        })


@app.route("/all")
def get_all_cafes():
    if request.method == "GET":
        all_cafes = Cafe.query.all()
        list_of_cafes = [cafe.to_dict() for cafe in all_cafes]
        return jsonify(cafes=list_of_cafes)


@app.route("/search")
def find_cafe_by_location():
    search_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=search_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={
            "Not Found": "Sorry we don't have a cafe at that location.",
        })


@app.route("/add", methods=["POST"])
def add_new_cafe():
    key = request.args.get("api-key")
    if key == "TopSecretAPIKey":
        new_cafe = Cafe(name=request.form.get("name"), map_url=request.form.get("map_url"),
                        img_url=request.form.get("img_url"),
                        location=request.form.get("location"), has_sockets=bool(request.form.get("has_sockets")),
                        has_toilet=bool(request.form.get("has_toilet")), has_wifi=bool(request.form.get("has_wifi")),
                        can_take_calls=bool(request.form.get("can_take_calls")), seats=request.form.get("seats"),
                        coffee_price=request.form.get("coffee_price"))
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={
            "success": "Successfully added the new cafe.",
        })
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key."), 403


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price."), 200
    else:
        return jsonify(error={
            "Not Found": "Sorry a cafe with that id was not found in the database."
        }), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def closed_cafe(cafe_id):
    key = request.args.get("api-key")
    if key == "TopSecretAPIKey":
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="Successfully deleted the cafe from the database."), 200
        else:
            return jsonify(error={
                "Not Found": "Sorry a cafe with that id was  not found in the database."
            }), 404
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key."), 403


if __name__ == '__main__':
    app.run(debug=True, port=8000)
