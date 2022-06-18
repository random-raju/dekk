"""
Sample API calls:
    GET - http://127.0.0.1:8000/api/v1/cards/search?q=Infectivity of Hepatitis&offset=0

"""
import json
import re

import falcon
import spacy
from api.user import authorization
from utils import http_response
from utils import postgres

KEYS_TO_DROP = [
    "account_id",
    "for_search",
    "source_link",
    "master_topic",
    "search_tokens",
]

sp = spacy.load("en_core_web_sm")
all_stopwords = sp.Defaults.stop_words


def construct_tags_query(query_string):

    query = ""

    if "tag:" in query_string:
        tags_query = re.search(r"tag:(.*)", query_string).group()
        tags = tags_query.split("tag:")
        tags = [i.strip().lower() for i in tags if i.strip()]
    else:
        tags = []

    for tag in tags:
        tag = tag.lower()
        query += f" tags ? '{tag}' AND"

    query = re.sub(r" AND$", " ", query).strip()

    return query


def construct_free_text_query(query_string):
    """
        todo - improve relevance
    """

    query = ""
    query_string = re.sub(r"tag:(.*)", "", query_string).strip()
    query_string = re.sub(r"[\W]", " ", query_string)
    clean_string = re.sub(r"\s{2,}", " ", query_string).strip()

    hp_tokens = clean_string.split(" ")
    hp_tokens = [
        token.strip().lower() for token in hp_tokens if token.strip() and len(token) > 1
    ]

    hp_tokens = [word for word in hp_tokens if not word in all_stopwords]

    for token in hp_tokens:
        token = token.lower()
        query += f" for_search ilike '%{token}%' OR"

    query = re.sub(r" OR$", " ", query).strip()

    return query


def get_cards_by_tags_and_tokens(db_conn, query_string, offset):
    """
        todo count
    """
    query = f"""
        SELECT * FROM  user_content.cards
    """

    query_string = query_string.lower()
    query_string = query_string.replace("'", " ")
    query_string = query_string.replace('"', " ")

    offset = offset.strip()
    try:
        offset = int(offset)
    except:
        msg = f"Invalid query parameters , can't convert offset to int"
        raise falcon.HTTPBadRequest("Bad request", msg)

    tags_query = construct_tags_query(query_string)
    free_text_query = construct_free_text_query(query_string)

    print(tags_query)
    print(free_text_query)

    if tags_query and free_text_query:
        query += " WHERE " + tags_query + " AND " + "(" + free_text_query + ")"
    elif tags_query and not free_text_query:
        query += " WHERE " + tags_query
    elif not tags_query and free_text_query:
        query += " WHERE " + free_text_query
    else:
        return {}

    query = query + f" OFFSET {offset} LIMIT 10"

    query_result = db_conn.fetch_query_direct_query(query)
    cards_found = len(query_result)

    for result in query_result:
        for key in KEYS_TO_DROP:
            result.pop(key, None)

    if cards_found:
        total_cards = get_total_count_cards_by_tags_and_tokens(db_conn, query_string)
        response = {
            "cards_count": cards_found,
            "total_cards": total_cards,
            "page": f"{int(offset // 10) + 1}/{total_cards//10 + 1}",
            "results": query_result,
        }
    else:
        response = {
            "message": "No more cards for you",
            "results": [],
            "cards_count": 0,
            "total_cards": 0,
        }

    return response


def get_total_count_cards_by_tags_and_tokens(db_conn, query_string):
    """
        todo count
    """
    query = f"""
        SELECT count(*) FROM  user_content.cards
    """

    query_string = query_string.lower()
    query_string = query_string.replace("'", " ")
    query_string = query_string.replace('"', " ")

    tags_query = construct_tags_query(query_string)
    free_text_query = construct_free_text_query(query_string)

    print(tags_query)
    print(free_text_query)

    if tags_query and free_text_query:
        query += " WHERE " + tags_query + " AND " + "(" + free_text_query + ")"
    elif tags_query and not free_text_query:
        query += " WHERE " + tags_query
    elif not tags_query and free_text_query:
        query += " WHERE " + free_text_query
    else:
        return {}

    query_result = db_conn.fetch_query_direct_query(query)

    if query_result and query_result[0]["count"]:
        count = query_result[0]["count"]
    else:
        count = 0

    return count


def get_cards_by_tags(db_conn, tags, offset):
    """
        todo count
    """
    query = f"""
        SELECT * FROM  user_content.cards
    """

    if not tags:
        return {}

    offset = offset.strip()
    try:
        offset = int(offset)
    except:
        msg = f"Invalid query parameters , can't convert offset to int"
        raise falcon.HTTPBadRequest("Bad request", msg)

    tags_where_clause = " "
    for tag in tags:
        tags_where_clause += f"tags ->>'{tag.lower()}' is not null or "

    tags_where_clause = re.sub(" or$", " ", tags_where_clause.strip())
    tags_where_clause = " WHERE " + tags_where_clause

    # print(tags_where_clause)

    query = query + tags_where_clause + f" OFFSET {offset} LIMIT 10"
    # print(query)

    query_result = db_conn.fetch_query_direct_query(query)
    cards_found = len(query_result)

    relevant_tags = []
    for result in query_result:
        for key in KEYS_TO_DROP:
            result.pop(key, None)

        if result["tags"]:
            for tag in result["tags"]:
                relevant_tags.append(tag)

    relevant_tags = list(set(relevant_tags))

    response = {
        "total_cards_found": cards_found,
        "tags": relevant_tags,
        "results": query_result,
    }

    return response


class SearchCardsByTags:
    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp):

        if "q" in req.params and "offset" in req.params:
            query_string = req.params["q"]
            try:
                tags = json.loads(query_string)
            except:
                msg = f"Invalid query parameters , can't convert query string to list"
                raise falcon.HTTPBadRequest("Bad request", msg)

            offset = req.params["offset"]
            query_result = get_cards_by_tags(self.db_conn, tags, offset)

            http_response.ok(resp, query_result)
        else:
            error_message = "Something went wrong"
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)


class SearchCards:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp):
        if "q" in req.params and "offset" in req.params:
            query_string = req.params["q"]
            offset = req.params["offset"]
            query_result = get_cards_by_tags_and_tokens(
                self.db_conn, query_string, offset
            )

            http_response.ok(resp, query_result)
        else:
            error_message = "Something went wrong"
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
