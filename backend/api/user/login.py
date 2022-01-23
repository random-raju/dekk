"""
Sample API calls:
    POST - http://127.0.0.1:8000/api/v1/login
    {
            "email" : "darshan@gmail.com",
            "password" : "darshanraju"
    }

"""
import os
import uuid
from datetime import datetime
from datetime import timedelta

import falcon
import jwt
import psycopg2
from utils import http_response
from utils import postgres
from utils.logger import logger_main

REQUEST_OBJECT_KEYS = [
    "email",
    "password",
]

REQUEST_OBJECT_KEYS.sort()

LOGGER = logger_main("login")


def request_valiation(req, resp, resource, params):

    try:
        req_data = req.media
    except:
        error_message = (
            f"Empty value in key - required key-value pairs {REQUEST_OBJECT_KEYS}"
        )
        raise falcon.HTTPBadRequest("Bad request", error_message)

    keys_req_data = list(req_data.keys())
    keys_req_data.sort()

    if not REQUEST_OBJECT_KEYS == keys_req_data:
        error_message = f"Missing keys - required key-value pairs {REQUEST_OBJECT_KEYS}"
        raise falcon.HTTPBadRequest("Bad request", error_message)

    for key in req_data:
        if not req_data[key]:
            error_message = (
                f"Empty value in key - required key-value pairs {REQUEST_OBJECT_KEYS}"
            )
            raise falcon.HTTPBadRequest("Bad request", error_message)
        if key == "password" and len(req_data["password"]) <= 7:
            error_message = "Password is less than 8 characters"
            raise falcon.HTTPBadRequest("Bad request", error_message)


def get_user(req, db_conn):

    req_data = req.media

    user_email = req_data["email"].lower().strip()
    password = req_data["password"]

    skeleton = f"""
        SELECT
            user_name,
            account_id,
            created_at,
            last_active,
            full_name,
            is_admin
        FROM
            users.accounts
        WHERE
            email = %(email)s AND
            password = %(password)s
    """

    values = {
        "email": user_email,
        "password": password,
    }

    query_result = db_conn.pg_fetch_rows(skeleton, values)

    return query_result


def create_user_session(db_obj, user, headers, session_id):

    user_session_dict = {
        "account_id": user[0]["account_id"],
        "session_id": session_id,
        "user_agent": headers["USER-AGENT"],
        "host": headers["HOST"],
        "is_active": True,
    }

    try:
        rowcount = db_obj.pg_handle_insert(user_session_dict)
    except psycopg2.errors.UniqueViolation:
        raise Exception("User has already logged in")
    except Exception:
        raise Exception(
            f"Something went wrong while creating session for user {user[0]['account_id']}"
        )
    if rowcount > 0:
        return True
    else:
        return False


def create_jwt(user, session_id):

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    user_details = {
        "user_name": user[0]["user_name"],
        "full_name": user[0]["full_name"],
        "is_admin": user[0]["is_admin"],
        "account_id": user[0]["account_id"],
        "session_id": session_id,
        "exp": datetime.utcnow() + timedelta(seconds=100800),  # todo
    }
    token = jwt.encode(user_details, secret, algorithm="HS256")

    return token


class Login:
    """
        Request data has to be a json
        todo -
            Hard coded exp time
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("users", "sessions")

    @falcon.before(request_valiation)
    def on_post(self, req, resp):
        headers = req.headers
        user = get_user(req, self.db_conn)
        if not user:
            error_message = "Password and email combination did not match"
            message = {"message": error_message}
            LOGGER.exception(message)
            http_response.err(resp, "401", message)
        elif user:
            try:
                session_id = str(uuid.uuid4())
                ok = create_user_session(self.db_conn, user, headers, session_id)
                if ok:
                    jwt = create_jwt(user, session_id)
                    status = "Login Successful"
                    message = {"message": status, "auth_token": jwt}
                    LOGGER.info(message)
                    http_response.ok(resp, message)
            except Exception as error_message:
                message = {"message": str(error_message)}
                LOGGER.exception(message)
                http_response.err(resp, falcon.HTTP_500, message)
        else:
            error_message = "Something went wrong, while logging in"
            message = {"message": error_message}
            LOGGER.exception(message)
            http_response.err(resp, falcon.HTTP_500, message)
