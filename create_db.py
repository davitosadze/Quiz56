import sqlite3

conn = sqlite3.connect('blog.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY,
full_name VARCHAR(255) ,
email VARCHAR(255),
password VARCHAR(255)
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS products (
id integer PRIMARY KEY,
user_id integer,
title VARCHAR(255),
location VARCHAR(255),
price VARCHAR(255),
description text,
image_link VARCHAR(255)
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS categories (
id integer PRIMARY KEY,category_name VARCHAR(255))''')
