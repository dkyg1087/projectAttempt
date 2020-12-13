from flask import Blueprint,request,jsonify
from . import get_db
from flask_pymongo import PyMongo

requestEvent = Blueprint("requestEvent",__name__)
mongo = get_db()

def rejectPeople(userID,eventID,reason="Others are picked,not you."):
    userRejectList=mongo.db.rejectTable.find_one({'user_id':userID})
    if userRejectList is None:
        mongo.db.rejectTable.insert_one({'user_id':userID,"rejected_event_list":[{"event_id":eventID,"reason":reason}]})
    else:
        rejectEventList=userRejectList["rejected_event_list"]
        rejectEventList.append({'event_id':eventID,"reason":reason})
        mongo.db.rejectTable.update_one({'user_id':userID},{'$set':{'rejected_event_list':rejectEventList}})
    return

def deleteAlert(userID,eventID):
    mongo.db.alertTable.find_one({'user_id':userID})
@requestEvent.route('/request',methods=['POST'])
def requestAdd():
    requestObj = request.json
    if  mongo.db.currentEvent.find_one({'event_id':requestObj['event_id']}) is None:
        return jsonify({"status":False,"reason":"You are requesting a none existing event."})    
    mongo.db.requestTable.insert_one(requestObj)
    #TODO infrom event driver
    return jsonify({"status":True,"reason":""})

@requestEvent.route('/accept-request',methods=['POST'])
def requestAccept():
    requestObj = request.json
    eventID= requestObj['event_id']
    userID= requestObj['user_id']
    requests=mongo.db.requestTable.find_one({'event_id':eventID,"user_id":userID})
    mongo.db.currentEvent.update_one({"event_id":eventID},{"$set":{"final_request":requests}})
    mongo.db.requestTable.delete_one({'event_id':eventID,"user_id":userID})
    userRequest = mongo.db.requestTable.find({'event_id':eventID})
    for user in userRequest:
        userID=user["user_id"]
        rejectPeople(userID,eventID)
        #delete alert time for every user.
    mongo.db.requestTable.delete_many({'event_id':eventID})
    #TODO delete other request from request table and inform others 
    #TODO add all other request to reject table and add reason
    #TODO inform driver and passenger
    #TODO remove other's alert time
    return jsonify({"status":True,"reason":""})

@requestEvent('/reject-event',methods=['POST'])
def requestReject():
    requestObj = request.json
    eventID= requestObj['event_id']
    userID= requestObj['user_id']
    reason = requestObj['reason']
    rejectPeople(userID,eventID,reason)
    jsonify({"status":True,"reason":""})