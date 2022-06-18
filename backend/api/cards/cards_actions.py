"""
Sample API calls:
    GET - http://127.0.0.1:8000/api/v1/dekk/204af12a0bb2a5bbdf80e6b6b77bd64b
    GET - http://127.0.0.1:8000/api/v1/dekk/204af12a0bb2a5bbdf80e6b6b77bd64b
    POST - http://127.0.0.1:8000/api/v1/dekk
            {
                "dekk_name": "abc"
            }

    GET - http://127.0.0.1:8000/api/v1/card/14894d5c75aef72bac20535917c339dd
"""
import hashlib
import json
import os
import re

import falcon
import jwt
from api.user import authorization
from deepdiff import DeepDiff
from psycopg2.errors import ForeignKeyViolation
from psycopg2.errors import UniqueViolation
from utils import http_response
from utils import postgres

HASH_KEYS_CARDS = [
    "title",
    "content_on_front",
    "content_on_back",
    "account_id",
]


def card_difference(og_card, current_card):

    og_card.pop("highlighted_keywords", None)
    og_card.pop("permission", None)
    og_card.pop("type", None)
    og_card.pop("tags", None)
    og_card.pop("image_links", None)
    og_card.pop("card_id", None)
    og_card.pop("dekk_id", None)

    difference = DeepDiff(og_card, current_card)
    updated_fields = []
    for key in difference:
        for col_key in difference[key].keys():
            updated_fields.append((col_key.split("['")[1].split("']")[0]))

    return updated_fields


def tags_difference(og_tags, current_tags):

    difference = DeepDiff(og_tags, current_tags)
    updated_fields = []

    for key in difference:
        for col_key in difference[key].keys():
            updated_fields.append((col_key.split("['")[1].split("']")[0]))

    return updated_fields


def get_hash_for_cards(data_dict, hsh_keys):
    """
	Create hash of the string of (location_value, court_value)
	"""

    # Asserting hsh_keys is not empty
    assert hsh_keys

    # Asserting no duplicates
    assert len(hsh_keys) == len(set(hsh_keys))

    # Asserting that hash creation is clean to avoid mishaps
    assert set(hsh_keys).issubset(data_dict.keys())

    # Next, create hash in a generalized way
    data_dict_to_hash = {
        k: str(v).lower() for k, v in data_dict.items() if k in hsh_keys
    }
    string_to_hash = json.dumps(data_dict_to_hash, sort_keys=True, default=str)
    hashed = hashlib.md5(string_to_hash.encode()).hexdigest()

    return hashed


def get_hash_for_tags(data_dict):
    """
	Create hash of the string of (location_value, court_value)
	"""

    # Next, create hash in a generalized way
    data_dict_to_hash = {k: str(v).lower() for k, v in data_dict.items()}
    string_to_hash = json.dumps(data_dict_to_hash, sort_keys=True, default=str)
    data_dict_to_hash = json.loads(string_to_hash)
    str_to_hash = ""
    for key in data_dict_to_hash:
        str_to_hash += data_dict_to_hash[key]

    hashed = hashlib.md5(str_to_hash.encode()).hexdigest()

    return hashed


def get_all_card_ids_for_a_dekk(db_conn, tag_id):

    card_ids_query = f"""
        SELECT t1.title,t1.card_id,t1.content_on_front FROM user_content.cards t1 inner join user_content.tags_cards t2
        on t1.card_id = t2.card_id
        where t2.tag_id = '{tag_id}'
        order by t1.title
    """
    card_ids_result = db_conn.fetch_query_direct_query(card_ids_query)

    dekk_name_query = f"""
        SELECT tag_name as dekk_name FROM user_content.tags
        where tag_id = '{tag_id}'
        limit 1
    """

    dekk_name_result = db_conn.fetch_query_direct_query(dekk_name_query)

    tags_query = f"""
        SELECT tag_name,tag_id FROM user_content.tags
        where parent_topic_hash = '{tag_id}' and tag_id != '{tag_id}'
    """

    tags_query_result = db_conn.fetch_query_direct_query(tags_query)

    if dekk_name_result and dekk_name_result[0]["dekk_name"]:
        result = {
            "dekk_name": dekk_name_result[0]["dekk_name"],
            "dekk_id": tag_id,
            "tags": tags_query_result,
            "cards": card_ids_result,
        }
    else:
        raise Exception("Opps ids did not match")
    return result


