import requests
import json
import mysql.connector
from flask import Flask, request

#API From Helius
API_Helius = ""

#Configuration Database
mydb = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)
mycursor = mydb.cursor()

#BOT Telegram Token
TOKEN = ""
#Your Website for Webhook url/webhook
WEBHOOK_URL = ""

# Dictionary untuk melacak langkah-langkah berikutnya dalam percakapan
next_steps = {}

app = Flask(__name__)

def send_message(chat_id, text, reply_markup=None):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    response = requests.post(url, data=data)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhok():
    update_data = request.get_json()
    handle_callback(update_data)
    return update_data, 200

@app.route('/', methods=['GET'])
def index():
    return 'Running:)', 200

def send_start(chat_id):
    teks = 'Welcome to Solana NFT Notifier, just add your wallets and relax we will notif you every your wallet makes a move on Solana.\n\n Choose commands below and follow the steps:'
    markup = {
        "inline_keyboard": [
            [{"text": "Add", "callback_data": "/add"}],
            [{"text": "Delete", "callback_data": "/delete"}],
            [{"text": "Show", "callback_data": "/show"}]
        ]
    }
    send_message(chat_id, teks, markup)

def handle_callback(update):
    if 'chat_id' in next_steps and 'callback_query' not in update:
        text = update['message']['text'].split(' ',1)
        chat_id = update['message']['chat']['id']
        step = next_steps['chat_id']
        if step == "add_wallet":
            add_wallet(chat_id, text[0], text[1])
        elif step == "delete_wallet":
            delete_wallet(chat_id, text, next_steps['result'])
            
    if 'callback_query' not in update:
        chat_id = update['message']['chat']['id']
        send_start(chat_id)
    else:
        callback_query = update['callback_query']
        chat_id = callback_query['message']['chat']['id']
        callback_data = callback_query['data']

        if "/add" in callback_data:
            markup = {
                "inline_keyboard": [[{"text": "Back", "callback_data": "/back"}]]
            }
            send_message(chat_id, "Send your wallet address and name wallet\nexample : AiUeO Wallet1", markup)
            next_steps['chat_id'] = "add_wallet"
        elif "/start" in callback_data:
            send_start(chat_id)
        elif "/delete" in callback_data:
            # do delete logic
            markup = {
                "inline_keyboard": [[{"text": "Back", "callback_data": "/back"}]]
            }
            sql = f"SELECT * FROM notif WHERE id_tele = '{chat_id}'"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            teks = "Your Wallet Address : \n\n"
            for i in range(len(result)):
                teks += f"{i+1}. {result[i][2]}\n"
            send_message(chat_id, teks)
            send_message(chat_id, "Choose number you want to delete : ", markup)
            next_steps['chat_id'] = "delete_wallet"
            next_steps['result'] = result
        elif "/show" in callback_data:
            # do show logic
            markup = {
                "inline_keyboard": [[{"text": "Back", "callback_data": "/back"}]]
            }
            sql = f"SELECT * FROM notif WHERE id_tele = '{chat_id}'"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            teks = "Your Wallet Address : \n\n"
            for i in range(len(result)):
                teks += f"{i+1}. {result[i][2]} - {result[i][3]}\n"
            send_message(chat_id, teks, markup)
            next_steps['chat_id'] = "show_wallet"
        elif "/back" in callback_data:
            del next_steps['chat_id']
            send_start(chat_id)

