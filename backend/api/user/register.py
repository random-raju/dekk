"""
Sample API calls:
    POST - http://127.0.0.1:8000/api/v1/register
    {
            "user_name" : "draju",
            "full_name" : "darshan",
            "email" : "darshan@gmail.com",
            "password" : "darshanraju",
            "college" : "xyz"
    }
"""
import hashlib

import falcon
import psycopg2
from utils import http_response
from utils import postgres

REQUEST_OBJECT_KEYS = [
    "user_name",
    "full_name",
    "email",
    "password",
    # "college",
]


REQUEST_OBJECT_KEYS.sort()

REGISTER_TABLE_UNIQUE_CONSTRAINT = "email_unique_constraint"


def request_valiation(req, resp, resource, params):

    try:
        req_data = req.media
        if not req_data:
            error_message = (
                f"Empty value in key - required key-value pairs {REQUEST_OBJECT_KEYS}"
            )
            raise falcon.HTTPBadRequest("Bad request", error_message)
    except:
        error_message = (
            f"Empty value in key - required key-value pairs {REQUEST_OBJECT_KEYS}"
        )
        raise falcon.HTTPBadRequest("Bad request", error_message)

    keys_req_data = list(req_data.keys())
    keys_req_data.sort()
    
    try:
        keys_req_data.remove('college')
    except:
        pass

    if not REQUEST_OBJECT_KEYS == keys_req_data:
        error_message = f"Missing keys - required key-value pairs {REQUEST_OBJECT_KEYS}"
        raise falcon.HTTPBadRequest("Bad request", error_message)

    for key in req_data:
        if req_data[key] == "college":
            continue
        if not req_data[key]:
            error_message = (
                f"Empty value in key - required key-value pairs {REQUEST_OBJECT_KEYS}"
            )
            raise falcon.HTTPBadRequest("Bad request", error_message)
        if key == "password" and len(req_data["password"]) <= 7:
            error_message = "Password is less than 8 characters"
            raise falcon.HTTPBadRequest("Bad request", error_message)


def create_user(req):
    """
        create user dictionary to ease insert query
    """
    user_data = {}

    req_data = req.media

    user_data["user_name"] = req_data["user_name"].lower().strip()
    user_data["full_name"] = req_data["full_name"].strip()
    user_data["email"] = req_data["email"].lower().strip()
    # user_data["password"] = hashlib.md5(req_data["password"].encode()).hexdigest()
    user_data["password"] = req_data["password"]
    user_data["college"] = req_data.get("college",None)

    return user_data


class Register:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("users", "accounts")

    @falcon.before(request_valiation)
    def on_post(self, req, resp):

        user_dict = create_user(req,)

        try:
            status_code = self.db_conn.pg_handle_insert(
                user_dict, unique_constraint=REGISTER_TABLE_UNIQUE_CONSTRAINT
            )
            if status_code:
                status = "Created User"
                message = {"message": status}
                http_response.ok(resp, message)
            else:
                status = "Email already in use"
                message = {"message": status}
                http_response.err(resp, falcon.HTTP_409, message)
        except psycopg2.errors.UniqueViolation as e:
            status = "User name already in use"
            message = {"message": status}
            http_response.err(resp, falcon.HTTP_409, message)