def get_card_by_id(db_conn, card_id):

    card_ids_query = f"""
        SELECT
            title,content_on_front,content_on_back,
            highlighted_keywords,permission,type,image_links,card_id
         FROM user_content.cards
        where card_id = '{card_id}'
        limit 1
    """
    result = db_conn.fetch_query_direct_query(card_ids_query)

    if result:
        tags = get_card_and_its_tags(db_conn, card_id)
        result[0]["tags"] = []

        for item in tags:
            if item["is_master_topic"] == True:
                result[0]["dekk_id"] = item["tag_id"]
            else:
                result[0]["tags"].append(item["tag_id"])

    return result


def get_card_and_its_tags(db_conn, card_id):

    card_ids_query = f"""
        select t1.tag_id,t2.is_master_topic,t2.tag_type,t2.tag_name from user_content.tags_cards t1 inner join user_content.tags t2 on
        t1.tag_id = t2.tag_id and
        t1.card_id = '{card_id}'
    """
    result = db_conn.fetch_query_direct_query(card_ids_query)

    return result


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


def create_card(db_conn, req):
    """
        Has to create new tags and upload
    """
    req_data = req.media

    req_data = req_data

    if not req_data:
        return {}

    card_dict = {}

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    if not req_data.get("title", ""):
        error_message = "Something went wrong , seems like the tittle is empty"
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "new_tags" not in req_data:
        error_message = "Something went wrong , seems new_tags is not in request body"
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "selected_tag_ids" not in req_data:
        error_message = (
            "Something went wrong , seems selected_tag_ids is not in request body"
        )
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "dekk_id" not in req_data:
        error_message = "Something went wrong , seems dekk_id is not in request body"
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "content_on_front" not in req_data:
        error_message = (
            "Something went wrong , seems content_on_front is not in request body"
        )
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "content_on_back" not in req_data:
        error_message = (
            "Something went wrong , seems content_on_back is not in request body"
        )
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    card_dict["account_id"] = decode["account_id"]
    card_dict["title"] = req_data["title"]
    card_dict["content_on_front"] = req_data["content_on_front"]
    card_dict["content_on_back"] = req_data["content_on_back"]

    for_search = (
        card_dict["title"]
        + " "
        + card_dict["content_on_front"]
        + " "
        + card_dict["content_on_back"]
    )
    for_search = re.sub(r"\s{2,}", " ", for_search).strip()
    for_search = re.sub(r"_", " ", for_search).strip()
    for_search = re.sub(r"\W", " ", for_search).strip()
    for_search = re.sub(r"\r", " ", for_search).strip().lower()
    card_dict["for_search"] = re.sub(r"\s{2,}", " ", for_search).strip().lower()

    card_dict["card_id"] = get_hash_for_cards(card_dict, HASH_KEYS_CARDS)

    new_tags = []  # to be inserted to user_content.tags

    for tag in req_data["new_tags"]:
        dict_ = {
            "tag_name": tag.strip(),
            "account_id": card_dict["account_id"],
        }
        dict_["tag_id"] = get_hash_for_tags(dict_)
        dict_["tag_type"] = "tag"
        dict_["parent_topic_hash"] = req_data["dekk_id"]

        new_tags.append(dict_)

    tags_cards = []  # to be inserted to user_content.tags_cards
    for tag in new_tags:
        dict_ = {"card_id": card_dict["card_id"], "tag_id": tag["tag_id"]}
        tags_cards.append(dict_)

    dekk_dict = {"card_id": card_dict["card_id"], "tag_id": req_data["dekk_id"]}
    tags_cards.append(dekk_dict)

    for tag in req_data["selected_tag_ids"]:
        dict_ = {"card_id": card_dict["card_id"], "tag_id": tag}
        tags_cards.append(dict_)

    # print(new_tags)
    # print('=--------------------')
    # print(tags_cards)
    # print('=--------------------')
    # print(card_dict)
    # print('=--------------------')

    for tag in new_tags:  # add new tags to tags
        try:
            db_conn.table = "tags"
            status = db_conn.pg_handle_insert(tag)
            if status == 0:
                raise Exception("Oops something went wrong could not create new tag")
        except UniqueViolation as e:
            # print(e)
            pass
        except Exception as e:
            raise e
    try:
        cursor = db_conn.conn_obj.cursor
        cursor.execute("BEGIN")
        try:  # add card
            db_conn.table = "cards"
            status = db_conn.pg_handle_insert(card_dict, commit=False)
        except UniqueViolation as e:
            raise Exception(
                "Oops something went wrong could not create new card - looks like same card already exists"
            )
        except Exception as e:
            raise e

        for tags_card in tags_cards:  # add tags_cards
            try:
                db_conn.table = "tags_cards"
                status = db_conn.pg_handle_insert(tags_card, commit=False)
            except UniqueViolation as e:
                print(e)
                pass
            except Exception as e:
                raise e
        cursor.execute("COMMIT")
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(e)
        raise Exception(
            "Oops something went wrong could not create new card - looks like same card already exists"
        )

    return True


