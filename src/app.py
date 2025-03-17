import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from src.models import db, User, People, Planet, Favorite
from src.admin import setup_admin
from src.utils import APIException, generate_sitemap

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url:
    db_url = db_url.replace("postgres://", "postgresql://")
else:
    db_url = "sqlite:///starwars.db"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
Migrate(app, db)
CORS(app)
setup_admin(app)

with app.app_context():
    db.create_all()

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ------------------- USERS ------------------- #
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return jsonify(users_list), 200

@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorites_list = [
        {"id": f.id, "people_id": f.people_id, "planet_id": f.planet_id} 
        for f in favorites
    ]
    return jsonify(favorites_list), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or "username" not in data or "email" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already in use"}), 400
    
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already in use"}), 400

    new_user = User(
        username=data["username"],
        email=data["email"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created successfully", "id": new_user.id}), 201


# ------------------- PEOPLE ------------------- #
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [{"id": p.id, "name": p.name, "gender": p.gender} for p in people]
    return jsonify(people_list), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    return jsonify({"id": person.id, "name": person.name, "gender": person.gender}), 200

@app.route('/people', methods=['POST'])
def create_person():
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_person = People(
        name=data["name"],
        birth_year=data.get("birth_year"),
        gender=data.get("gender"),
        height=data.get("height"),
        mass=data.get("mass"),
        hair_color=data.get("hair_color"),
        skin_color=data.get("skin_color"),
        eye_color=data.get("eye_color")
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify({"msg": "Person created successfully"}), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    data = request.json
    for key, value in data.items():
        setattr(person, key, value)

    db.session.commit()
    return jsonify({"msg": "Person updated successfully"}), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    db.session.delete(person)
    db.session.commit()
    return jsonify({"msg": "Person deleted successfully"}), 200

# ------------------- PLANETS ------------------- #
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planet_list = [{"id": p.id, "name": p.name, "climate": p.climate} for p in planets]
    return jsonify(planet_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify({"id": planet.id, "name": planet.name, "climate": planet.climate}), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_planet = Planet(
        name=data["name"],
        climate=data.get("climate"),
        terrain=data.get("terrain"),
        population=data.get("population")
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "Planet created successfully"}), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    data = request.json
    for key, value in data.items():
        setattr(planet, key, value)

    db.session.commit()
    return jsonify({"msg": "Planet updated successfully"}), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted successfully"}), 200

# ------------------- FAVORITES ------------------- #
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get("user_id")
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if not user or not planet:
        return jsonify({"error": "User or Planet not found"}), 404

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.json.get("user_id")
    user = User.query.get(user_id)
    person = People.query.get(people_id)

    if not user or not person:
        return jsonify({"error": "User or Person not found"}), 404

    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Person added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get("user_id")
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planet removed from favorites"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.json.get("user_id")
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Person removed from favorites"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
