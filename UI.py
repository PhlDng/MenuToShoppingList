import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import json
import keys

########################### Setting up the event logger #############################################
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("Telegram Bot")

############### Helper functions that have nothing to do with the Telegram API ######################
def load_user_info():
# Load User Info
    try:
        f = open("user_data.json", "r")
        list_known_ids = json.load(f)
        f.close()
    except:
        list_known_ids = {"":""}

    return list_known_ids

def save_user_info(user_info):
    f = open("user_data.json", 'w')
    json.dump(user_info, f)
    f.close()

################################## Main Commandhandler Function #####################################
def new_user(bot, update):
    list_known_ids = load_user_info()
    #checking if user is registered in the user_data file. If not ask for info
    if str(update.message.chat_id) in list_known_ids.keys():
        bot.send_message(chat_id=update.message.chat_id,
                         text="Welcome back {}!".format(update.message.from_user.first_name))
        logger.info("Returning user %s connected", update.message.from_user.first_name)

    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Looks like you're new here! Welcome 😊")

        logger.info("New user %s connected", update.message.from_user.first_name)

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
        logger.info ("Info for new user %s added to the JSON file", update.message.from_user.first_name)

def show_recipes(bot, update):
    update.message.reply_text(
        'Hello {}, showing you all recipes'.format(update.message.from_user.first_name))

def add_recipe(bot, update):
    update.message.reply_text(
        'Hello {}, add your recipe'.format(update.message.from_user.first_name))

def edit_user_profile(bot, update):
    user_info = load_user_info()

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text="*This is what we have about you:* \n\n" +
                          "*Telegram ID*: {}".format(user_info[str(update.message.chat_id)]["telegram_id"]) +
                          "\n*First Name*: {}".format(user_info[str(update.message.chat_id)]["first_name"]) +
                          "\n*Last Name*: {}".format(user_info[str(update.message.chat_id)]["last_name"]) +
                          "\n*E-Mail*: {}".format(user_info[str(update.message.chat_id)]["e-mail"]) +
                          "\n*Wunderlist ID*: {}".format(user_info[str(update.message.chat_id)]["wunderlist_id"])
                     )

    #Asking user what to do next? Init of bot waiting for signal from menu, will be funneled through callback handler
    button_list = [[InlineKeyboardButton("Edit e-mail", callback_data="edit_email"),
                    InlineKeyboardButton("Edit wunderlist ID", callback_data="edit_wunderlist")]]

    reply_markup = InlineKeyboardMarkup(button_list)

    bot.send_message(chat_id=update.message.chat_id,
                     text="What would you like to edit?",
                     reply_markup=reply_markup)

    return OPTION_EDIT

def admin_info(bot, update):
    if update.message.chat_id in keys.telegram_admin_ids:
        user_info = load_user_info()
        update.message.reply_text(user_info)

################### Functions for ConversationHandler (Edit User Info) ###############################

#Not sure why this has to be done. Creates states for Cenversation Handler?
OPTION_EDIT, EDIT_EMAIL, EDIT_WUNDERLIST = range(3)

def user_info_inline_call_handler(bot, update):
    if update.callback_query.data == "edit_email":
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
                                text="Editing your e-mail address")
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Alright! Please send me your e-mail address:")

        return EDIT_EMAIL

    elif update.callback_query.data == "edit_wunderlist":
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
                                text="Editing your Wunderlist ID")
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Alright! Please send me your Wunderlist ID:")

        return EDIT_WUNDERLIST

    else:
        logger.error("Signal sent by InlineKeyboard not found.")

def edit_email(bot, update):
    user_info = load_user_info()
    user_info[str(update.message.chat_id)]["e-mail"] = str(update.message.text)
    save_user_info(user_info)

    update.message.reply_text("Thanks! Your e-mail address has been saved.")
    logger.info("%s changed his E-Mail", update.message.from_user.first_name)
    return ConversationHandler.END # temp. Should go back to asking if change anythin else

def edit_wunderlist(bot, update):
    user_info = load_user_info()
    user_info[str(update.message.chat_id)]["wunderlist_id"] = update.message.text
    save_user_info(user_info)

    update.message.reply_text("Thanks! Your Wunderlist ID has been saved.")
    logger.info("%s changed his Wunderlist ID", update.message.from_user.first_name)
    return ConversationHandler.END  # temp. Should go back to asking if change anythin else

def cancel(bot, update):
    user = update.message.from_user
    logger.info("%s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END

######################### General Error Handling Function ############################################
def error_callback(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


####################################################################################################
############################### BOT ASSEMBLY AND EXECUTION #########################################
####################################################################################################

# Create the Updater which will connect to the Telegram API and send/recieve updates
updater = Updater(keys.key_telegram_bot) #creates bot
dispatcher = updater.dispatcher #shortcut to add Handlers to the dispatcher

#################### DIFFERENT TYPES OF EVENT HANDLERS USED BY THE BOT #############################
#################### Types of Handlers used:
                   #  - CommandHandler        --> To handle commands (/...) comming from the user
                   #  - ConverstionHandler    --> To create more complexe structures. Uses MessageHandler + CallbackQueryHandler
                   #  - MessageHandler        --> To handle written text from the user in the chat
                   #  - CallbackQueryHandler  --> To handle signals from InlineKeyboards (Menus)
                   #  - ErrorHandler

##################################### ConversationHandlers ###########################################
#ConversationHandler for "User Info Function"
user_info_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('edit_profile', edit_user_profile)],

        states={ #Worauf warten wir? State wird am ende der vorherigen Funtkion gesetzt
            OPTION_EDIT: [CallbackQueryHandler(user_info_inline_call_handler)],
            EDIT_EMAIL: [MessageHandler(Filters.text, edit_email)],

            EDIT_WUNDERLIST : [MessageHandler(Filters.text, edit_wunderlist)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

dispatcher.add_handler(user_info_conv_handler)

##################################### CommandHandlers #################################################
dispatcher.add_handler(CommandHandler('start', new_user))
dispatcher.add_handler(CommandHandler('list_recipes', show_recipes))
dispatcher.add_handler(CommandHandler('add_recipes', add_recipe))
dispatcher.add_handler(CommandHandler('admin', admin_info))


##################################### ErrorHandlers ###################################################
dispatcher.add_error_handler(error_callback) #Any errors will be added to the log


#Starting the bot
updater.start_polling()
updater.idle()