def create_dekk(db_conn, req):

    req_data = req.media

    req_data = req_data

    if not req_data:
        return {}

    dekk_dict = {}

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    if not req_data["dekk_name"]:
        message = "Couldn't create dekk , empty name"
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    dekk_dict["account_id"] = decode["account_id"]
    dekk_dict["tag_name"] = req_data["dekk_name"]

    hash_ = get_hash_for_tags(dekk_dict)
    dekk_dict["tag_id"] = hash_
    dekk_dict["parent_topic_hash"] = hash_
    dekk_dict["is_master_topic"] = True
    dekk_dict["tag_type"] = "master"
    dekk_dict["field"] = "Medical"

    try:
        status = db_conn.pg_handle_insert(dekk_dict)
        if status == 0:
            message = "Couldn't create dekk"
            raise falcon.HTTPBadRequest("Oops something when wrong", message)
        else:
            return dekk_dict["tag_id"]
    except Exception as e:
        # print(e)
        # print(dir(e))
        if e.pgcode == "42P01":
            message = "Couldn't create dekk"
            raise falcon.HTTPBadRequest("Oops something when wrong", message)
        if str(e.pgcode) == "23505":
            message = f'Dekk name `{req_data["dekk_name"]}` already exists'
            raise falcon.HTTPBadRequest("Oops something when wrong", message)

        message = f'Dekk name `{req_data["dekk_name"]}` already exists'
        raise falcon.HTTPBadRequest("Oops something when wrong", message)


def create_subdekk(db_conn, req):

    req_data = req.media

    req_data = req_data

    if not req_data:
        return {}

    dekk_dict = {}

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    if not req_data["sub_master_name"]:
        message = "Couldn't create sub dekk , empty name"
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if not req_data["master_dekk_id"]:
        message = "Couldn't create sub dekk , master_dekk_id"
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    dekk_dict["account_id"] = decode["account_id"]
    dekk_dict["tag_name"] = req_data["sub_master_name"]

    hash_ = get_hash_for_tags(dekk_dict)
    dekk_dict["tag_id"] = hash_
    dekk_dict["tag_type"] = "submaster"
    dekk_dict["field"] = "Medical"
    dekk_dict["parent_topic_hash"] = req_data["master_dekk_id"]

    try:
        status = db_conn.pg_handle_insert(dekk_dict)
        if status == 0:
            message = "Couldn't create subdekk"
            raise falcon.HTTPBadRequest("Oops something when wrong", message)
        else:
            return (dekk_dict["tag_id"], dekk_dict["parent_topic_hash"])
    except Exception as e:
        # print(e)
        # print(dir(e))
        if e.pgcode == "42P01":
            message = "Couldn't create subdekk"
            raise falcon.HTTPBadRequest("Oops something when wrong", message)
        if str(e.pgcode) == "23505":
            message = f'Subdekk name `{req_data["dekk_name"]}` already exists'
            raise falcon.HTTPBadRequest("Oops something when wrong", message)

        message = f'Subdekk name `{req_data["dekk_name"]}` already exists'
        raise falcon.HTTPBadRequest("Oops something when wrong", message)


def create_tag(db_conn, req):

    req_data = req.media

    req_data = req_data

    if not req_data:
        return {}

    dekk_dict = {}

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    if not req_data["tag_name"]:
        message = "Couldn't create sub dekk , empty name"
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if not req_data["master_dekk_id"]:
        message = "Couldn't create sub dekk , master_dekk_id"
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    dekk_dict["account_id"] = decode["account_id"]
    dekk_dict["tag_name"] = req_data["tag_name"]

    hash_ = get_hash_for_tags(dekk_dict)
    dekk_dict["tag_id"] = hash_
    dekk_dict["tag_type"] = "tag"
    dekk_dict["field"] = "Medical"
    dekk_dict["parent_topic_hash"] = req_data["master_dekk_id"]

    try:
        status = db_conn.pg_handle_insert(dekk_dict)
        if status == 0:
            message = "Couldn't create subdekk"
            raise falcon.HTTPBadRequest("Oops something when wrong", message)
        else:
            return (dekk_dict["tag_id"], dekk_dict["parent_topic_hash"])
    except Exception as e:
        # print(e)
        # print(dir(e))
        if e.pgcode == "42P01":
            message = "Couldn't create subdekk"
            raise falcon.HTTPBadRequest("Oops something when wrong", message)
        if str(e.pgcode) == "23505":
            message = f'Subdekk name `{req_data["dekk_name"]}` already exists'
            raise falcon.HTTPBadRequest("Oops something when wrong", message)

        message = f'Subdekk name `{req_data["dekk_name"]}` already exists'
        raise falcon.HTTPBadRequest("Oops something when wrong", message)


