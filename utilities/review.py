import html
import re
import utilities
from collections import defaultdict


CLEANR = re.compile("<.*?>")
NUMS = re.compile("[^0-9.]")


def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, "", string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded

# Convert reviews to array of dictionaries
def reviews_to_array(reviews):
    return [review.to_dict() for review in reviews]


class Review:
    def __init__(self, author, rating, review, owner_response=None):
        self._author = author
        self._rating = int(re.sub(NUMS, '', rating)) if isinstance(rating, str) else rating
        self._review = review
        self._owner_response = owner_response if owner_response != "" else None

    # Getters
    @property
    def author(self):
        return self._author

    @property
    def rating(self):
        return self._rating

    @property
    def review(self):
        return self._review

    @property
    def owner_response(self):
        return self._owner_response

    # Setters
    @author.setter
    def author(self, author):
        self._author = author

    @rating.setter
    def rating(self, rating):
        self._rating = float(re.sub(NUMS, "", rating))

    @review.setter
    def review(self, review):
        self._review = review

    @owner_response.setter
    def owner_response(self, owner_response):
        self._owner_response = owner_response

    # Convert to dictionary
    def to_dict(self):
        return {
            "author": clean(self.author),
            "rating": self.rating,
            "review": clean(self.review),
            "owner_response": (
                {"text": clean(self.owner_response)} if self.owner_response is not None else None
            ),
        }


class Business:
    def __init__(
        self,
        name,
        average_rating,
        company_type,
        address,
        review_count,
        id = None,
        reviews= None,
    ):

        self._review_key = None
        self._id = id
        self._name = name
        self._slug = utilities.get_slug(name)
        self._average_rating = float(re.sub(NUMS, "", average_rating)) if isinstance(average_rating, str) else average_rating
        self._company_type = company_type
        self._address = address
        self.review_count = int(re.sub(NUMS, "", review_count)) if isinstance(review_count, str) else review_count
        self._reviews = reviews

    # Getters
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def slug(self):
        return self._slug

    @property
    def average_rating(self):
        return self._average_rating

    @property
    def company_type(self):
        return self._company_type

    @property
    def address(self):
        return self._address

    @property
    def review_count(self):
        return self._review_count

    @property
    def review_key(self):
        return self._review_key

    @property
    def reviews(self):
        return self._reviews

    @id.setter
    def id(self, id):
        self._id = id

    @name.setter
    def name(self, name):
        self._name = name

    @slug.setter
    def slug(self, slug):
        self._slug = utilities.get_slug(slug)

    @average_rating.setter
    def average_rating(self, average_rating):
        if isinstance(average_rating, 'str'):
            self._average_rating = float(re.sub(NUMS,"", average_rating))
        self._average_rating = average_rating

    @company_type.setter
    def company_type(self, company_type):
        self._company_type = company_type

    @address.setter
    def address(self, address):
        self._address = address

    @review_count.setter
    def review_count(self, review_count):
        if isinstance(review_count, str):
            self._review_count = int(re.sub(NUMS, "", review_count))
        self._review_count = review_count

    @review_key.setter
    def review_key(self, review_key):
        self._review_key = review_key

    @reviews.setter
    def reviews(self, reviews):
        if self._reviews is None:
            self._reviews = reviews
        else:
            self._reviews = {**self._reviews, **reviews}

    # Convert to dictionary
    def to_dict(self):
        return {
            "name": self.name,
            "slug": self.slug,
            "company_type": utilities.get_whitelist_types(self.company_type),
            "address": self.address,
            "review_count": self.review_count,
            "average_rating": self.average_rating,
            "reviews": {key: [review.to_dict() for review in value] for key, value in self.reviews.items()},
        }
