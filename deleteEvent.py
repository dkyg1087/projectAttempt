from Flask import Blueprint,request,jsonify,abort
from flask_pymongo import PyMongo
from . import get_db

deleteEvent = Blueprint("deleteEvent",__name__)
mongo = get_db()

@deleteEvent.route('/delete-event',methods=['POST'])
def delete():
    stuff = request.json
    eventID = stuff['eventID'] #request.args.get('event_id')
    operation = stuff['operation'] #request.args.get('operation')
    if operation == 'delete':
        requests=mongo.db.requestTable.find_one({'event_id':eventID})
        if requests is not None:
            return jsonify({"status":False,"reason":"You have a request for this event. Please reply first."}) 
        else:
            mongo.db.currentEvent.find_one_and_delete({'event_id':eventID})
        return jsonify({"status":True,"reason":""})
    elif operation == 'drop':
        mongo.db.currentEvent.find_one_and_delete({'event_id':eventID})
        #TODO notify driver and passenger
        #TODO move to passEvent and status "RED"
        return jsonify({"status":True,"reason":""})
    elif operation == 'finish':
        mongo.db.currentEvent.find_one_and_delete({'event_id':eventID})
        #TODO notify driver and passenger
        #TODO move to passEvent and status "GREY"
        return jsonify({"status":True,"reason":""})
    else:
        return abort(500, 'Unknown operation')