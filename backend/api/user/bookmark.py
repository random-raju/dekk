"""
Sample API calls:
    GET - http://127.0.0.1:5000/api/v1/bookmark/card/00379eea64d5330747d109b3c12e2045
    GET - http://127.0.0.1:5000/api/v1/unmark/card/00379eea64d5330747d109b3c12e2045


"""
import os

import falcon
import jwt
from api.user import authorization
from utils import http_response
from utils import postgres


def mark_card(db_conn, req, card_id, flag):

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    account_id = decode["account_id"]

    query = f"""
    UPDATE users.activity_log
    set bookmarked = {flag}
    WHERE id = md5(concat({account_id},'{card_id}'))
    """

    db_conn.conn_obj.cursor.execute(query)
    db_conn.conn_obj.conn.commit()
    rowcount = db_conn.conn_obj.cursor.rowcount

    if rowcount:
        return True
    else:
        return False


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


class BookmarkCard:
    """
        Request data has to be a json
    """

    def __init__(self):
        self.db_conn = postgres.QueryManager("users", "activity_log")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp, card_id):
        try:
            if not card_id:
                error_message = "Empty card id"
                raise falcon.HTTPBadRequest("Bad request", error_message)

            result = mark_card(self.db_conn, req, card_id, "true")
            if result:
                message = "Bookmarked card"
                message = {"message": message}
                http_response.ok(resp, message)
            else:
                message = {"message": "Nothing changed"}
                http_response.err(resp, falcon.HTTP_304, message)
        except Exception as e:
            print(e)
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)


class UnmarkCard:
    """
        Request data has to be a json
    """

    def __init__(self):
        self.db_conn = postgres.QueryManager("users", "activity_log")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp, card_id):
        try:
            if not card_id:
                error_message = "Empty card id"
                raise falcon.HTTPBadRequest("Bad request", error_message)

            result = mark_card(self.db_conn, req, card_id, "false")
            if result:
                message = "Unmarked card"
                message = {"message": message}
                http_response.ok(resp, message)
            else:
                message = {"message": "Nothing changed"}
                http_response.err(resp, falcon.HTTP_304, message)
        except Exception as e:
            print(e)
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
