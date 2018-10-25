#This is where all the commands relating to the interaction with the User will be

from telegram.ext import Updater, CommandHandler
import json
import keys

def load_user_info():
# Load User Info
    try:
        f = open("user_data.json", "r")
        list_known_ids = json.load(f)
        f.close()
    except:
        list_known_ids = {"":""}

    return list_known_ids

#definition of functions to execute when user enters the right command

def new_user(bot, update):
    list_known_ids = load_user_info()
    #checking if user is registered in the user_data file. If not ask for info
    if str(update.message.chat_id) in list_known_ids.keys():
        update.message.reply_text("I know you")

    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Looks like you're new here! Welcome 😊")

        #add user info to user base
        new_user_info = {"telegram_id":update.message.chat_id,
                         "first_name":update.message.from_user.first_name,
                         "last_name":update.message.from_user.last_name,
                         "wunderlist_id":"",
                         "e-mail":""}

        list_known_ids[update.message.chat_id] = new_user_info

        #save new dict to json-file
        f = open("user_data.json", 'w')
        json.dump(list_known_ids, f)
        f.close()

def show_recipes(bot, update):
    update.message.reply_text(
        'Hello {}, showing you all recipes'.format(update.message.from_user.first_name))

def add_recipe(bot, update):
    update.message.reply_text(
        'Hello {}, add your recipe'.format(update.message.from_user.first_name))

def edit_user_profile(bot, update):
    user_info = load_user_info()
    update.message.reply_text("This is your user info:")
    update.message.reply_text(user_info[str(update.message.chat_id)])

updater = Updater(keys.key_telegram_bot)

#adding commands to commandhandler
#CommandHandler(Command to look for, name of function to execute)
updater.dispatcher.add_handler(CommandHandler('start', new_user))
updater.dispatcher.add_handler(CommandHandler('list_recipes', show_recipes))
updater.dispatcher.add_handler(CommandHandler('add_recipes', add_recipe))
updater.dispatcher.add_handler(CommandHandler('edit_profile', edit_user_profile))

updater.start_polling()
updater.idle()