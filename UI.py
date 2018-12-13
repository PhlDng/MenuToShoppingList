import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import json
import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

########################### Definition of global variables###########################################
global list_selected_recipes
list_selected_recipes = []

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

def load_recipes():
# Load User Info
    try:
        f = open("list_recipes.json", "r")
        list_recipes = json.load(f)
        f.close()
        #Raise error of json file doesn't contain any recipes --> Create Pesto Nudeln
        if list_recipes == {}:
            raise ValueError("The list is empty")
    except:
        #if json file not found, create basic recipe to be saved to new file
        list_recipes = {"Pesto Nudeln": {
            "Nudeln": {
                "Name": "Nudeln",
                "Menge": "800",
                "Einheiten": "g"}
            ,
            "Pesto": {
                "Name": "Pesto",
                "Menge": "1",
                "Einheiten": "Glas"}
        }}
        save_recipes(list_recipes)
    return list_recipes

def save_recipes(list_recipes):
    f = open("list_recipes.json", 'w')
    json.dump(list_recipes, f)
    f.close()

def menu_build_helper(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):

    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def build_list_ingredients(list_selected_recipes):
    data_recipes = load_recipes()
    str_ingredients = ""

    #List of recipes
    str_ingredients = "<b>You selected the following recipes</b>: \n"
    for recipe in list_selected_recipes:
        str_ingredients = str_ingredients + str(recipe) + "\n"

    #List of ingredients
    str_ingredients = str_ingredients + "\n<b>Here are the ingredients you need to prepare these recipes</b>: \n"

    for selected_item in list_selected_recipes:
        for ingredient in data_recipes[selected_item]:
            str_ingredients = str_ingredients + \
                              data_recipes[selected_item][ingredient]["Menge"] + " " + \
                              data_recipes[selected_item][ingredient]["Einheiten"] + " " + \
                              data_recipes[selected_item][ingredient]["Name"] + "\n"

    return str_ingredients
################################## Main Commandhandler Functions #####################################

def new_user(bot, update):
    list_known_ids = load_user_info()
    #checking if user is registered in the user_data file. If not ask for info
    if str(update.message.chat_id) in list_known_ids.keys():
        bot.send_message(chat_id=update.message.chat_id,
                         text="Welcome back {}!\n\n".format(update.message.from_user.first_name)
                         + "What would you like to do? You have the choice between the following options:\n\n"
                         + "Select one or more recipes by typing: /show_recipes\n"
                         + "Add a recipe to the list by typing: /add_recipes\n"
                         + "Delete a recipe from the list by typing: /delete_recipe\n"
                         + "Change your user information by typing: /edit_profile")

        logger.info("Returning user %s connected", update.message.from_user.first_name)

    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Welcome {}! Looks like you're new here!\n\n".format(update.message.from_user.first_name)
                         + "We don't know your e-mail adress yet. If you want to be able to send the list of ingredients"
                         + "to your e-mail, make sure to add it in the profile section: /edit_profile\n\n"
                         + "What would you like to do? You have the choice between the following options:\n\n"
                         + "Select one or more recipes by typing: /show_recipes\n"
                         + "Add a recipe to the list by typing: /add_recipes\n"
                         + "Delete a recipe from the list by typing: /delete_recipe\n"
                         + "Change your user information by typing: /edit_profile")

        logger.info("New user %s connected", update.message.from_user.first_name)

        #add user info to user base
        new_user_info = {"telegram_id":update.message.chat_id,
                         "first_name":update.message.from_user.first_name,
                         "last_name":update.message.from_user.last_name,
                         "e-mail":"No e-mail"}
        list_known_ids[update.message.chat_id] = new_user_info

        #save new dict to json-file
        save_user_info(list_known_ids)
        logger.info ("Info for new user %s added to the JSON file", update.message.from_user.first_name)

def show_recipes(bot, update):

    #creating list of available recipes from JSON to build the button menu
    list_recipes = []
    for recipe in load_recipes():
        list_recipes.append(recipe)

    button_list = [InlineKeyboardButton(s, callback_data="selection_" + str(s)) for s in list_recipes]
    footer_button = [InlineKeyboardButton("Send ingredients to telegram",
                                          callback_data="export_to_telegram"),
                     InlineKeyboardButton("Send an email with ingredients",
                                          callback_data="export_to_email")]

    reply_markup = InlineKeyboardMarkup(menu_build_helper(button_list,
                                                          n_cols=3,
                                                          footer_buttons=footer_button))
    bot.send_message(chat_id=update.message.chat_id,
                     text="This is what we have in store. "
                          "Please select what you would like to add to your list",
                     reply_markup=reply_markup)

