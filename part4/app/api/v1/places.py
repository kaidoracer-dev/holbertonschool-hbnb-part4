from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('places', description='Place operations')

# Define the models for related entities
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Adding the review model
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

# Define the place model for input validation and documentation
place_model = api.model('PlaceCreate', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True,
                            description='Latitude of the place'),
    'longitude': fields.Float(required=True,
                            description='Longitude of the place'),
})

update_place_model = api.model('PlaceUpdate', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True,
                            description='Latitude of the place'),
    'longitude': fields.Float(required=True,
                            description='Longitude of the place'),
})


@api.route('/')
class PlaceList(Resource):
    """Class route which create a place and read all the places created """
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place"""
        current_user = get_jwt_identity()

        if not current_user:
            return {"error": "Not authorized"}, 401
        
        place_data = api.payload

        if not place_data:
            return {"error": "Invalid input data"}, 400

        place_data['user_id'] = current_user
        new_place = facade.create_place(place_data)

        return {'id': new_place.id,
                'title': new_place.title,
                'description': new_place.description,
                'price': new_place.price,
                'latitude': new_place.latitude,
                'longitude': new_place.longitude,
                'owner_id': new_place.user_id
                }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""

        places = facade.get_all_places()

        return [{'id': place.id,
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude
                }
                for place in places
                ], 200


@api.route('/<place_id>')
class PlaceResource(Resource):
    """class route wich read a place with details and update a place"""
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""

        place = facade.get_place(place_id)
        owner = facade.get_user(place.user_id)

        if not place:
            return {'error': 'Place not found'}, 404

        return {'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'owner': f"{owner.first_name} {owner.last_name}",
                'amenities': [
                    {
                        'name': amenity.name
                    }
                    for amenity in place.amenities
                ]
                }, 200

    @api.expect(update_place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """
        Update a place
        """
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        claims = get_jwt()

        if not place:
            return {'error': 'Place not found'}, 404

        if place.user_id != current_user and not claims.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        place_data = api.payload
        if not place_data:
            return {'error': 'Invalid input data'}, 400

        place_data["user_id"] = current_user
        updated_place = facade.update_place(place_id, place_data)

        return {"message": "Place updated successfully"}, 200

    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @jwt_required()
    def delete(self, place_id):
        """Delete a place"""
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        claims = get_jwt()

        if not place:
            return {"error": "Place not found or invalid data"}, 404
        if place.user_id != current_user and not claims.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        success = facade.delete_place(place_id)

        return {"message": "Place deleted successfully"}, 200

@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        reviews = facade.get_reviews_by_place(place_id)
        if reviews is None:
            return {"message": "No reviews found for this place"}, 404
        return {
                            'reviews': [
                    {
                        'id': review.id,
                        'user': review.user_id,
                        'text': review.text,
                        'rating': review.rating
                    }
                    for review in reviews
                ]
        }, 200
