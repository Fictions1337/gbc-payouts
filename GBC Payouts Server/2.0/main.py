import pymysql  
import pymysql.cursors
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request
from flask import send_file
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery

@app.route('/', methods=['GET'])
def index():
    return "GBC Web API"

@app.route('/client/update')
def client_update():
    version = '2.1'
    return version

@app.route('/client/download')
def download():
    path = "E:/GBC_Payouts_2.1.exe"
    return send_file(path, as_attachment=True)

@app.route('/import/sheet')
def update_database():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

        service = discovery.build('sheets', 'v4', credentials=credentials)
        sheet_id = '1R6_1r9WYXs3hrgwabZDXLlk_f9Z7KAgxjjXFAzAoFt4'
        range_ = '13thNov.Balance!C3:F'

        request = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_)
        response = request.execute()
        connection = mysql.connect()
        cur = connection.cursor()
        records_to_insert = []
        for i in range(len(response['values'])):
            records_to_insert.append(tuple(response['values'][i]))
        cur.execute("TRUNCATE TABLE balance")
        mysql_insert = """INSERT INTO balance (name, pref_realm, paid, balance) VALUES (%s,%s,%s,%s)"""
        cur.executemany(mysql_insert, records_to_insert)
        connection.commit()
        resp = jsonify("Inserted " + str(cur.rowcount) + " rows in the database!")
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cur.close()
        connection.close()

@app.route('/update/sheet')
def update_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

        service = discovery.build('sheets', 'v4', credentials=credentials)
        sheet_id = '1JJAAaYavv_WK9JC0pOe-R0V8S66Kx9itQeTM7FMU6PM'
        
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute("SELECT paid FROM balance")
        data = cur.fetchall()
        mega_list = []
        for row in data:
            mega_list.append([row[0]])
        
        batch_update_values_request_body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
            {
            "range": "13thNov.Balance!E3:E",
            "values": mega_list
            }
        ]
        }
        
        request = service.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body=batch_update_values_request_body)
        response = request.execute()
        
        resp = jsonify("Successfully updated the spreadsheet!")
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cur.close()
        connection.close()

@app.route('/get/all')
def get_all():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM balance HAVING LENGTH(balance)>6")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        for row in rows:
            uid = row['id']
            name = row['name']
            realm = row['pref_realm']
            paid = row['paid']
            balance = row['balance']
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/get/pref_realm')
def get_pref_realm():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT pref_realm FROM balance WHERE LENGTH(pref_realm)!=0")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
          
@app.route('/get/realm/<string:argument>')
def get_realm(argument):
    argument = argument.replace('-', '/')
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM balance WHERE pref_realm=%s HAVING LENGTH(balance)>6", (argument))
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/update/<int:member_id>', methods=['PUT'])
def update_balance(member_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        paid_value = ('TRUE',)
        cursor.execute("UPDATE balance SET paid=%s WHERE id=%s", (paid_value, member_id))
        conn.commit()
        resp = jsonify('User updated successfully!')
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
        
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
		
if __name__ == "__main__":
    app.run()