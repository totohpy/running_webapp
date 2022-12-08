from pymongo import MongoClient
from datetime import datetime

client = None
db = None

def init_db(db_host, db_name, db_user, db_password):
    global client, db
    client = MongoClient(db_host,
                         username=db_user,
                         password=db_password)
    db = client[db_name]

def get_all_posts():
    posts = db.record
    return list(posts.find())

def get_post(object_id):
    posts = db.record
    return posts.find_one({"_id": object_id})

def create_post(date, distance, time, owner):
    posts = db.record
    posts.insert_one({
        'date': date,
        'distance': distance,
        'time': time,
        'owner_id': owner['_id'],
        'owner_username': owner['username'],
        'pace': float(time)/float(distance),
        'speed': float(distance)/(float(time)/60),
        
    })


def delete_post(object_id):
    posts = db.record
    return posts.delete_one({"_id": object_id})

def update_post(object_id, date, distance, time):
    posts = db.record

    updated_values = {
        '$set': {
            'date': date,
            'distance': distance,
            'time' : time,
        }
    }
    posts.update_one({"_id": object_id}, updated_values)

def create_comment(post_object_id, message):
    comments = db.comments
    comments.insert_one({
        'post_id': post_object_id,
        'message': message,
    })

def get_post_comments(object_id):
    comments = db.comments
    return list(comments.find({ 'post_id': object_id }))

def get_user_from_username(username):
    users = db.users
    return users.find_one({ 'username': username })
