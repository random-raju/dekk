# import hashlib
# import json
# import os
# import re
# import falcon
# import jwt
# from api.user import authorization
# from utils import http_response
# from utils import postgres
# def request_valiation(req, resp, resource, params):
#     try:
#         token = req.headers.get("AUTHORIZATION")
#         options = {"verify_exp": True}
#         env = os.environ.get(f"ENV")
#         secret = os.environ.get(f"SECRET_{env}")
#         jwt.decode(token, secret, verify="True", algorithms=["HS256"], options=options)
#     except Exception as e:
#         print(e)
#         raise falcon.HTTPUnauthorized("Authentication required")
# # def increment_view_count(db_conn, card_id):
# #     db_conn.
# #     return True
# class CardViews:
#     def __init__(self) -> None:
#         self.db_conn = postgres.QueryManager("users", "activity_log")
#     #@falcon.before(authorization.request_valiation)
#     def on_post(self, req, resp, card_id):
#         query_result = increment_view_count(self.db_conn, card_id)
#         try:
#             http_response.ok(resp, query_result)
#         except:
#             error_message = "Something went wrong , id didnt match"
#             message = {"message": error_message}
#             http_response.err(resp, falcon.HTTP_500, message)
