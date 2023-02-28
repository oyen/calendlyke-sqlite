#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, request, jsonify

import datetime
import os
import re
import sqlite3

dirname = os.path.dirname(__file__)
db_file = os.path.join(dirname, "db\calendlyke.db")
connection = sqlite3.connect(db_file)

app = Flask(__name__)


def create_connection():
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)


# TODO: documentation
# if incomplete parameters?


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    print(user_id)
    with create_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT [UserId], [Name], [Email] from Users WHERE [UserId]=?",
                (user_id,),
            )
            rows = cur.fetchall()
            if rows:
                return jsonify(rows)
        except sqlite3.error as e:
            print(e)
    return jsonify({"error": "data not found"})


@app.route("/users", methods=["POST"])
def add_user():
    name = request.json.get("Name")
    email = request.json.get("Email")
    print(name, email)

    # some data validation
    # is Name at least 3 characters?
    if not name.replace(" ", "").isalpha():
        return jsonify({"error": "Invalid `Name` value provided"})

    # is Email valid?
    # shameless copy-pasta: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if not (re.fullmatch(regex, email)):
        return jsonify({"error": "Invalid `Email` value provided"})

    with create_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO [Users] ([Name], [Email]) VALUES (?, ?)", (name, email)
            )
            new_user_id = cur.lastrowid
            conn.execute(
                "SELECT [UserId], [Name], [Email] from Users WHERE [UserId]=?",
                (new_user_id,),
            )
            rows = cur.fetchall()
            if rows:
                return jsonify(rows)
        except sqlite3.error as e:
            print(e)
    return jsonify({"error": "failed to add new user"})


@app.route("/users/<int:user_id>/schedules", methods=["GET"])
def get_schedules(user_id):
    filter = request.args.get("filter")
    isFree = None
    if(filter is not None and filter == "booked"):
        isFree = 0
    print(user_id)
    with create_connection() as conn:
        try:
            cur = conn.cursor()

            # only show scheduled slots
            if(isFree is not None and not isFree):
                cur.execute(
                "SELECT [Date], [Time], [Name], [Email], [Phone], [Notes] from Schedules WHERE [UserId]=? AND [isFree] = 0",
                (user_id,),
                )
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "Date": row[0],
                        "Time": row[1],
                        "Name": row[2],
                        "Email": row[3],
                        "Phone": row[4],
                        "Notes": row[5]
                    })
                return jsonify(results)
            
            # show all slots for the next 2 weeks
            cur.execute(
                "SELECT [Date], [Time], [isFree] from Schedules WHERE [UserId]=?",
                (user_id,),
            )
            rows = cur.fetchall()

            today = datetime.date.today()
            i = 1
            while i <= 14:
                date = today + datetime.timedelta(days=i)
                # complicated query for Date in Dates
                if str(date) in [r[0] for r in rows]:
                    print("existing", date)
                else:
                    print("new", date)
                    rows.append((str(date), "8:00", 1))
                    rows.append((str(date), "8:30", 1))
                    rows.append((str(date), "9:00", 1))
                    rows.append((str(date), "9:30", 1))
                    rows.append((str(date), "10:00", 1))
                    rows.append((str(date), "10:30", 1))
                    rows.append((str(date), "11:00", 1))
                    rows.append((str(date), "11:30", 1))
                    rows.append((str(date), "12:00", 1))
                    rows.append((str(date), "12:30", 1))
                    rows.append((str(date), "13:00", 1))
                    rows.append((str(date), "13:30", 1))
                    rows.append((str(date), "14:00", 1))
                    rows.append((str(date), "14:30", 1))
                    rows.append((str(date), "15:00", 1))
                    rows.append((str(date), "15:30", 1))
                    rows.append((str(date), "16:00", 1))
                i += 1

            if rows:
                return jsonify(rows)
        except sqlite3.error as e:
            print(e)

        return jsonify({"error": "data not found"})


@app.route("/users/<int:user_id>/schedules", methods=["POST"])
def set_schedule(user_id):
    print(user_id)
    date = request.json.get("Date")
    time = request.json.get("Time")
    name = request.json.get("Name")
    email = request.json.get("Email")
    phone = request.json.get("Phone")
    notes = request.json.get("Notes")
    print(date, time, name, email, phone, notes)

    # some data validation
    # is Name at least 3 characters?
    if not name.replace(" ", "").isalpha():
        return jsonify({"error": "Invalid `Name` value provided"})

    # is Email valid?
    # shameless copy-pasta: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if not (re.fullmatch(regex, email)):
        return jsonify({"error": "Invalid `Email` value provided"})

    # date and time has to be in the future
    input_datetime = datetime.datetime.fromisoformat(date + " " + time)
    print(input_datetime)
    if input_datetime < datetime.datetime.now():
        return jsonify({"error": "Appointment date and time should be in the future"})

    # format phone number
    # format date YYYY-MM-DD
    # format time 24-hr and 30 min increments only
    # set Holidays to not free if free
    # set Weekends to not free if free

    with create_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT [isFree] from Schedules WHERE [UserId]=? AND [Date]=? AND [Time]=?",
                (user_id, date, time),
            )
            isFree = cur.fetchone()
            print('isFree', isFree)
            if isFree is None:
                cur.execute(
                    "INSERT INTO [Schedules] ([UserId], [Date], [Time], [Name], [Email], [Phone], [Notes], [isFree])"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, str(date), time, name, email, phone, notes, 0),
                )
            elif isFree:
                cur.execute(
                    "UPDATE [Schedules] SET "
                    "[Name] = ?,"
                    "[Email] = ?,"
                    "[Phone] = ?,"
                    "[Notes] = ?,"
                    "[isFree] = 0 "
                    "WHERE [UserId]=? AND [Date]=? AND [Time]=?",
                    (name, email, phone, notes, user_id, str(date), time),
                )
            return jsonify({"success": "added appointment"})
        except sqlite3.error as e:
            print(e)
    return jsonify({"error": "failed to add new user"})


@app.route("/users/<int:user_id>/schedules", methods=["DELETE"])
def remove_schedule(user_id):
    print(user_id)
    date = request.json.get("Date")
    time = request.json.get("Time")
    email = request.json.get("Email")
    print(date, time, email)

    with create_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT [isFree] from Schedules WHERE [UserId]=? AND [Date]=? AND [Time]=? AND [Email]=?",
                (user_id, date, time, email),
            )
            isFree = cur.fetchone()
            if isFree is not None:
                cur.execute(
                    "UPDATE [Schedules] SET "
                    "[Name] = '',"
                    "[Email] = '',"
                    "[Phone] = '',"
                    "[Notes] = '',"
                    "[isFree] = 1"
                    "WHERE [UserId]=? AND [Date]=? AND [Time]=? AND [Email]=?",
                    (user_id, str(date), time, email),
                )
            return jsonify({"success": "appointment was cancelled"})
        except sqlite3.error as e:
            print(e)
    # always return success to avoid checking if email exists
    return jsonify({"error": "appointment was cancelled"})


if __name__ == "__main__":
    app.run()