def add_recipe(bot, update):
    update.message.reply_text(
        'Hello {}, add your recipe'.format(update.message.from_user.first_name))

    update.message.reply_text("Please send your first ingredient:")
    return ADD_NAME

def delete_recipe(bot, update):
    # creating list of available recipes from JSON to build the button menu
    list_recipes = []
    for recipe in load_recipes():
        list_recipes.append("Delete " + recipe)

    button_list = [InlineKeyboardButton(s, callback_data=str(s)) for s in list_recipes]

    reply_markup = InlineKeyboardMarkup(menu_build_helper(button_list,
                                                          n_cols=2))

    bot.send_message(chat_id=update.message.chat_id,
                     text="What recipe would you like to delete? Keep in mind, this is definitive",
                     reply_markup=reply_markup)

def edit_user_profile(bot, update):
    user_info = load_user_info()
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text="*This is what we have about you:* \n\n" +
                          "*Telegram ID*: {}".format(user_info[str(update.message.chat_id)]["telegram_id"]) +
                          "\n*First Name*: {}".format(user_info[str(update.message.chat_id)]["first_name"]) +
                          "\n*Last Name*: {}".format(user_info[str(update.message.chat_id)]["last_name"]) +
                          "\n*E-Mail*: {}".format(user_info[str(update.message.chat_id)]["e-mail"])
                     )

    #Asking user what to do next? Init of bot waiting for signal from menu, will be funneled through callback handler
    button_list = [[InlineKeyboardButton("Edit e-mail", callback_data="edit_email")]]

    reply_markup = InlineKeyboardMarkup(button_list)

    bot.send_message(chat_id=update.message.chat_id,
                     text="What would you like to edit?",
                     reply_markup=reply_markup)

    return OPTION_EDIT

def admin_info(bot, update):
    if update.message.chat_id in config.telegram_admin_ids:
        user_info = load_user_info()
        update.message.reply_text(user_info)

################### Functions for ConversationHandler (Edit User Info) ###############################
#Not sure why this has to be done. Creates states for Cenversation Handler?
OPTION_EDIT, EDIT_EMAIL = range(2)

def user_info_inline_call_handler(bot, update):
    if update.callback_query.data == "edit_email":
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
                                text="Editing your e-mail address")
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Alright! Please send me your e-mail address:")

        return EDIT_EMAIL
    else:
        logger.error("Signal sent by InlineKeyboard fro Profil Edit not found.")

def edit_email(bot, update):
    user_info = load_user_info()
    user_info[str(update.message.chat_id)]["e-mail"] = str(update.message.text)
    save_user_info(user_info)

    update.message.reply_text("Thanks! Your e-mail address has been saved.")
    logger.info("%s changed his/her E-Mail", update.message.from_user.first_name)
    return ConversationHandler.END # temp. Should go back to asking if change anythin else

