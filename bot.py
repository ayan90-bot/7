import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_ID
from admin_utils import *
from flask import Flask, request
import threading

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# States for tracking user input
user_states = {}

# Main Menu Keyboard
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Redeem Request", "Buy Premium")
    keyboard.row("Service", "Dev")
    return keyboard

# Service Keyboard
def service_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Prime Video", "Spotify", "Crunchyroll", "Turbo VPN", "Hotspot Shield VPN", "Back"]
    keyboard.add(*buttons)
    return keyboard

# Admin commands
@bot.message_handler(commands=['start'])
def start_msg(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "You are banned from using this bot.")
        return
    bot.send_message(user_id, f"Welcome {message.from_user.first_name}!", reply_markup=main_keyboard())

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace("/broadcast ", "")
    for user in get_all_users():
        try:
            bot.send_message(int(user), text)
        except:
            pass
    bot.reply_to(message, "Broadcast sent.")

@bot.message_handler(commands=['ban'])
def ban(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "You don't have permission.")
        return
    try:
        user_id = int(message.text.split()[1])
        ban_user(user_id)
        bot.reply_to(message, f"Banned user {user_id}")
    except:
        bot.reply_to(message, "Usage: /ban user_id")

@bot.message_handler(commands=['unban'])
def unban(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "You don't have permission.")
        return
    try:
        user_id = int(message.text.split()[1])
        unban_user(user_id)
        bot.reply_to(message, f"Unbanned user {user_id}")
    except:
        bot.reply_to(message, "Usage: /unban user_id")

@bot.message_handler(commands=['genk'])
def gen_key(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        days = int(parts[1])
        import secrets
        key = secrets.token_hex(5)
        add_premium_key(key, days)
        bot.reply_to(message, f"Generated key: {key} for {days} days.")
    except:
        bot.reply_to(message, "Usage: /genk <days>")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    user_id = message.from_user.id

    if is_banned(user_id):
        bot.send_message(user_id, "You are banned from this bot.")
        return

    text = message.text

    if user_id in user_states:
        # Waiting for user to enter redeem details
        if user_states[user_id] == "redeem":
            if not is_user_premium(user_id) and has_used_redeem(user_id):
                bot.send_message(user_id, "Free users can only redeem once. Please buy premium for unlimited access.")
                user_states.pop(user_id)
                return

            # Forward message to admin
            bot.send_message(ADMIN_ID, f"Redeem request from @{message.from_user.username} ({user_id}):\n\n{text}")
            if not is_user_premium(user_id):
                mark_redeem_used(user_id)
            bot.send_message(user_id, "Your redeem request details have been sent to admin.")
            user_states.pop(user_id)
            return

        # Waiting for premium key input to activate
        if user_states[user_id].startswith("buy_"):
            key = text.strip()
            if check_key_valid(key):
                set_user_premium(user_id, key)
                bot.send_message(user_id, f"Premium activated! Your key is valid.")
                bot.send_message(ADMIN_ID, f"User @{message.from_user.username} ({user_id}) activated premium with key: {key}")
            else:
                bot.send_message(user_id, "Invalid or expired key.")
            user_states.pop(user_id)
            return

    if text == "Redeem Request":
        user_states[user_id] = "redeem"
        bot.send_message(user_id, "Enter Details:")

    elif text == "Buy Premium":
        user_states[user_id] = "buy_key"
        bot.send_message(user_id, "Please enter your premium key:")

    elif text == "Service":
        bot.send_message(user_id, "Choose a service:", reply_markup=service_keyboard())

    elif text == "Dev":
        bot.send_message(user_id, "Developer: @YourAizenRender")

    elif text in ["Prime Video", "Spotify", "Crunchyroll", "Turbo VPN", "Hotspot Shield VPN"]:
        # Respond with a fixed message for services
        bot.send_message(user_id, f"Details about {text} service:\n[Provide your service details or links here]")

    elif text == "Back":
        bot.send_message(user_id, "Back to main menu", reply_markup=main_keyboard())

    else:
        bot.send_message(user_id, "Use the buttons below:", reply_markup=main_keyboard())

# Flask for uptime robot
@app.route("/")
def home():
    return "Bot is running."

def run():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    # Run bot polling in separate thread because Flask will block main thread
    threading.Thread(target=run).start()
    app.run(host="0.0.0.0", port=8080)