def delete_card(db_conn, req, card_id):

    cursor = db_conn.conn_obj.cursor

    try:
        cursor = db_conn.conn_obj.cursor
        cursor.execute("BEGIN")
        cursor.execute(
            "DELETE FROM user_content.tags_cards WHERE card_id = %s;", (card_id,)
        )
        cursor.execute("DELETE FROM user_content.cards WHERE card_id = %s;", (card_id,))
        if int(cursor.rowcount) > 0:
            cursor.execute("COMMIT")
            return True
        else:
            cursor.execute("ROLLBACK")
            return False
    except:
        raise Exception("Failed to delete card and its tags")


def edit_card(db_conn, req):
    """
        todo:
            must be able to edit only theirs

    """
    req_data = req.media

    req_data = req_data

    if not req_data:
        return {}

    card_dict = {}

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    if not req_data.get("title", ""):
        error_message = "Something went wrong , seems like the tittle is empty"
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    # if "new_tags" not in req_data:
    #     error_message = "Something went wrong , seems new_tags is not in request body"
    #     message = {"message": error_message}
    #     raise falcon.HTTPBadRequest("Oops something when wrong", message)

    # if "selected_tag_ids" not in req_data:
    #     error_message = (
    #         "Something went wrong , seems selected_tag_ids is not in request body"
    #     )
    #     message = {"message": error_message}
    #     raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "dekk_id" not in req_data:
        error_message = "Something went wrong , seems dekk_id is not in request body"
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "content_on_front" not in req_data:
        error_message = (
            "Something went wrong , seems content_on_front is not in request body"
        )
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "content_on_back" not in req_data:
        error_message = (
            "Something went wrong , seems content_on_back is not in request body"
        )
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    if "card_id" not in req_data:
        error_message = "Something went wrong , seems card_id is not in request body"
        message = {"message": error_message}
        raise falcon.HTTPBadRequest("Oops something when wrong", message)

    card_dict["title"] = req_data["title"]
    card_dict["content_on_front"] = req_data["content_on_front"]
    card_dict["content_on_back"] = req_data["content_on_back"]

    selected_tag_ids = req_data.pop("selected_tag_ids", None)
    dekk_id = req_data.pop("dekk_id", None)
    new_tags = req_data.pop("new_tags", None)
    card_id = req_data.pop("card_id", None)

    for_search = (
        card_dict["title"]
        + " "
        + card_dict["content_on_front"]
        + " "
        + card_dict["content_on_back"]
    )
    for_search = re.sub(r"\s{2,}", " ", for_search).strip()
    for_search = re.sub(r"_", " ", for_search).strip()
    for_search = re.sub(r"\W", " ", for_search).strip()
    for_search = re.sub(r"\r", " ", for_search).strip().lower()

    # compare cards
    og_card = get_card_by_id(db_conn, card_id)

    updated_card_fields = card_difference(og_card[0], card_dict)
    # print(updated_card_fields)
    card_dict["account_id"] = decode["account_id"]

    card_dict["for_search"] = re.sub(r"\s{2,}", " ", for_search).strip().lower()
    card_dict["card_id"] = card_id

    # get updated fields
    if updated_card_fields:
        updated_card = {}
        for key in updated_card_fields:
            updated_card[key] = card_dict[key]

        updated_card["card_id"] = card_id
    else:
        updated_card = {}

    # compare tags
    tags = get_card_and_its_tags(db_conn, card_id)
    og_tags = [tag["tag_id"] for tag in tags]

    edited_new_tags = []  # to be inserted to user_content.tags

    for tag in new_tags:
        dict_ = {
            "tag_name": tag.strip(),
            "account_id": card_dict["account_id"],
        }
        dict_["tag_id"] = get_hash_for_tags(dict_)
        dict_["tag_type"] = "tag"
        dict_["parent_topic_hash"] = dekk_id

        edited_new_tags.append(dict_)

    tags_cards = []  # to be inserted to user_content.tags_cards
    for tag in edited_new_tags:
        dict_ = {"card_id": card_dict["card_id"], "tag_id": tag["tag_id"]}
        tags_cards.append(dict_)

    dekk_dict = {"card_id": card_dict["card_id"], "tag_id": dekk_id}
    tags_cards.append(dekk_dict)

    for tag in selected_tag_ids:
        dict_ = {"card_id": card_dict["card_id"], "tag_id": tag}
        tags_cards.append(dict_)

    for tag in edited_new_tags:  # add new tags to tags
        try:
            db_conn.table = "tags"
            status = db_conn.pg_handle_insert(tag)
            if status == 0:
                raise Exception("Oops something went wrong could not create new tag")
        except UniqueViolation as e:
            # print(e)
            pass
        except Exception as e:
            raise e

    try:
        cursor = db_conn.conn_obj.cursor
        cursor.execute("BEGIN")
        if new_tags or selected_tag_ids:
            cursor.execute(
                "DELETE FROM user_content.tags_cards WHERE card_id = %s;", (card_id,)
            )
        try:  # update card
            if updated_card:
                db_conn.table = "cards"
                status = status = db_conn.pg_handle_update(
                    updated_card, "card_id", commit=False
                )
            else:
                pass  # no changes to card edit only tags
        except Exception as e:
            print(e)
            raise e

        for tags_card in tags_cards:  # add tags_cards
            try:
                db_conn.table = "tags_cards"
                status = db_conn.pg_handle_insert(tags_card, commit=False)
            except UniqueViolation as e:
                print(e)
                pass
            except Exception as e:
                raise e
        cursor.execute("COMMIT")
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(e)
        raise Exception(
            "Oops something went wrong could not create new card - looks like same card already exists"
        )

    return True


