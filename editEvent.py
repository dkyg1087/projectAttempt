from flask import Blueprint,request,jsonify
from . import get_db
from flask_pymongo import PyMongo

mongo = get_db()
editEvent = Blueprint("editEvent",__name__)

@editEvent.route("/alter-event",methods=['POST'])
def edit():
    data=request.json
    eventID=data['event_id']
    requests = mongo.db.request.find_one({"event_id":eventID}) 
    if requests is None:
        return jsonify({'isSuccess':False,'reason':'You have a request for this event. Please reply first.'})
    else:
        data.pop('event_id')
        for stuff in data:
            if stuff == 'acceptable_time_interval':
                userID=mongo.db.currentEvent.find_one({'event_id':eventID})['driver_id']
                userAlert=mongo.db.alertTable.find_one({'user_id':userID})
                alertTime=userAlert['block_time']
                for time in alertTime:
                    if time['event_id']==eventID:
                        time['interval']=stuff['acceptable_time_interval']
                        break
                mongo.db.alertTable.update_one({'user_id':userID},{"$set":{'block_time':alertTime}})
            mongo.db.currentEvent.update_one({"event_id":eventID},{"$set":{stuff:data[stuff]}})
    return jsonify({"status":True,"reason":""})               
    