"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)













@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([{'id': person.id, 'name': person.name} for person in people])
    
    
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify({'id': person.id, 'name': person.name})




    
@app.route('/planet', methods=['GET'])
def get_planet():
    planets = Planet.query.all()
    return jsonify([{'id': planet.id, 'name': planet.name} for planet in planets])
    
    
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify({'id': planet.id, 'name': planet.name})
    




@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(
        [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active
            }
            for user in users
        ]
    )
    
@app.route('/users/favorites', methods=['GET'])
def get_user_favorite(user_id):
    user_id = 1 
    user = User.query.get_or_404(user_id) #busca al usuairo si no se encuentra devuelve un error 404
    # favorite.serialize() se llama en cada objeto Favorite para convertirlo en un diccionario JSON
    #  user.favorites devuelve una lista de objetos Favorite que pertenecen al usuario.
    return jsonify([favorite.serialize() for favorite in user.favorites]) 





@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def get_favorite_planet(planet_id):
    user_id = 1  # Ajustar para obtener el ID del usuario actual
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite) # Añade el nuevo objeto favorite a la sesión de la base de datos.
    db.session.commit() # Guarda los cambios en la base de datos, lo que significa que el nuevo favorito se inserta en la tabla 
    return jsonify(favorite.serialize()), 201 # Este es el código de estado HTTP para "Created"

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def get_favorite_people(people_id):
    user_id = 1  # Ajustar para obtener el ID del usuario actual
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite) # Añade el nuevo objeto favorite a la sesión de la base de datos.
    db.session.commit() # Guarda los cambios en la base de datos, lo que significa que el nuevo favorito se inserta en la tabla 
    return jsonify(favorite.serialize()), 201 # Este es el código de estado HTTP para "Created"



@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first_or_404()
    db.session.delete(favorite) # Añade la operación de eliminación del objeto favorite a la sesión de la base de datos.
    db.session.commit()
    return jsonify({"message": "favorito eliminado"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get_json()  # Obtener datos JSON del cuerpo de la solicitud
    user_id = data.get('user_id')  # Obtener el user_id desde los datos de la solicitud
    
    if not user_id:
        return jsonify({"error": "user is required"}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first_or_404()
    db.session.delete(favorite) # Añade la operación de eliminación del objeto favorite a la sesión de la base de datos.
    db.session.commit()
    return jsonify({"message": "favorito eliminado"}), 200


@app.route('/create_users', methods=['POST'])
def create_user():
    data = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_active = data.get('is_active', True)

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    new_user = User(username=username, email=email, password=password, is_active=is_active)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active
    }), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
