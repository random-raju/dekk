"""

"""
# init env variables
from dotenv import load_dotenv

load_dotenv("./local.env")

import os
import falcon


from falcon.http_status import HTTPStatus
from api.user.register import Register
from api.user.login import Login
from api.cards.cards_actions import Cards
from api.cards.search import SearchCards
from api.tags.list_master_topics import ListMasterTags, AutoSuggestTags


class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header("Access-Control-Allow-Origin", "*")
        # resp.set_header('Access-Control-Allow-Methods', '*')
        # resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header("Access-Control-Max-Age", 1728000)  # 20 days
        if req.method == "OPTIONS":
            raise HTTPStatus(falcon.HTTP_200, body="\n")


def initialize_routes() -> falcon.API:
    """
    Initialize the falcon api and our router
    :return: an initialized falcon.API
    """

    api = falcon.API(middleware=[HandleCORS()])

    # Routes
    api_version = "/api/v1"

    api.add_route(f"{api_version}/register", Register())
    api.add_route(f"{api_version}/login", Login())
    api.add_route(f"{api_version}/cards", Cards())
    api.add_route(f"{api_version}/cards/search", SearchCards())

    api.add_route(f"{api_version}/tags/master_tags", ListMasterTags())
    api.add_route(f"{api_version}/tags/auto_suggest", AutoSuggestTags())

    return api


def run() -> falcon.API:
    """
    :return: an initialized falcon.API
    """
    # load endpoints

    return initialize_routes()
