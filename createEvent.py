from flask import Blueprint,request,jsonify
from flask_pymongo import PyMongo
from . import get_db
import uuid
createEvent=Blueprint("createEvent",__name__)
mongo = get_db()
@createEvent.route("/new-event",methods=['POST'])
def create():
    event=request.json
    try:
        event.pop('request')
        event.pop('user')
        event['event_id']=uuid.uuid4()
    except Exception as e:
        return jsonify({"status":False,"reason":"Event setup failed."})
    try:
        mongo.db.currentEvent.insert_one(event)
    except Exception as e:
        return jsonify({"status":False,"reason":"Database failed to add event."})
    return jsonify({"status":True,"reason":""})

