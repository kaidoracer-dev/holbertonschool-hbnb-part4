from flask import Flask
from flask_restx import Api
from app.extensions import db, bcrypt, jwt

def create_app(config_class="config.DevelopmentConfig"):
        app = Flask(__name__)
        app.config.from_object(config_class)

        db.init_app(app)
        bcrypt.init_app(app)
        jwt.init_app(app)

        from app.api.v1.users import api as users_ns
        from app.api.v1.auth import api as auth_ns
        from app.api.v1.amenities import api as amenities_ns
        from app.api.v1.places import api as places_ns
        from app.api.v1.reviews import api as reviews_ns

        authorizations = {
                "Bearer": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Add: Bearer <your_jwt_token>"
                }
        }

        api = Api(
                app,
                version="1.0",
                title="HBnB API",
                description="HBnB Application API",
                doc="/api/v1/",
                authorizations=authorizations,
                security="Bearer"
        )

        api.add_namespace(users_ns, path='/api/v1/users')
        api.add_namespace(auth_ns, path='/api/v1/auth')
        api.add_namespace(amenities_ns, path='/api/v1/amenities')
        api.add_namespace(places_ns, path='/api/v1/places')
        api.add_namespace(reviews_ns, path='/api/v1/reviews')

        return app