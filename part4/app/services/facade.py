from app.persistence.repository import InMemoryRepository
from app.persistence.repository import SQLAlchemyRepository
from app import db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
import uuid

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        return self.model.query.filter_by(email=email).first()

class PlaceRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Place)

    def get_place_by_id(self, place_id):
        return self.model.query.get(place_id)

class ReviewRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Review)

    def get_review_by_id(self, review_id):
        return self.model.query.get(review_id)
    
class AmenityRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Amenity)

    def get_amenity_by_id(self, amenity_id):
        return self.model.query.get(amenity_id)


class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.amenity_repo = AmenityRepository()
        self.review_repo = ReviewRepository()

    def create_user(self, user_data):
        user = User(**user_data)
        if not user:
            return None
        password = user_data.get('password')
        user.hash_password(user_data['password'])
        self.user_repo.add(user)
        return user

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.get_user(user_id)

        if not user:
            return None

        for key, value in user_data.items():
            setattr(user, key, value)

        self.user_repo.update(user, user_data)

        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)
    
    def delete_user(self, user_id):
        self.user_repo.delete(user_id)
        return True

    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        if not amenity:
            return None
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        for key, value in amenity_data.items():
            setattr(amenity, key, value)
        self.amenity_repo.update(amenity, amenity_data)
        return amenity

    def link_amenity_to_place(self, place_id, amenity_id):
        place = Place.query.get(place_id)
        if not place:
            return False

        try:
            uuid_obj = uuid.UUID(amenity_id)
        except ValueError:
            return False

        amenity = Amenity.query.get(amenity_id)
        if not amenity:
            return False

        if amenity not in place.amenities:
            place.amenities.append(amenity)
            db.session.commit()
        
        return True

    def create_place(self, place_data):

        amenities_data = place_data.pop("amenities", [])

        place = Place(**place_data)

        if not place:
            return None

        self.place_repo.add(place)

        for amenity_name in amenities_data:
            amenity = self.create_amenity({"name": amenity_name})

            if amenity:
                place.amenities.append(amenity)

        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return [obj for obj in self.place_repo.get_all() if isinstance(obj, Place)]

    def update_place(self, place_id, place_data):
        place = self.get_place(place_id)

        if not place:
            return None

        for key, value in place_data.items():
            setattr(place, key, value)

        self.place_repo.update(place_id, place_data)

        return place
    
    def delete_place(self, place_id):
        self.place_repo.delete(place_id)
        return True

    def create_review(self, review_data):
        review = Review(**review_data)
        if not review:
            return None
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return list(self.review_repo.get_all())

    def get_reviews_by_place(self, place_id):
        result = []
        for review in self.review_repo.get_all():
            if review.place_id == place_id:
                result.append(review)
        return result

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None
        review.update(review_data)
        return review

    def delete_review(self, review_id):
        self.review_repo.delete(review_id)
        return True
