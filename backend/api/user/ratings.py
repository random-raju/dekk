"""
Sample API calls:
    POST - http://127.0.0.1:5000/api/v1/ratings/dekk
{
    "rating" : 1,
    "dekk_id" : "cd888b33d7219a2a970f855aabb01cde",
    "comments": "abv"
}

"""
import os
from datetime import datetime

import falcon
import jwt
import psycopg2
from utils import hashing
from utils import http_response
from utils import postgres
from utils.logger import logger_main


LOGGER = logger_main("ratings")

UNIQUE_KEYS = ["account_id", "dekk_id"]


def update_user_dekk_ratings(ratings_row, db_obj):

    ratings_row["updated_at"] = datetime.utcnow()
    db_obj.pg_handle_update(ratings_row, unique_key="id")


def insert_user_dekk_ratings(req, db_obj):

    status_ok = True

    req_data = req.media
    dekk_id = req_data["dekk_id"]
    rating = req_data["rating"]
    comments = req_data["comments"]

    if rating > 0 and rating <= 5:

        env = os.environ.get(f"ENV")
        secret = os.environ.get(f"SECRET_{env}")
        token = req.headers.get("AUTHORIZATION")
        jwt_decoded = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

        account_id = jwt_decoded["account_id"]
        ratings_row = {
            "account_id": account_id,
            "dekk_id": dekk_id,
        }
        row_hash = hashing.get_hash(ratings_row, UNIQUE_KEYS)

        ratings_row = {  # reassign
            "account_id": account_id,
            "rating": rating,
            "dekk_id": dekk_id,
            "comments": comments,
            "id": row_hash,
        }

        try:
            db_obj.pg_handle_insert(ratings_row)
        except psycopg2.errors.UniqueViolation as e:
            LOGGER.exception(e)
            update_user_dekk_ratings(ratings_row, db_obj)
        except Exception as e:
            raise e
    else:
        error_message = "Invalid rating value"
        LOGGER.exception(error_message)
        raise falcon.HTTPBadRequest("Bad request", error_message)

    return status_ok


class Ratings:
    """

    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("users", "ratings")

    # @falcon.before(request_valiation)
    def on_post(self, req, resp):
        try:
            result = insert_user_dekk_ratings(req, self.db_conn)
            if result:
                message = {"message": "Successfully added ratings"}
                LOGGER.exception(message)
                http_response.ok(resp, message)
        except Exception as e:
            error_message = "Something went wrong in dekk ratings requests" + str(e)
            message = {"message": error_message}
            LOGGER.exception(message)
            http_response.err(resp, falcon.HTTP_500, message)
