"""
Sample API calls:
    POST - http://127.0.0.1:8000/api/v1/login
   {
            "email" : "darshan@gmail.com",
            "password" : "darshanraju",
            "verification_code" : 12345
    }


    POST - http://127.0.0.1:8000/api/v1/googlereglog

     {
        "email": "darshanr163@gmail.com",
        "familyName": "Raju",
        "givenName": "Darshan",
        "googleId": "117765997799925296176",
        "imageUrl": "https://lh3.googleusercontent.com/a-/AOh14GgZZJfnD7e5Qy8wDnn-5_y0ibYicAKg86qbwBOPrPw=s96-c",
        "name": "Darshan Raju"
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
    "verification_code"
]

REQUEST_OBJECT_KEYS.sort()

LOGGER = logger_main("login")

REGISTER_TABLE_UNIQUE_CONSTRAINT = "email_unique_constraint"


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


def get_user(req, db_conn,by_email = False):

    req_data = req.media

    user_email = req_data["email"].lower().strip()

    if by_email == True:
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
                email = %(email)s
        """

        values = {
            "email": user_email,
        }
    else:
        password = req_data["password"]
        verification_code = req_data["verification_code"]
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


def create_user_with_google_cred(req,db_conn):
    """
        create user dictionary to ease insert query
        todo:
            make sure you use only email as use name
    """
    user_data = {}

    req_data = req.media

    user_data["user_name"] = req_data["name"].lower().strip() + "_dekkuser"
    user_data["full_name"] = req_data["name"].strip()
    user_data["email"] = req_data["email"].lower().strip()
    # user_data["password"] = hashlib.md5(req_data["password"].encode()).hexdigest()
    # user_data["password"] = req_data["password"]

    user_data['profile_pic_link'] = req_data["imageUrl"]
    user_data["google_id"] = req_data["googleId"]

    try:
        db_conn.table = 'accounts'
        status_code = db_conn.pg_handle_insert(
            user_data, unique_constraint = REGISTER_TABLE_UNIQUE_CONSTRAINT
        )
        print(status_code)
        if status_code:
            return True
        else:
            return False
            # raise Exception('Oops, something went wrong! Couldnt create user via google api')
    except psycopg2.errors.UniqueViolation as e:
        return False

    
class GoogleRegisterLogin:
    """
        Request data has to be a json
        todo -
            Hard coded exp time
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("users", "accounts")

    # @falcon.before(request_valiation)
    def on_post(self, req, resp):
        try:
            headers = req.headers
            is_already_user = create_user_with_google_cred(req, self.db_conn)
            user = get_user(req,self.db_conn,by_email=True)
            print(user)
            self.db_conn.table = 'sessions'

            if not user:
                error_message = "Could not find user with this email id"
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
        except Exception as e:
            print(e)
            http_response.ok(resp, {"Fail" : "Asd"})

        # if is_already_user == True:
        #     # get user and get jwt

        #     # error_message = "Password and email combination did not match"
        #     # message = {"message": error_message}
        #     # LOGGER.exception(message)
        #     http_response.err(resp, "401", message)
        # elif user:
        #     try:
        #         session_id = str(uuid.uuid4())
        #         ok = create_user_session(self.db_conn, user, headers, session_id)
        #         if ok:
        #             jwt = create_jwt(user, session_id)
        #             status = "Login Successful"
        #             message = {"message": status, "auth_token": jwt}
        #             LOGGER.info(message)
        #             http_response.ok(resp, message)
        #     except Exception as error_message:
        #         message = {"message": str(error_message)}
        #         LOGGER.exception(message)
        #         http_response.err(resp, falcon.HTTP_500, message)
        # else:
        #     error_message = "Something went wrong, while logging in"
        #     message = {"message": error_message}
        #     LOGGER.exception(message)
        #     http_response.err(resp, falcon.HTTP_500, message)