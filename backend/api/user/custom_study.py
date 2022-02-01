"""
Sample API calls:
    GET - http://127.0.0.1:8000/api/v1/select/dekk

    POST - http://127.0.0.1:5000/api/v1/study/dekk
    {
        "cards_count": 100,
        "ids": ["cd888b33d7219a2a970f855aabb01cde", "204af12a0bb2a5bbdf80e6b6b77bd64b"],
        "offset": 10
    }

"""
import os

import falcon
import jwt
from api.user import authorization
from utils import http_response
from utils import postgres
from utils.add_cards import get_hash
from utils.add_cards import HASH_KEYS


def load_all_curated_content(db_obj, account_id):

    query = f"""
        INSERT INTO users.activity_log (id ,account_id ,card_id, views)
        SELECT md5(concat({account_id},card_id)),{account_id}, card_id, 0 FROM user_content.cards ON CONFLICT DO NOTHING

    """
    db_obj.conn_obj.cursor.execute(query)
    db_obj.conn_obj.conn.commit()


def get_cards_by_tags(db_conn, tag_ids, offset):

    id_clause = [f"'{id}'" for id in tag_ids]
    id_clause = ",".join(id_clause)

    query = f"""
            SELECT
            t1.title,t1.content_on_front,t1.content_on_back,
            t1.highlighted_keywords,t1.permission,t1.type,
            t1.image_links,t1.card_id
            FROM
                    user_content.cards t1
                INNER JOIN
                    users.activity_log t2 ON
                t1.card_id = t2.card_id
            WHERE
                t1.card_id IN
                (
                    SELECT card_id FROM user_content.tags_cards
                    WHERE tag_id IN ( {id_clause} ) ORDER BY random()
                )
            ORDER BY t2.views ASC OFFSET {offset} LIMIT 10
            """

    session_cards = db_conn.fetch_query_direct_query(query)

    return session_cards


def get_study_cards(db_conn, req):

    req_data = req.media

    req_data = req_data

    if not req_data:
        return {}

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    account_id = decode["account_id"]
    session_id = decode["session_id"]

    offset = req_data["offset"]
    cards_count = req_data["cards_count"]
    tag_ids = req_data["ids"]

    load_all_curated_content(db_conn, account_id)

    if offset >= cards_count:
        response = {
            "session_id": session_id,
            "total_cards_to_study": cards_count,
            "total_cards_given": 0,
            "cards": [],
        }

        return response

    study_session_cards = get_cards_by_tags(db_conn, tag_ids, offset)

    response = {
        "session_id": session_id,
        "total_cards_to_study": cards_count,
        "total_cards_given": len(study_session_cards) + offset,
        "cards": study_session_cards,
    }

    return response


def create_custom_study_menu(db_conn, req):

    env = os.environ.get(f"ENV")
    secret = os.environ.get(f"SECRET_{env}")
    token = req.headers.get("AUTHORIZATION")
    decode = jwt.decode(token, secret, verify="False", algorithms=["HS256"])

    master_topics_query = f"""
        select count(*) as cards_count,t1.tag_name as dekk_name ,t1.tag_id as dekk_id from user_content.tags t1 inner join
        user_content.tags_cards t2 on t1.tag_id = t2.tag_id
        where  t1.is_master_topic = true
        and t1.tag_type = 'master' and t1.account_id = 1
        group by t1.tag_name,t1.tag_id
        order by count(*) desc
    """
    master_topics_ids = db_conn.fetch_query_direct_query(master_topics_query)

    custom_study_tree = []

    for id in master_topics_ids:
        dekk_id = id["dekk_id"]
        dekk_tree = {
            "cards_count": id["cards_count"],
            "dekk_id": dekk_id,
            "dekk_name": id["dekk_name"],
        }

        if decode["account_id"] == 1:
            dekk_tree["is_owner"] = True
        else:
            dekk_tree["is_owner"] = False

        submaster_query = f"""select count(*) as cards_count,t1.tag_name,t1.tag_id from user_content.tags t1 full join
        user_content.tags_cards t2 on t1.tag_id = t2.tag_id
        where t1.parent_topic_hash = '{dekk_id}' and t1.tag_id !='{dekk_id}'
        and t1.tag_type = 'submaster'
        group by t1.tag_name,t1.tag_id
        order by count(*) desc
        """

        submaster_results = db_conn.fetch_query_direct_query(submaster_query)
        for result in submaster_results:
            if dekk_tree["is_owner"] == True:
                result["is_owner"] = True
            else:
                result["is_owner"] = False

        dekk_tree["sub_dekks"] = submaster_results

        for sub_dekk in dekk_tree["sub_dekks"]:
            subtopics_query = f"""select count(*) as cards_count,t1.tag_name,t1.tag_id from user_content.tags t1 inner join
            user_content.tags_cards t2 on t1.tag_id = t2.tag_id
            where t1.parent_topic_hash = '{dekk_id}' and t1.tag_id !='{dekk_id}'
            and t1.tag_type = 'subtopic'
            group by t1.tag_name,t1.tag_id
            order by count(*) desc
            """
            subtopics_results = db_conn.fetch_query_direct_query(subtopics_query)
            for result in subtopics_results:
                if dekk_tree["is_owner"] == True:
                    result["is_owner"] = True
                else:
                    result["is_owner"] = False
            sub_dekk["sub_topics"] = subtopics_results

        custom_study_tree.append(dekk_tree)

    return custom_study_tree


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


class GetCustomStudyMenu:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_get(self, req, resp):
        try:
            result = create_custom_study_menu(self.db_conn, req)
            http_response.ok(resp, result)
        except Exception as e:
            print(e)
            error_message = "Something went wrong"
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)


class GetCustomStudyCards:
    """
        Request data has to be a json
    """

    def __init__(self) -> None:
        self.db_conn = postgres.QueryManager("user_content", "cards")

    # @falcon.before(authorization.request_valiation)
    def on_post(self, req, resp):
        try:
            # req.params["ids"] = req.params.get("ids", 30)
            # req.params["session_id"] = req.params.get("session_id", None)
            # req.params["cards_count"] = req.params.get("cards_count", 30)
            result = get_study_cards(self.db_conn, req)
            http_response.ok(resp, result)
        except Exception as e:
            print(e)
            error_message = str(e)
            message = {"message": error_message}
            http_response.err(resp, falcon.HTTP_500, message)
