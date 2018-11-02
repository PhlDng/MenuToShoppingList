#This is where all the functions related to sending out the data will be stored
# Options so far: E-Mail, Telegram, Wunderlist

#import packages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import telegram
from telegram.ext import Updater, CommandHandler

import wunderpy2

#import keys for apps
import config

list_groceries = ["Milk", "Eggs", "Bread", "Meat", "Lemons", "Flour"]

def send_to_telegram(list_to_send = ["Eggs", "Milk"]):

    # creating a bot that will send messages
    TelegramBot = telegram.Bot(config.key_telegram_bot)

    for element in list_to_send:
    # sending a message for every element in the list
        TelegramBot.send_message(chat_id=config.telegram_chat_ids[0],  #currently only send messages to me
                                 text=element,
                                 parse_mode="Markdown")

def send_to_email(list_to_send=["Eggs", "Milk"], email_to_send_to="philipp.ding@gmail.com"):
    server = smtplib.SMTP(str(config.email_smtp_adr), int(config.email_smtp_port))
    server.starttls()
    server.login(config.email_user, config.email_password)

    msg = MIMEMultipart()
    msg['From'] = config.email_user
    msg['To'] = email_to_send_to
    msg['Subject'] = "SUBJECT OF THE MAIL"

    body = str(list_to_send)
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(config.email_user, email_to_send_to, msg.as_string())
    server.quit()

send_to_wunderlist(list_groceries)
send_to_telegram(list_groceries)