def add_wallet(chat_id, address, name):
    url_webhook = f"{WEBHOOK_URL}/{chat_id}"
    sql_check = f"SELECT * FROM notif WHERE id_tele = '{chat_id}'"
    mycursor.execute(sql_check)
    res = mycursor.fetchall()

    if len(res) > 0:
        # existing logic
        try:
            new_address = [res[i][2] for i in range(len(res))]
            new_address.append(address)
            url = f"https://api.helius.xyz/v0/webhooks/{res[0][5]}?api-key={API_Helius}"
            headers = {"Content-Type":"application/json"}
            data = {"webhookURL": url_webhook,
            "transactionTypes": ["Any"],
            "accountAddresses": new_address,
            "webhookType": "enhanced"}
            req = requests.put(url, data=json.dumps(data), headers=headers)
            if req.status_code == 200:
                webID = req.json()["webhookID"]
                sql = "INSERT INTO notif (id_tele, wallet_address, name_wallet, url_webhook, id_webhook) VALUES (%s, %s, %s, %s, %s)"
                val = (chat_id, address, name, url_webhook, webID)
                mycursor.execute(sql, val)
                mydb.commit()
                send_message(chat_id, "Wallet Address succesfully added.")
                send_start(chat_id)
            else:
                print(req.json())
        except Exception as e:
            print(e)
    else:
        # new logic
        try:
            url = f"https://api.helius.xyz/v0/webhooks?api-key={API_Helius}"
            headers = {"Content-Type":"application/json"}
            data = {"webhookURL": url_webhook,
            "transactionTypes": ["Any"],
            "accountAddresses": [address],
            "encoding": "jsonParsed",
            "webhookType": "enhanced"}
            
            req = requests.post(url, data=json.dumps(data), headers=headers)
            if req.status_code == 200:
                webID = req.json()["webhookID"]
                sql = "INSERT INTO notif (id_tele, wallet_address, name_wallet, url_webhook, id_webhook) VALUES (%s, %s, %s, %s, %s)"
                val = (chat_id, address, name, url_webhook, webID)
                mycursor.execute(sql, val)
                mydb.commit()
                send_message(chat_id, "Wallet Address succesfully added.")
                send_start(chat_id)
            else:
                print(req.json())
        except Exception as e:
            print(e)
    
    del next_steps['chat_id']

def delete_wallet(chat_id, text, result):
    number = text
    url_webhook = f"{WEBHOOK_URL}/{chat_id}"
    if number.isdigit() and int(number) > 0 and int(number) <= len(result):
        sql = f"DELETE FROM notif WHERE wallet_address = '{result[int(number)-1][2]}'"
        mycursor.execute(sql)
        mydb.commit()
        sql_check = f"SELECT * FROM notif WHERE id_tele = '{chat_id}'"
        mycursor.execute(sql_check)
        res = mycursor.fetchall()
        try:
            url = f"https://api.helius.xyz/v0/webhooks/{res[0][4]}?api-key={API_Helius}"
            headers = {"Content-Type":"application/json"}
            data = {"webhookURL": url_webhook,
            "transactionTypes": ["Any"],
            "accountAddresses": [res[i][2] for i in range(len(res))],
            "webhookType": "enhanced"}
            req = requests.put(url, data=json.dumps(data), headers=headers)
            if req.status_code == 200:
                send_message(chat_id, "Wallet Address has been delete.")
                send_start(chat_id)
            else:
                send_message(chat_id, "Sorry can't add your address, please contact support.")
        except Exception as e:
            print(e)
    else:
        send_message(chat_id, "Please choose number correctly.")
    del next_steps['chat_id']
    del next_steps['result']

@app.route('/webhook/<idtele>', methods=['POST'])
def webhook(idtele):
    data = request.get_json()[0]
    teks = data['description']
    if "compressed" in teks:
        getId = data['events']['compressed'][0]['assetId']
        teks = cek_nft(getId)
        send_message(idtele, teks)
    else:
        send_message(idtele, teks)
    return '', 200

def cek_nft(address):
    url = f"https://rpc.helius.xyz/?api-key={API_Helius}"
    headers = {"Content-Type":"application/json"}
    data = {
      "jsonrpc": "2.0",
      "id": "my-id",
      "method": "getAsset",
      "params": {
        "id": address
      }
    }
            
    req = requests.post(url, data=json.dumps(data), headers=headers).json()
    sql_check = f"SELECT * FROM notif WHERE wallet_address = '{req['result']['ownership']['owner']}'"
    mycursor.execute(sql_check)
    res = mycursor.fetchone()
    teks = f"Your Address : {req['result']['ownership']['owner']}\nName Wallet : {res[3]}\n\nName : {req['result']['content']['metadata']['name']}\nSymbol : {req['result']['content']['metadata']['symbol']}\n"
    for i in req['result']['content']['metadata']['attributes']:
        if i['trait_type'] == 'rarity' or i['trait_type'] == 'Rarity':
            teks += f"Rarity : {i['value']}\n"
    return teks

if __name__ == "__main__":
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    app.run(host='127.0.0.1', port=80, debug=True)