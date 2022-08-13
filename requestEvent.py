from flask import Blueprint,request,jsonify
from . import get_db
from flask_pymongo import PyMongo
from datetime import datetime as dt,timedelta
requestEvent = Blueprint("requestEvent",__name__)
mongo = get_db()

def rejectPeople(userID,eventID,reason="Others are picked,not you."):
    userRejectList=mongo.db.reject_collection.find_one({'user_id':userID})
    if userRejectList is None:
        mongo.db.reject_collection.insert_one({'user_id':userID,"rejected_event_list":[{"event_id":eventID,"reason":reason}]})
    else:
        rejectEventList=userRejectList["rejected_event_list"]
        for rejectEvent in rejectEventList:
            if rejectEvent["event_id"]==eventID:
                return
        rejectEventList.append({'event_id':eventID,"reason":reason})
        mongo.db.reject_collection.update_one({'user_id':userID},{'$set':{'rejected_event_list':rejectEventList}})
    return

def deleteAlert(userID,eventID):
    userAlertList=mongo.db.alert_collection.find_one({'user_id':userID})['block_time']
    for i in range(len(userAlertList)):
        if userAlertList[i]['event_id']==eventID:
            userAlertList.pop(i)
            break
    mongo.db.alert_collection.update_one({'user_id':userID},{'$set':{'block_time':userAlertList}})

@requestEvent.route('/request',methods=['POST'])
def requestAdd():
    requestObj = request.json
    if  mongo.db.current_collection.find_one({'event_id':requestObj['event_id']}) is None:
        return jsonify({"isSuccess":False,"reason":"You are requesting a none existing event."})    
    if mongo.db.request_collection.find_one({'event_id':requestObj['event_id'],"user_id":requestObj['user_id']}) is not None:
        return 
    mongo.db.request_collection.insert_one(requestObj)
    userID = requestObj['user_id']
    formatString = "%Y-%m-%d %H:%M"
    actualTime = dt.strptime(requestObj['actual_time'],formatString)
    startTime = (actualTime-timedelta(minutes=10)).strftime(formatString)
    endTime = (actualTime+timedelta(minutes=10)).strftime(formatString)
    timeInterval=[startTime,endTime]
    driverAlert=mongo.db.alert_collection.find_one({'user_id':userID})
    if driverAlert is not None:
        blockTime=driverAlert['block_time']
        blockTime.append({"event_id":requestObj['event_id'],"interval":timeInterval})
        mongo.db.alert_collection.update_one({'user_id':userID},{"$set":{'block_time':blockTime}})
    else:
        alert={'user_id':userID,
               'block_time':[
                {"event_id":requestObj['event_id'],"interval":timeInterval}
               ]}
        mongo.db.alert_collection.insert_one(alert)
    #TODO infrom event driver
    return jsonify({"isSuccess":True,"reason":""})

@requestEvent.route('/accept-request',methods=['POST'])
def requestAccept():
    requestObj = request.form
    eventID= requestObj['event_id']
    userID= requestObj['user_id']
    requests=mongo.db.request_collection.find_one({'event_id':eventID,"user_id":userID})
    mongo.db.current_collection.update_one({"event_id":eventID},{"$set":{"final_request":requests,"passenger_id":userID,"status":"green"}})
    #TODO set user info on current Event
    mongo.db.request_collection.delete_one({'event_id':eventID,"user_id":userID})
    userRequest = mongo.db.request_collection.find({'event_id':eventID})
    for user in userRequest:
        userID=user["user_id"]
        rejectPeople(userID,eventID)
        deleteAlert(userID,eventID)
        #delete alert time for every user.
    mongo.db.request_collection.delete_many({'event_id':eventID})
    #TODO delete other request from request table and inform others 
    #TODO add all other request to reject table and add reason
    #TODO inform driver and passenger
    #TODO remove other's alert time
    return jsonify({"isSuccess":True,"reason":""})

@requestEvent.route('/reject-event',methods=['POST'])
def requestReject():
    requestObj = request.form
    eventID= requestObj['event_id']
    userID= requestObj['user_id']
    reason = requestObj['reason']
    rejectPeople(userID,eventID,reason)
    deleteAlert(userID,eventID)
    mongo.db.request_collection.find_one_and_delete({"event_id":eventID,"user_id":userID})
    return jsonify({"isSuccess":True,"reason":""})