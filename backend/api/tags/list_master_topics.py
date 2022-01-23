"""
Sample API calls:
    GET - http://127.0.0.1:8000/api/v1/tags

"""
import hashlib

import falcon
from api.user import authorization
from utils import http_response
from utils import postgres

KEYS_TO_DROP_IN_MASTER_TOPICS = [
    "created_by_id",
    "tag_hash",
]


def get_all_unique_tags_on_cards(db_conn):

    query = f"""
        select tag_id, tag_name , parent_topic_hash as dekk_id  from user_content.tags
        order by tag_name
    """

    query_result = db_conn.fetch_query_direct_query(query)

    output = []
    # for result in query_result:
    #     if "tag" in result:
    #         output.append(result["tag"].lower())

    return query_result


class AutoSuggestTags:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp):

        query_result = get_all_unique_tags_on_cards(self.db_conn)

        if not query_result:
            error_message = "Something went wrong"
            message = {"message": error_message}
            http_response.err(resp, "500", message)
        elif query_result:
            http_response.ok(resp, query_result)
        else:
            error_message = "Something went wrong"
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
