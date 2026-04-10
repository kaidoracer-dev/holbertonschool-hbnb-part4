from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new review"""
        try:
            current_id = get_jwt_identity()
            data = request.json
            data["user_id"] = current_id

            place_id = data.get("place_id")

            place = facade.get_place(place_id)
            if not place:
                return {"error": "Place not found"}, 400
            if place.user_id == current_id:
                return {"error": "Cannot review your own place"}, 400

            all_reviews = facade.get_all_reviews()

            existing_review = next(
            (r for r in all_reviews
            if r.user_id == current_id and r.place_id == place_id),
            None
            )
            if existing_review:
                return {"error": "User has already reviewed this place"}, 400

            review = facade.create_review(data)
            if not review:
                return {"error": "Invalid input data"}, 400

            return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user_id,
                'place_id': review.place_id
            }, 201
        except Exception as e:
            return {"error": str(e)}, 500

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        return {
            'reviews': [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating
                }
            ] for review in reviews
        }, 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {"error": "review not found"}, 404
        return {
            'id': review.id,
            'text': review.text,
            'rating': review.rating,
            'user_id': review.user_id,
            'place_id': review.place_id
        }, 201

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, review_id):
        """Update a review's information"""
        try:
            current_user = get_jwt_identity()
            review = facade.get_review(review_id)
            claims = get_jwt()

            if not review:
                return {"error": "Review not found or invalid data"}, 404

            if review.user_id != current_user and not claims.get('is_admin'):
                return {'error': 'Unauthorized action'}, 403
            data = api.payload

            if not data:
                return {"error": "Review not found or invalid data"}, 400

            data["user_id"] = current_user
            review_up = facade.update_review(review_id, data)

            return {"message": "Review updated successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)
        claims = get_jwt()

        if not review:
            return {"error": "Review not found or invalid data"}, 404
        if review.user_id != current_user and not claims.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        success = facade.delete_review(review_id)

        return {"message": "Review deleted successfully"}, 200