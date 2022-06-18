# init env variables
from dotenv import load_dotenv

load_dotenv("./local.env")

import os
import falcon


from falcon.http_status import HTTPStatus
from api.user.register import Register
from api.user.login import Login
from api.cards.cards_actions import (
    CrudCard,
    GetCardsIdsForADekk,
    GetCardById,
    CreateDekk,
    CreateSubDekk,
    CreateTag,
)
from api.user.home import Home
from api.tags.list_master_topics import AutoSuggestTags
from api.user.custom_study import GetCustomStudyMenu, GetCustomStudyCards
from api.resources.get_colleges import Colleges
from api.cards.search import SearchCards, SearchCardsByTags
from api.user.ratings import Ratings
from api.user.bookmark import BookmarkCard, UnmarkCard
from api.user.view import ViewCard
from api.images.on_card import ImagesOnCard


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

    api.add_route(f"{api_version}/register", Register())  # ok
    api.add_route(f"{api_version}/login", Login())  # ok
    api.add_route(f"{api_version}/users/home", Home())  # ok
    api.add_route(f"{api_version}/cards/search", SearchCards())  # ok

    # api.add_route(f"{api_version}/cards/tags", SearchCardsByTags())

    api.add_route(f"{api_version}/tags/all", AutoSuggestTags())  # ok

    api.add_route(f"{api_version}/card", CrudCard())  # CRUD

    api.add_route("/api/v1/card/{card_id}", GetCardById())  # ok

    api.add_route("/api/v1/dekk/", CreateDekk())  # ok
    api.add_route("/api/v1/subdekk/", CreateSubDekk())  # ok
    api.add_route("/api/v1/tag/", CreateTag())  # ok

    api.add_route("/api/v1/dekk/{dekk_id}", GetCardsIdsForADekk())  # ok

    api.add_route("/api/v1/select/dekk", GetCustomStudyMenu())  # ok
    api.add_route("/api/v1/study/dekk", GetCustomStudyCards())  # ok
    api.add_route("/api/v1/ratings/dekk", Ratings())  # ok
    api.add_route("/api/v1/bookmark/card/{card_id}", BookmarkCard())  # ok
    api.add_route("/api/v1/unmark/card/{card_id}", UnmarkCard())  # ok
    api.add_route("/api/v1/view/card/{card_id}", ViewCard())  # ok

    api.add_route(f"{api_version}/resources/colleges", Colleges())  # ok

    api.add_route(f"{api_version}/images/card", ImagesOnCard())  # ok

    return api


def run() -> falcon.API:
    """
    :return: an initialized falcon.API
    """
    # load endpoints

    return initialize_routes()
