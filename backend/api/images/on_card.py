"""
Sample API calls:
    POST - http://127.0.0.1:5000/api/v1/images/card
    {
        "card_id" : "2cf142cb0e222fc382ccddb5ef91454c",
        "image_date" : "base64 string"
    }

"""
import base64
import json
import os
import random
import re
import string
from mimetypes import guess_extension
from mimetypes import guess_type

import boto3
import falcon
import jwt
from api.user import authorization
from utils import http_response
from utils import postgres

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET = "dekk-images"
S3_BASE_URL = f"https://{S3_BUCKET}.s3.ap-south-1.amazonaws.com"


def request_valiation(req, resp, resource, params):

    try:
        token = req.headers.get("AUTHORIZATION")
        options = {"verify_exp": True}
        env = os.environ.get(f"ENV")
        secret = os.environ.get(f"SECRET_{env}")
        jwt.decode(token, secret, verify="True", algorithms=["HS256"], options=options)
    except Exception as e:
        print(e)
        raise falcon.HTTPUnauthorized("Authentication required")


def get_card_by_id(db_conn, card_id):

    card_ids_query = f"""
        SELECT
            title,content_on_front,content_on_back,
            highlighted_keywords,permission,type,image_links,card_id,account_id
         FROM user_content.cards
        where card_id = '{card_id}'
        limit 1
    """
    card = db_conn.fetch_query_direct_query(card_ids_query)

    return card


def generate_random_file_name(extension):

    file_name = "".join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits + string.ascii_uppercase
        )
        for _ in range(30)
    )
    return file_name + "." + extension


def get_account_id(req):

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    account_id = decode["account_id"]

    return account_id


class ImagesOnCard:
    """
        Request data has to be a json
    """

    def __init__(self):
        session = boto3.Session(profile_name="dekk")
        self.s3_client = session.client("s3")
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        """
            Todo -
                Add logger
                Add conditions before adding for user and super user
        """
        try:
            req_data = req.media
            image_data = req_data["image_data"]
            card_id = req_data["card_id"]
            account_id = get_account_id(req)
            card = get_card_by_id(self.db_conn, card_id)

            if not card:
                raise falcon.HTTPBadRequest("Card doesn't exist")

            if card and card[0]["account_id"] != account_id:
                raise falcon.HTTPUnauthorized("Permission not granted")

            if card and card[0]["image_links"] and len(card[0]["image_links"]) >= 2:
                message = "Max limit reached - delete an image"
                raise falcon.HTTPBadRequest(message)

            extension = guess_extension(guess_type(image_data)[0])[1:]
            if extension not in EXTENSIONS:
                message = f"Valid image formats are {EXTENSIONS}"
                raise falcon.HTTPBadRequest(message)

            image_str = re.sub(r"^data:image/.*;base64,", "", image_data)
            image_data = base64.b64decode(image_str)

            file_name = generate_random_file_name(extension)

            s3_response = self.s3_client.put_object(
                Body=image_data, Bucket=S3_BUCKET, Key=file_name
            )

            if s3_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                s3_link = f"{S3_BASE_URL}/{file_name}"
                message = "Uploaded image"
                message = {"message": message, "image_location": s3_link}
                image_links = card[0]["image_links"]
                image_links.append(s3_link)

                card_update = {
                    "image_links": json.dumps(image_links),
                    "card_id": card_id,
                }
                status = self.db_conn.pg_handle_update(
                    card_update, "card_id", commit=True
                )
                if status >= 1:
                    http_response.ok(resp, message)
                else:
                    error_message = "Oops! Something went wrong while uploading image"
                    message = {"message": error_message}
                    http_response.err(resp, falcon.HTTP_500, message)
        except Exception as e:
            print(e)
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)

    # @falcon.before(authorization.request_valiation)
    def on_delete(self, req, resp):

        try:
            req_data = req.media
            image_link = req_data["image_link"]
            card_id = req_data["card_id"]
            account_id = get_account_id(req)
            card = get_card_by_id(self.db_conn, card_id)

            if not card:
                raise falcon.HTTPBadRequest("Card doesn't exist")

            if not card[0]["image_links"]:
                raise falcon.HTTPBadRequest("Card doesn't have any images")

            if card and card[0]["account_id"] != account_id:
                raise falcon.HTTPUnauthorized("Permission not granted")

            message = "Deleted image"
            key = re.search(r"com\/()(.*)", image_link).group().replace("com/", "")

            s3_response = self.s3_client.delete_object(Bucket=S3_BUCKET, Key=key)

            if s3_response["ResponseMetadata"]["HTTPStatusCode"] == 204:

                message = {"message": "Deleted image"}
                image_links = card[0]["image_links"]
                if image_link in image_links:
                    image_links.remove(image_link)

                if image_links:
                    card_update = {
                        "image_links": json.dumps(image_links),
                        "card_id": card_id,
                    }
                else:
                    card_update = {"image_links": None, "card_id": card_id}
                status = self.db_conn.pg_handle_update(
                    card_update, "card_id", commit=True
                )
                if status >= 1:
                    http_response.ok(resp, message)
                else:
                    error_message = "Oops! Something went wrong while deleting image"
                    message = {"message": error_message}
                    http_response.err(resp, falcon.HTTP_500, message)
            else:
                error_message = "Oops! Something went wrong while deleting image"
                message = {"message": error_message}
                http_response.err(resp, falcon.HTTP_500, message)

        except Exception as e:
            print(e)
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
