CREATE DATABASE flaskapp;
use flaskapp;

create table articles
(
	id bigint auto_increment,
	title varchar(45) null,
	body varchar(9999) null,
	author varchar(45) null,
	constraint id
		unique (id)
);

alter table articles
	add primary key (id);

create table users
(
	name varchar(45) null,
	email varchar(45) null,
	username varchar(45) null,
	password varchar(9999) null
);
