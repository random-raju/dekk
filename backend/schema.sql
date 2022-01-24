

drop table IF EXISTS user_content.cards cascade ;
drop table IF EXISTS user_content.tags_cards cascade;
drop table IF EXISTS user_content.tags cascade;

drop table IF EXISTS users.activity_log cascade;
drop table IF EXISTS users.accounts cascade;
drop table IF EXISTS users.ratings cascade;
drop table IF EXISTS users.sessions cascade;

drop schema IF EXISTS users;
drop schema IF EXISTS user_content;

create schema users;
create schema user_content;

CREATE TABLE users.accounts (
	account_id int4 NOT NULL GENERATED ALWAYS AS IDENTITY,
	created_at timestamp without time zone default (now() at time zone 'utc'),
	last_active timestamp without time zone default (now() at time zone 'utc'),
	user_name varchar NULL,
	full_name varchar NULL,
	email varchar NULL,
	"password" varchar NULL,
	college varchar null,
	is_admin boolean null,
	user_type varchar null,
	CONSTRAINT accounts_pkey PRIMARY KEY (account_id),
	CONSTRAINT email_unique_constraint UNIQUE (email),
	CONSTRAINT user_name_unique_constraint UNIQUE (user_name)
);
CREATE UNIQUE INDEX email_unique_index ON users.accounts USING btree (lower((email)::text));
CREATE UNIQUE INDEX user_name_unique_index ON users.accounts USING btree (lower((user_name)::text));

insert into users.accounts(user_name,full_name,email,password,is_admin,user_type)
values ('admin','admin','admin@dekk.in',md5('welcometothejungle'),true,'admin');

CREATE TABLE user_content.cards (
	card_id varchar NOT NULL,
	account_id int4 NULL,
	title varchar NULL,
	content_on_front varchar NULL,
	content_on_back varchar NULL,
	highlighted_keywords jsonb NULL,
	"permission" varchar NULL,
	"type" varchar NULL,
	image_links jsonb NULL,
	source_link varchar NULL,
	for_search text NULL,
	search_tokens TSVECTOR,
	created_at timestamp NULL DEFAULT timezone('utc'::text, now()),
	updated_at timestamp NULL DEFAULT timezone('utc'::text, now()),
	CONSTRAINT pk_card_id PRIMARY KEY (card_id),
	CONSTRAINT fk_card_and_user FOREIGN KEY (account_id) REFERENCES users.accounts(account_id)
);

CREATE TABLE user_content.tags (
	tag_id varchar NOT NULL,
	account_id int4  not null,
	field varchar NULL,
	tag_name varchar NULL,
	is_master_topic bool default false,
	created_at timestamp NULL DEFAULT timezone('utc'::text, now()),
	updated_at timestamp NULL DEFAULT timezone('utc'::text, now()),
	parent_topic_hash varchar null,
	tag_type varchar null,
	CONSTRAINT pk_dekk_id PRIMARY KEY (tag_id),
	CONSTRAINT fk_tag_and_user FOREIGN KEY (account_id) REFERENCES users.accounts(account_id),
	CONSTRAINT fk_tags_tags FOREIGN KEY (parent_topic_hash) REFERENCES user_content.tags(tag_id)
);

CREATE TABLE user_content.tags_cards (
	card_id varchar not NULL,
	tag_id varchar not NULL,
	UNIQUE (card_id,tag_id),
	CONSTRAINT fk_tags_cards_tags FOREIGN KEY (tag_id) REFERENCES user_content.tags(tag_id)
);

CREATE TABLE users.activity_log (
	account_id int4 NOT NULL,
	session_id varchar not null,
	card_id varchar not null,
	no_of_cards int not null,
	viewed boolean null,
	bookmarked boolean null,
	views int null,
	created_at timestamp NULL DEFAULT timezone('utc'::text, now()),
	updated_at timestamp NULL DEFAULT timezone('utc'::text, now()),
	UNIQUE (account_id,card_id),
	CONSTRAINT fk_us_accounts_ua_accounts FOREIGN KEY (account_id) REFERENCES users.accounts(account_id)
);

CREATE TABLE users.ratings (
	id varchar null,
	account_id int4 NOT NULL ,
	rating numeric NULL,
	dekk_id varchar NULL,
	comments varchar null,
	created_at timestamp without time zone default (now() at time zone 'utc'),
	updated_at timestamp without time zone default (now() at time zone 'utc'),
	UNIQUE (id),
	CONSTRAINT fk_user_and_ratings FOREIGN KEY (account_id) REFERENCES users.accounts(account_id),
	CONSTRAINT fk_user_and_dekk FOREIGN KEY (dekk_id) REFERENCES user_content.tags(tag_id)
);

CREATE TABLE users.sessions (
	account_id int4 NOT NULL ,
	session_id varchar not null,
	user_agent varchar not null,
	host varchar not null,
	is_active boolean not null,
	created_at timestamp without time zone default (now() at time zone 'utc'),
	updated_at timestamp without time zone default (now() at time zone 'utc'),
	CONSTRAINT fk_user_and_sessions FOREIGN KEY (account_id) REFERENCES users.accounts(account_id),
	UNIQUE (account_id,is_active)
);



-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','infectious-diseases',true,1,md5('1medicalinfectious-diseases'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','cardiovascular-system',true,1,md5('1medicalcardiovascular-system'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','respiratory-system',true,1,md5('1medicalrespiratory-system'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','kidney-and-urinary-tract',true,1,md5('1medicalkidney-and-urinary-tract'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','rheumatology-and-immunology',true,1,md5('1medicalrheumatology-and-immunology'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','neurology',true,1,md5('1medicalneurology'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','endocrinology',true,1,md5('1medicalendocrinology'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','biochemistry',true,1,md5('1medicalbiochemistry'));
-- insert into user_content.tags (field,tag_name,is_master_topic,created_by_id,tag_hash) values
-- ('Medical','hemat-oncology',true,1,md5('1medicalhemat-oncology'));
