import sqlite3
from os import urandom
from hashlib import sha512



class DataLayer:
    def __init__(self):
        self.conn = None
        conn = sqlite3.connect('example.db')
        cur = conn.cursor()
        # create the tables
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT UNIQUE, password BINARY(64), salt BINARY(8));")
        cur.execute("CREATE TABLE IF NOT EXISTS macs (id INTEGER REFERENCES users(id), address TEXT)")

    def queryDB(self, sql, parameters=(), more=False):
        if not self.conn:
            self.conn = sqlite3.connect('example.db')
        cur = self.conn.cursor()
        cur.execute(sql, parameters)
        return cur.fetchone() if not more else cur.fetchall()

    def getUser(self, name, password):
        user = self.queryDB("SELECT * FROM users WHERE name == ?", (name,))

        if not user:
            return user
        print("user is type: {} and looks like {}".format(type(user), user))
        salt = user[3]
        user_hash = user[2]
        pass_hash = sha512(salt + password.encode()).digest()
        print("user and pass hash:\n{}\n{}".format(user_hash, pass_hash))
        if user_hash == pass_hash:
            return user
        return None

    def addUser(self, name, password):
        sha512(password.encode()).digest()
        salt = urandom(8)
        pass_hash = sha512(salt + password.encode()).digest()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO users VALUES (?, ?, ?)", (name, pass_hash, salt))
        self.conn.commit()

    def addMac(self, userId, macAddress):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO macs VALUES (?, ?)", (userId, macAddress))
        self.conn.commit()