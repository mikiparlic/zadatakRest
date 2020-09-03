import os
from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)

array = []
calculations = []

users = [
    {"username": "admin",
     "password": "adminPass"},
    {"username": "user1",
     "password": "user1Pass"},
    {"username": "user2",
     "password": "user2Pass"},
    {"username": "user3",
     "password": "user3Pass"}
]
user = ''
file = 'history.txt'

def id_number():
    id = 0
    global file
    f = open(file, 'r')
    for line in f:
        id += 1
    f.close()
    return id

def read_file(id):
    global user
    global file
    results = []
    history = []
    f = open(file, 'r')
    lines = f.readlines()
    for line in lines:
        if '\n' in line:
            line = line[:-1]
        if user != 'admin':
            parts = line.split('|')
            if parts[3] == user:
                history.append(line)
        else:
            history.append(line)
    for item in history:
        parts = item.split('|')
        data = {}
        data['id'] = parts[0]
        data['array'] = parts[1]
        data['calculations'] = parts[2]
        if id != None:
            if id == data['id']:
                results.append(data)
                break
        else:
            results.append(data)
    return results

def write_file(history):
    global file
    file_size = os.path.getsize(file)
    try:
        file = open(file, 'a')
        if file_size != 0:
            file.writelines("\n")
        file.writelines(str(history))
        return 0
    except Exception as e:
        return 1
    finally:
        file.close()

@app.route('/add', methods=['POST'], defaults={'add': None})
@app.route('/add/<add>', methods=['POST'])
@auth.login_required()
def add(add):
    if add == None:
        abort(400)
    global array
    values= add.split(',')
    for item in values:
        try:
            item = int(item)
            array.append(int(item))
        except Exception as e:
            print ('Item {}, can not be cast to string, skipping!'.format(item))
    return jsonify({'201 Added new value': array}), 201

@app.route('/calculate', methods=['GET'])
@auth.login_required()
def calculate():
    global array
    global calculations
    if len(array) == 0:
        abort(412)
    calculation = sum(array)
    calculations.append(calculation)
    return jsonify({'200 Calculated value from array': calculation}), 200

@app.route('/reset', methods=['POST'])
@auth.login_required()
def reset():
    global user
    global array
    global calculations
    id = id_number()
    if id != 0:
        id = id + 1
    else:
        id = 1
    print (id)
    history = '{0}|{1}|{2}|{3}'.format(id,array,calculations,user)
    responce = write_file(history)
    if responce == 0:
        array.clear()
        calculations.clear()
        return jsonify({'Code 202 Reseted values': 'Reseted Array and Results'}), 202
    else:
        abort(500)

@app.route('/history', methods=['GET'], defaults={'id': None})
@app.route('/history/<id>', methods=['GET'])
@auth.login_required()
def history(id):
    history = read_file(id)
    if len(history) > 0:
        return jsonify({'Code 200 Retreved history': history}), 200
    else:
        return jsonify({'Code 204 No Content': 'No Content'}), 204

@app.route('/home')
def home():
    return 'Main Route'

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'Error': 'Code 400 Bad Requst'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Code 404 No results found'}), 404)

@app.errorhandler(412)
def precondition_failed(error):
    return make_response(jsonify({'Error': 'Code 412 No elements in array'}), 412)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'Error': 'Code 500 Internal Server Error'}), 500)

@auth.get_password
def get_password(username):
    password = None
    global user
    global users
    for item in users:
        if item['username'] == username:
            password = item['password']
    if password == None:
        return None
    else:
        user = username
        return password

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'Error': 'Code 401 Unauthorized access'}), 401)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='6767')