class CreateSubDekk:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "tags")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        try:
            subdekk_id, dekk_id = create_subdekk(self.db_conn, req)
            http_response.ok(
                resp,
                {
                    "message": "Created subdekk",
                    "dekk_id": dekk_id,
                    "subdekk_id": subdekk_id,
                },
            )
        except Exception as e:
            raise e


class CreateTag:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "tags")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        try:
            tag_id, dekk_id = create_tag(self.db_conn, req)
            http_response.ok(
                resp, {"message": "Created tag", "dekk_id": dekk_id, "tag_id": tag_id}
            )
        except Exception as e:
            raise e


class CreateDekk:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "tags")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        try:
            dekk_id = create_dekk(self.db_conn, req)
            http_response.ok(resp, {"message": "Created the dekk", "dekk_id": dekk_id})
        except Exception as e:
            raise e


class CrudCard:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        try:
            create_card(self.db_conn, req)
            http_response.ok(resp, {"message": "Created the card"})
        except Exception as e:
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)

    # @falcon.before(authorization.request_valiation)
    def on_put(self, req, resp):
        try:
            edit_card(self.db_conn, req)
            http_response.ok(resp, {"message": "Edited the card"})
        except Exception as e:
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)


class GetCardsIdsForADekk:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp, dekk_id):
        if dekk_id:
            try:
                tag_id = dekk_id  # dekk id  is tag id
                query_result = get_all_card_ids_for_a_dekk(self.db_conn, tag_id)
                http_response.ok(resp, query_result)
            except:
                error_message = "Something went wrong , id didnt match"
                message = {"message": error_message}
                http_response.err(resp, falcon.HTTP_500, message)
        else:
            error_message = "Something went wrong , you have to pass dekk_id in url"
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)


class GetCardById:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp, card_id):
        query_result = get_card_by_id(self.db_conn, card_id)

        if card_id:  # dekk id is tag id
            try:
                query_result = get_card_by_id(self.db_conn, card_id)
                http_response.ok(resp, query_result)
            except:
                error_message = "Something went wrong , id didnt match"
                message = {"message": error_message}
                http_response.err(resp, falcon.HTTP_500, message)
        else:
            error_message = "Something went wrong , you have to pass card_id in url"
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)

    # @falcon.before(authorization.request_valiation)
    def on_delete(self, req, resp, card_id):
        try:
            result = delete_card(self.db_conn, req, card_id)
            if result:
                http_response.ok(resp, {"message": "Delete the card"})
            else:
                message = {"message": "Nothing with this card id"}
                http_response.err(resp, falcon.HTTP_400, message)
        except Exception as e:
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
