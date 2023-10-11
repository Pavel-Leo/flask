CREATE TABLE IF NOT EXISTS mainmenu (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    url text NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    id integer PRIMARY KEY AUTOINCREMENT,
    username character(250) NOT NULL,
    phone integer(13) NOT NULL,
    created_at timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS category (
    id integer PRIMARY KEY AUTOINCREMENT,
    name character(250) NOT NULL,
    slug character(250) NOT NULL,
    created_at timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id integer PRIMARY KEY AUTOINCREMENT,
    category_id integer NOT NULL,
    name character  NOT NULL,
    slug text NOT NULL,
    image VARCHAR  NOT NULL,
    description text NOT NULL,
    price text NOT NULL,
    available boolean NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    username character(250) NOT NULL,
    email character(250) NOT NULL,
    password character(250) NOT NULL,
    created_at timestamp NOT NULL
);