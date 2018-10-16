#This is where all the functions related to sending out the data willl be stored

#import packages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import telegram
from telegram.ext import Updater, CommandHandler

import wunderpy2

#import keys for apps
import keys


def send_to_telegram(list_to_send = ["Eggs", "Milk"]):

    # creating a bot that will send messages
    TelegramBot = telegram.Bot(keys.key_telegram_bot)

    for element in list_to_send:
    # sending a message for every element in the list
        TelegramBot.send_message(chat_id=keys.telegram_chat_ids[0], #currently only send messages to me
                                 text=element,
                                 parse_mode="Markdown")

def send_to_wunderlist(list_to_send=["Eggs", "Milk"],):
    api = wunderpy2.WunderApi()
    client = api.get_client(keys.wunderlist_access_token, keys.wunderlist_client_id)
    lists = client.get_lists()

    #creating a dict with all the List names and corresponding id
    dict_lists = {}
    for i in range(len(lists)):
        dict_lists[lists[i]["title"]] = lists[i]["id"]

    # check if there is a list called "Grocery List
    list_name_grocery = "List of groceries"
    if str(list_name_grocery) in dict_lists.keys():
        print("List already exists")
    else:
        client.create_list(list_name_grocery)
        #update dict of list to get id of new list
        lists = client.get_lists()
        for i in range(len(lists)):
            dict_lists[lists[i]["title"]] = lists[i]["id"]
        print("New list created")

    #add groceries to list
    for items in list_to_send:
        client.create_task(dict_lists[list_name_grocery], items)




def send_to_email(list_to_send=["Eggs", "Milk"], email_to_send_to="philipp.ding@gmail.com"):
    server = smtplib.SMTP('smtp.mail.ch', 587)
    server.starttls()
    server.login(keys.email_user, keys.email_password)

    msg = MIMEMultipart()
    msg['From'] = keys.email_user
    msg['To'] = email_to_send_to
    msg['Subject'] = "SUBJECT OF THE MAIL"

    body = str(list_to_send)
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(keys.email_user, email_to_send_to , msg.as_string())
    server.quit()


send_to_wunderlist()