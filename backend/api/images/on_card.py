"""
Sample API calls:
    POST - http://127.0.0.1:5000/api/v1/images/card
    {
        "card_id" : "2cf142cb0e222fc382ccddb5ef91454c",
        "image_date" : "base64 string"
    }

"""
import base64
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


def generate_random_file_name():

    file_name = "".join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits + string.ascii_uppercase
        )
        for _ in range(30)
    )
    return file_name


class ImagesOnCard:
    """
        Request data has to be a json
    """

    def __init__(self):
        session = boto3.Session(profile_name="dekk")
        self.s3_client = session.client("s3")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        """
            DB update for a card
            Checks
        """
        try:
            req_data = req.media
            image_data = req_data["image_data"]
            extension = guess_extension(guess_type(image_data)[0])[1:]
            if extension not in EXTENSIONS:
                message = {"message": f"Valid image formats are {EXTENSIONS}"}
                http_response.err(resp, falcon.HTTP_500, message)

            image_str = re.sub(r"^data:image/.*;base64,", "", image_data)
            image_data = base64.b64decode(image_str)

            file_name = generate_random_file_name()

            file_name = file_name + "." + extension
            s3_response = self.s3_client.put_object(
                Body=image_data, Bucket=S3_BUCKET, Key=file_name
            )

            if s3_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                s3_link = f"{S3_BASE_URL}/{file_name}"
                message = "Uploaded image"
                message = {"message": message, "image_location": s3_link}
                http_response.ok(resp, message)
        except Exception as e:
            print(e)
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
