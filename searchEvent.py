from flask import Flask,BluePrint,jsonify,request
from flask_pymongo import PyMongo
from . import get_db
mongo = get_db()
searchEvent=BluePrint("searchEvent",__name__)

@searchEvent.route('/query-event',methods=['GET'])
def query():
    paramList=['user_id','driver_name','start','end','time','is_helmet','is_free']
    db_filter={}   
    for i in range(2,7):
        val=request.args.get(paramList[i])
        if val is not None:
            db_filter[paramList[i]]=val
    result=mongo.db.currentEvent.find(db_filter)
    rejectList=mongo.db.rejectTable.find_one({'user_id':request.args.get(paramList[0])})


    