def cancel(bot, update):
    user = update.message.from_user
    logger.info("%s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END

################### Functions for ConversationHandler (Add Recipe Info) ###############################
ADD_NAME, ADD_QUANTITY, ADD_UNIT, ADD_MORE = range(4)
def add_name_rec(bot, update):
    print(update.message.text)

    update.message.reply_text("Please enter the quantity:")
    return ADD_QUANTITY

def add_quantitiy_rec(bot, update):
    print(update.message.text)

    update.message.reply_text("Please enter the unit:")
    return ADD_UNIT

def add_unit_rec(bot, update):
    print (update.message.text)


    update.message.reply_text("Would you like to add another ingredient?")
    update.message.reply_text("Please enter 'yes' or 'no'")
    return ADD_MORE

def add_more_rec(bot, update):
    print ("more")
    if str(update.message.text) == "yes":

        update.message.reply_text("Please send your next ingredient:")
        return ADD_NAME

    else:
        update.message.reply_text("Thanks bro! Nice one")
        return ConversationHandler.END
# hier zwischenspeicher in JSON reinladen
def cancel(bot, update):
    user = update.message.from_user
    logger.info("%s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END

######################### General Error Handling Function ############################################
def error_callback(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

######################### CallbackQuerryHandler for selecting recipes#################################
def InlineKeyboardCallbackHandler(bot, update):
    #creating list of possible callbacks based on recipes stored in json file
    # callback can either come from Delete --> "Delete " or Select --> "selection_"
    list_possible_callbacks_select = []
    list_possible_callbacks_delete = []

    for recipe in load_recipes():
        list_possible_callbacks_select.append("selection_" + recipe)

    for recipe in load_recipes():
        list_possible_callbacks_delete.append("Delete " + recipe)

    ##### CALLBACK COMMING FROM THE SELECTION MENU #####
    #Callback from the menu for one of the recipes
    if str(update.callback_query.data) in list_possible_callbacks_select :
        list_selected_recipes.append(str(update.callback_query.data).lstrip("selection_"))

    # Callback for exporting the list of selected recipes
    elif update.callback_query.data == "export_to_telegram":
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         parse_mode=telegram.ParseMode.HTML,
                         text=build_list_ingredients(list_selected_recipes))
        logger.info("%s just exported a list of ingredients to telegram",
                    update.callback_query.message.chat.first_name)


    elif update.callback_query.data == "export_to_email":
        user_data = load_user_info()
        email_user = user_data[str(update.callback_query.message.chat.id)]["e-mail"]
        name_user = user_data[str(update.callback_query.message.chat.id)]["first_name"]

        server = smtplib.SMTP(str(config.email_smtp_adr), int(config.email_smtp_port))
        server.starttls()
        server.login(config.email_user, config.email_password)

        msg = MIMEMultipart()
        msg['From'] = config.email_user
        msg['To'] = email_user
        msg['Subject'] = "List of groceries for {}".format(name_user)
        #"replace" function to convert string from Makdown to html
        body = build_list_ingredients(list_selected_recipes).replace("\n", "<br>")
        msg.attach(MIMEText(body, 'html'))

        server.sendmail(config.email_user, email_user, msg.as_string())
        server.quit()

        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Allright! We just sent the list to {}".format(email_user))

        logger.info("%s just exported a list of ingredients to his e-mail address",
                    update.callback_query.message.chat.first_name)

    ##### CALLBACK COMMING FROM THE DELETE MENU #####
    elif update.callback_query.data in list_possible_callbacks_delete:
        list_recipes = load_recipes()
        del list_recipes[update.callback_query.data.lstrip("Delete ")]
        save_recipes(list_recipes)

        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Allright! The recipe '{}' has just been deleted."
                         .format(update.callback_query.data.lstrip("Delete ")))

        logger.info("%s just deleted the following recipe: %s",
                    update.callback_query.message.chat.first_name,
                    update.callback_query.data.lstrip("Delete "))

####################################################################################################
############################### BOT ASSEMBLY AND EXECUTION #########################################
####################################################################################################

# Create the Updater which will connect to the Telegram API and send/recieve updates
updater = Updater(config.key_telegram_bot) #creates bot
dispatcher = updater.dispatcher #shortcut to add Handlers to the dispatcher

#################### DIFFERENT TYPES OF EVENT HANDLERS USED BY THE BOT #############################
#################### Types of Handlers used:
                   #  - CommandHandler        --> To handle commands (/...) comming from the user
                   #  - ConversationHandler   --> To create more complexe structures. Uses MessageHandler + CallbackQueryHandler
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
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

add_recipe_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_recipes', add_recipe)],

        states={ #Worauf warten wir? State wird am ende der vorherigen Funtkion gesetzt
            ADD_NAME: [MessageHandler(Filters.text, add_name_rec)],
            ADD_QUANTITY: [MessageHandler(Filters.text, add_quantitiy_rec)],
            ADD_UNIT: [MessageHandler(Filters.text, add_unit_rec)],
            ADD_MORE: [MessageHandler(Filters.text, add_more_rec)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

dispatcher.add_handler(user_info_conv_handler)
dispatcher.add_handler(add_recipe_conv_handler)

##################################### CommandHandlers #################################################
dispatcher.add_handler(CommandHandler('start', new_user))
dispatcher.add_handler(CommandHandler('show_recipes', show_recipes))
dispatcher.add_handler(CommandHandler('delete_recipe', delete_recipe))
dispatcher.add_handler(CommandHandler('admin', admin_info))

##################################### CallbackQueryHandlers ############################################
dispatcher.add_handler(CallbackQueryHandler(InlineKeyboardCallbackHandler))


##################################### ErrorHandlers ####################################################
dispatcher.add_error_handler(error_callback) #Any errors will be added to the log


#Starting the bot
updater.start_polling()
updater.idle()
