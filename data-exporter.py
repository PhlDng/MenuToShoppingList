#This is where all the functions related to sending out the data willl be stored

#import packages
import telegram
from telegram.ext import Updater, CommandHandler

#import keys
import keys



def send_to_telegram(list_to_send = ["Eggs", "Milk"]):

    # creating a bot that will send messages
    TelegramBot = telegram.Bot(keys.key_telegram_bot)

    for element in list_to_send:
    # sending a message for every element in the list
        TelegramBot.send_message(chat_id=keys.telegram_chat_ids[0], #currently only send messages to me
                                 text=element,
                                 parse_mode="Markdown")

def send_to_wunderlist(list_to_send=["Eggs", "Milk"]):
    print ("ToDo: Wunderlist")

def send_to_email(list_to_send=["Eggs", "Milk"])
    print ("ToDo: E-Mail")

