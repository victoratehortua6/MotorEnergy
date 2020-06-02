CREATE SEQUENCE id_users_seq START 1 INCREMENT BY 1;
CREATE TABLE users (
	id INT NOT NULL DEFAULT nextval('id_users_seq'::regclass),
	f_name VARCHAR(30) NOT NULL,
	s_name VARCHAR(30) NULL,
	f_last_name VARCHAR(30) NOT NULL,
	s_last_name VARCHAR(30) NULL,
	email VARCHAR(80) NOT NULL,
	creation TIMESTAMP NOT NULL DEFAULT NOW()::TIMESTAMP,
	password VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
);