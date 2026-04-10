from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity'),
})

single_amenity_model = api.model('SingleAmenity', {
    'amenity_id': fields.String(required=True, description='UUID of the amenity to link to the place')
})

@api.route('/')
class AmenityList(Resource):
    """ Class Route used to create an amenity and list all the amenities """
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self):
        """Register a new amenity"""

        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload

        if not amenity_data:
            return {"error": "Invalid input data"}, 400

        new_amenity = facade.create_amenity(amenity_data)
        return {'name': new_amenity.name}, 201


    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""

        amenities = facade.get_all_amenities()

        return [{'id': amenity.id, 'name': amenity.name}
                for amenity in amenities], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    """Route class used to read one amenity and update a amenity"""
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""

        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            return {'error': 'Ameninty not found'}, 404

        return {'id': amenity.id, 'name': amenity.name}, 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def put(self, amenity_id):
        """Update an amenity's information"""

        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload

        if not amenity_data:
            return {"error": "Invalid input data"}, 400

        amenity = facade.update_amenity(amenity_id, amenity_data)

        if not amenity:
            return {'error': 'Amenity not found'}, 404

        return {'id': amenity.id, 'name': amenity.name}, 200
    
@api.route('/link-one-to-place/<place_id>')
class PlaceSingleAmenityLink(Resource):
    """Link an amenity to a specific place"""
    
    @api.expect(single_amenity_model)
    @api.response(200, 'Amenity successfully linked')
    @api.response(404, 'Place or Amenity not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self, place_id):
        """Link one amenity to a place"""
        
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        
        data = api.payload
        if not data or 'amenity_id' not in data:
            return {"error": "Invalid input data"}, 400
        
        amenity_id = data['amenity_id']
        
        success = facade.link_amenity_to_place(place_id, amenity_id)
        
        if not success:
            return {'error': 'Place or Amenity not found'}, 404
        
        return {'message': 'Amenity linked successfully'}, 200
