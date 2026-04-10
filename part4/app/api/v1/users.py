from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True,
                                description='First name of the user'),
    'last_name': fields.String(required=True,
                                description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

update_user_model = api.model('User Update', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user'),
    'email': fields.String(required=False, description='[READ ONLY] Cannot be modified'),
    'password': fields.String(required=False, description='[READ ONLY] Cannot be modified'),
})

@api.route('/')
class AdminUserCreate(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(400, 'Email already registered')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self):
        """Create a user passing by admin"""
        try:
            claims = get_jwt()
            if not claims.get('is_admin'):
                return {'error': 'Admin privileges required'}, 403

            user_data = api.payload
            if not user_data:
                return {"error": "Invalid input data"}, 400

            email = user_data.get('email')
            if facade.get_user_by_email(email):
                return {'error': 'Email already registered'}, 400

            new_user = facade.create_user(user_data)
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
            }, 201
        except Exception as e:
            return {"error": str(e)}, 500


    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of all users"""

        users = facade.get_all_users()

        return [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}
                for user in users], 200


@api.route('/<user_id>')
class UserResource(Resource):
    """Class route which can get an user with his email"""
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
                }, 200


    @api.expect(update_user_model, validate=True)
    @api.response(200, 'User updated successfully !')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')

    @jwt_required()
    def put(self, user_id):
        """Update user infos"""
        try:
            current_user = get_jwt()
            user = facade.get_user(user_id)
            claims = get_jwt()

            if not user:
                return {'error': 'User not found'}, 404
            if user_id != current_user and not claims.get('is_admin'):
                return {'error': 'Unauthorized action'}, 403

            user_data = api.payload

            if not user_data:
                return {'error': 'Invalid input data'}, 400

            if ('email' in user_data or 'password' in user_data) and not claims.get('is_admin'):
                return {'error': 'You cannot modify email or password'}, 400
            
            email = user_data.get('email')

            if email:
                existing_user = facade.get_user_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return {'error': 'Email is already in use'}, 400

            user_data["user_id"] = current_user
            facade.update_user(user_id, user_data)

            return {"message": "User updated successfully !"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @api.response(200, 'User deleted successfully')
    @api.response(404, 'User not found')
    @jwt_required()
    def delete(self, user_id):
        """Delete a user"""
        current_user = get_jwt_identity()
        user = facade.get_user(user_id)
        claims = get_jwt()

        if not user:
            return {"error": "User not found or invalid data"}, 404

        if user.id != current_user and not claims.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403

        success = facade.delete_user(user_id)

        return {"message": "User deleted successfully"}, 200