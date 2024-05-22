import html
import json
import re
import utilities


CLEANR = re.compile("<.*?>")
NUMS = re.compile("[^0-9]")


def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, "", string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded


class Review:
    def __init__(self, author, rating, review, ownerResponse=None):
        self._author = author
        self._rating = rating
        self._review = review
        self._ownerResponse = ownerResponse if ownerResponse != "" else None

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
    def ownerResponse(self):
        return self._ownerResponse

    # Setters
    @author.setter
    def author(self, author):
        self._author = author

    @rating.setter
    def rating(self, rating):
        self._rating = rating

    @review.setter
    def review(self, review):
        self._review = review

    @ownerResponse.setter
    def ownerResponse(self, ownerResponse):
        self._ownerResponse = ownerResponse

    # Convert to dictionary
    def to_dict(self):
        return {
            "author": self.author,
            "rating": self.rating,
            "review": self.review,
            "ownerResponse": (
                {"text": self.ownerResponse} if self.ownerResponse is not None else None
            ),
        }


class Business:
    def __init__(
        self,
        name,
        avg_rating,
        company_type,
        address,
        review_count,
        id = None,
        reviews= None,
    ):
        self._id = id
        self._name = name
        self._slug = utilities.get_slug(name)
        self._avg_rating = avg_rating
        self._company_type = company_type
        self._address = address
        self._review_count = review_count
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
    def avg_rating(self):
        return self._avg_rating

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

    @avg_rating.setter
    def avg_rating(self, avg_rating):
        self._avg_rating = avg_rating

    @company_type.setter
    def company_type(self, company_type):
        self._company_type = company_type

    @address.setter
    def address(self, address):
        self._address = address

    @review_count.setter
    def review_count(self, review_count):
        self._review_count = review_count

    @review_key.setter
    def review_key(self, review_key):
        self._review_key = review_key

    @reviews.setter
    def reviews(self, reviews):
        if self._reviews == None:
            self._reviews = reviews
        else:
            self._reviews = {**self._reviews, **reviews}

    # Convert to dictionary
    def to_dict(self):
        return {
            "name": self.name,
            "slug": self.slug,
            "company_type": self.company_type,
            "address": self.address,
            "review_count": self.review_count,
            "avg_rating": self.avg_rating,
            "reviews": {key: [review.to_dict() for review in value] for key, value in self.reviews.items()}
        }

    # Convert reviews to array of dictionaries
    def reviews_to_array(self, reviews):
        return [review.to_dict() for review in reviews]
