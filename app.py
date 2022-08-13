from setup import create_app,get_db
from werkzeug.security import generate_password_hash,check_password_hash
from flask import jsonify

app = create_app()
mongo = get_db()
@app.route('/add-pass/<string:userID>/<string:password>')
def add_password(userID,password):
    mongo.db.auth_collection.insert_one({"userID":userID, "password":generate_password_hash(password)})
    return jsonify({"status":"OK"})
@app.route('/check-pass/<string:userID>/<string:password>')
def check_password(userID,password):
    print(password)
    pwd = mongo.db.auth_collection.find_one({"userID":userID})
    if pwd != None:
        print(check_password_hash(pwd['password'],password))
    return jsonify({"status":"OK"})
app.run()