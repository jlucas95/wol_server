import sqlite3
from itertools import groupby
import os
from hashlib import sha512
import subprocess

DB_NAME = 'data.db'
if os.name == "posix":
    import python_arptable as arp_table


class DataLayer:
    def __init__(self):
        self.conn = None
        setup = False
        try:
            f = open("data.db")
            f.close()
        except FileNotFoundError:
            setup = True

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # create the tables
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT UNIQUE, password BINARY(64), salt BINARY(8), admin BOOLEAN DEFAULT 0);")
        cur.execute("CREATE TABLE IF NOT EXISTS macs (id INTEGER REFERENCES users(id), address TEXT)")
        conn.commit()

        if setup:
            pass_hash, salt = self.hash_salt("root")
            cur.execute("INSERT INTO Users(name, password, salt, admin) VALUES (?, ?, ?, ?)", ("root", pass_hash, salt, 1))
            conn.commit()

        conn.close()

    def queryDB(self, sql, parameters=(), more=False):
        if not self.conn:
            self.conn = sqlite3.connect(DB_NAME)
        cur = self.conn.cursor()
        cur.execute(sql, parameters)
        return cur.fetchone() if not more else cur.fetchall()

    def getUser(self, name, password):
        user = self.queryDB("SELECT * FROM users WHERE name == ?", (name,))

        if not user:
            return user
        salt = user[3]
        user_hash = user[2]
        pass_hash = sha512(salt + password.encode()).digest()
        if user_hash == pass_hash:
            return user
        return None

    def hash_salt(self, password):
        salt = os.urandom(8)
        pass_hash = sha512(salt + password.encode()).digest()
        return pass_hash, salt

    def updateUserPassword(self, id, password):
        pass_hash, salt = self.hash_salt(password)
        self.updateUser(id, ["password", "salt"],[pass_hash, salt])


    def updateUser(self, id, columns : iter, values: iter):
        if len(columns) != len(values):
            raise ValueError("length of columns and values is not the same")
        values.append(id)
        columns = [x + "=?"for x in columns]
        query = "UPDATE Users SET {} WHERE id = ?".format(",".join(columns),values)
        print(query)
        self.queryDB(query, values)
        self.conn.commit()

    def addUser(self, name, password, admin=False):
        pass_hash, salt = self.hash_salt(password)
        self.queryDB("INSERT INTO users(name, password, salt, admin) VALUES (?, ?, ?, ?)", (name, pass_hash, salt, admin))
        self.conn.commit()

    def addMac(self, userId, macAddress):
        self.queryDB("INSERT INTO macs VALUES (?, ?)", (userId, macAddress))
        self.conn.commit()

    def getMacs(self, userId):
        return self.queryDB("SELECT address FROM macs WHERE id == ?", (userId,), True)

    def get_arp_windows(self):
        output = subprocess.check_output(["arp", "-a"]).decode().split("\r\n", )
        output = [x for x in output if len(x) != 0]
        rows = [x.split(" ") for x in output]
        for i in range(len(rows)):
            rows[i] = [x for x in rows[i] if len(x) != 0]

        interfaces = []
        interface = None
        for i in range(len(rows)):
            row = rows[i]
            if "Interface" in row[0]:
                interface = {"name": row[1], "entries": []}
                interfaces.append(interface)
            elif row[0][0].isnumeric():
                interface["entries"].append(row)
        return interfaces

    def get_arp_linux(self):
        data = arp_table.get_arp_table()

        x = groupby(data, lambda x: x['Device'])
        processed = [
            {"name": interface[0], "entries": [
                {key[1]: entry[key[0]] for key in [("IP address", "ip"), ("HW address", "mac")]}
                for entry in interface[1]
            ]
             } for interface in x]
        return processed

    def get_arp(self):
        if os.name == "posix":
            return self.get_arp_linux()
        elif os.name == "nt":
            return self.get_arp_windows()
        else:
            return []  # panic!

    def validate_password(self, name, pw):
        return self.getUser(name, pw) is not None
