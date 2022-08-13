from flask import Blueprint,request,jsonify
from flask_pymongo import PyMongo
from setup import get_db
import uuid
createEvent=Blueprint("createEvent",__name__)
mongo = get_db()
@createEvent.route("/new-event",methods=['POST'])
def create():
    event=request.json
    try:
        event.pop('request')
        event.pop('user')
        event['event_id']=str(uuid.uuid4())
    except Exception as e:
        return jsonify({"isSuccess":False,"reason":"Event setup failed."})
    try:
        mongo.db.current_collection.insert_one(event)
    except Exception as e:
        return jsonify({"isSuccess":False,"reason":"Database failed to add event."})
    try:
        driverID = event['driver_id']
        driverAlert=mongo.db.alert_collection.find_one({'user_id':driverID})
        if driverAlert is not None:
            blockTime=driverAlert['block_time']
            blockTime.append({"event_id":event['event_id'],"interval":event['acceptable_time_interval']})
            mongo.db.alert_collection.update_one({'user_id':driverID},{"$set":{'block_time':blockTime}})
        else:
            alert={'user_id':driverID,
                   'block_time':[
                    {"event_id":event['event_id'],"interval":event['acceptable_time_interval']}
                   ]}
            mongo.db.alert_collection.insert_one(alert)
    except Exception as e:
        return jsonify({"isSuccess":False,"reason":"Database failed to add alert."})
    return jsonify({"isSuccess":True,"reason":""})

