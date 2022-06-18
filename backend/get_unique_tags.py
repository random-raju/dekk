import glob
import hashlib
import json
import re

from utils import postgres

# from dotenv import load_dotenv

DB_OBJ = postgres.QueryManager("user_content", "tags", db_req="TEST")
# load_dotenv("../../local.env")


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


def clean_tag_name(tag):

    tag = re.sub(r":", " ", tag)
    tag = re.sub(r"disease$", "diseases", tag)
    tag = re.sub(r"disorder$", "disorders", tag)
    tag = re.sub(r"^\W+", "", tag).strip()

    return tag


def clean_folder_names(file):

    file = file.replace(".txt", "")
    file = file.replace("./data_verified\\", "")
    file = file.replace(".\data_verified\\", "")
    file = file.replace("./data_verified/", "")
    file = file.replace("./data_verified", "")

    return file


def get_tags(item):

    if re.search(r"(?<=Tags:)(.*)(?=Content on front)", item):
        tags = re.search(r"(?<=Tags:)(.*)(?=Content on front)", item).group()
        tags = tags.split(",")
        tags = [clean_tag_name(i) for i in tags]
        return tags
    else:
        return []


def get_subtopics(item):

    if re.search(r"(?<=Title)(.*)(?=Tags:)", item):
        subtopic = re.search(r"(?<=Title)(.*)(?=Tags)", item).group()
        subtopic = clean_tag_name(subtopic)
        return subtopic
    else:
        return None


def create_tag_row(tag, tag_type):

    tag_row = {"account_id": 1, "tag_name": tag}
    tag_id = get_hash_for_tags(tag_row)
    tag_row["tag_id"] = tag_id
    tag_row["tag_type"] = tag_type

    return tag_row


def insert_tag(db_obj, tag_row):

    try:
        rowcount = db_obj.pg_handle_insert(tag_row)
        if rowcount > 0:
            status = True
        else:
            status = False
    except:
        status = False

    return status


def clean_flashcard(item):

    item = re.sub(r"\n", " ", item)
    item = re.sub(r"\r", " ", item)
    item = re.sub(r"Tags( )?:( )?", "Tags:", item)
    item = re.sub(r"Title( )?:( )?", "Title:", item)

    return item


for file in glob.glob("./data_verified/*"):
    """
    """
    # if 'Biochemistry' not in file:
    #     continue

    data = open(file).read()
    data = re.split(r"===+", data)
    file = clean_folder_names(file)
    main_tags = file.split(" - ")
    tags = []
    sub_topics = []
    for item in data:
        if "not adding" in item:
            continue

        item = clean_flashcard(item)
        card_tags = get_tags(item)
        tags = tags + card_tags

        sub_topic = get_subtopics(item)
        if sub_topic and sub_topic not in sub_topics:
            sub_topics.append(sub_topic)

    master = main_tags[0]
    master_row = create_tag_row(master, "master")
    master_row["parent_topic_hash"] = master_row["tag_id"]
    master_row["is_master_topic"] = True
    master_row["field"] = "Medical"

    sub_master = main_tags[1]
    sub_master_row = create_tag_row(sub_master, "submaster")
    sub_master_row["parent_topic_hash"] = master_row["tag_id"]
    sub_master_row["is_master_topic"] = False
    sub_master_row["field"] = "Medical"

    insert_tag(DB_OBJ, master_row)
    insert_tag(DB_OBJ, sub_master_row)

    sub_topics = [i.strip() for i in sub_topics if i.strip()]
    tags = [i.strip() for i in tags if i.strip()]

    for subtopic in sub_topics:
        subtopic_row = create_tag_row(subtopic, "subtopic")
        subtopic_row["parent_topic_hash"] = sub_master_row[
            "tag_id"
        ]  # grouped to submaster
        subtopic_row["is_master_topic"] = False
        subtopic_row["field"] = "Medical"
        insert_tag(DB_OBJ, subtopic_row)

    for tag in tags:
        tag_row = create_tag_row(tag, "tag")
        tag_row["parent_topic_hash"] = sub_master_row["tag_id"]  # grouped to submaster
        tag_row["is_master_topic"] = False
        tag_row["field"] = "Medical"
        insert_tag(DB_OBJ, tag_row)
