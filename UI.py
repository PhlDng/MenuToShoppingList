########################### Import of necesssry modules ###########################################
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
list_selected_recipes = {}

global current_ingredient
current_ingredient = ""

########################### Setting up the event logger #############################################
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("Telegram Bot")

############### Helper functions that have nothing to do with the Telegram API ######################
# Load user data json fila and crate python list from it
def load_user_info():
    try:
        f = open("user_data.json", "r")
        list_known_ids = json.load(f)
        f.close()
    except:
        list_known_ids = {"":""}

    return list_known_ids

# Safe new user data in user data json file
def save_user_info(user_info):
    f = open("user_data.json", 'w')
    json.dump(user_info, f)
    f.close()

# Load recipe list json file and create python list from it
def load_recipes():
    try:
        f = open("list_recipes.json", "r")
        list_recipes = json.load(f)
        f.close()
        #Raise error of json file doesn't contain any recipes --> Create standard "Pasta & Pesto"
        if list_recipes == {}:
            raise ValueError("The list is empty")
    except:
        #if json file not found, create basic recipe to be saved to new file
        list_recipes = {"Pasta & Pesto": {
            "Pasta": {
                "Name": "Pasta",
                "Quantity": "500",
                "Unit": "g"}
            ,
            "Pesto": {
                "Name": "Pesto",
                "Quantity": "1",
                "Unit": "Jar"}
        }}
        save_recipes(list_recipes)
    return list_recipes

# Safe new recipe in recipe data json file
def save_recipes(list_recipes):
    f = open("list_recipes.json", 'w')
    json.dump(list_recipes, f)
    f.close()

# buttons for Telegram
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

# "Layout" for final output
def build_list_ingredients(list_selected_recipes):
    data_recipes = load_recipes()
    str_ingredients = ""

    #List of recipes
    str_ingredients = "<b>You selected the following recipes</b>: \n"
    for recipe in list_selected_recipes:
        str_ingredients = str_ingredients + str(recipe) + "\n"

    #List of ingredients
    str_ingredients = str_ingredients + "\n<b>Here are the ingredients you need in order to prepare the recipes</b>: \n"

    for selected_item in list_selected_recipes:
        for ingredient in data_recipes[selected_item]:
            str_ingredients = str_ingredients + \
                              data_recipes[selected_item][ingredient]["Quantity"] + " " + \
                              data_recipes[selected_item][ingredient]["Unit"] + " " + \
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

        logger.info("%s just opened the start page", update.message.from_user.first_name)

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

        #save new user to json file
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
    global list_ingredients
    list_ingredients={}
    update.message.reply_text("What is your recipe called?:")
    return ADD_RECIPE_NAME # go into next state where recipe name is saved

def delete_recipe(bot, update):
    # creating list of available recipes from json to build the button menu
    list_recipes = []
    for recipe in load_recipes():
        list_recipes.append("Delete " + recipe)

    button_list = [InlineKeyboardButton(s, callback_data=str(s)) for s in list_recipes]

    reply_markup = InlineKeyboardMarkup(menu_build_helper(button_list,
                                                          n_cols=2))

    bot.send_message(chat_id=update.message.chat_id,
                     text="What recipe would you like to delete? Keep in mind, this is definitive",
                     reply_markup=reply_markup)

# "Layout" for displaying user info to user
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
# Initiate states
OPTION_EDIT, EDIT_EMAIL = range(2)

# Section to edit user e-mail address
def user_info_inline_call_handler(bot, update):
    if update.callback_query.data == "edit_email":
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
                                text="Editing your e-mail address")
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Alright! Please send me your e-mail address:")
        return EDIT_EMAIL
    else:
        logger.error("Signal sent by InlineKeyboard for Profil Edit not found.")

# Save the entered address
def edit_email(bot, update):
    user_info = load_user_info()
    user_info[str(update.message.chat_id)]["e-mail"] = str(update.message.text)
    save_user_info(user_info)
    update.message.reply_text("Thanks! Your e-mail address has been saved.")
    logger.info("%s changed his/her E-Mail", update.message.from_user.first_name)
    return ConversationHandler.END

def cancel(bot, update):
    user = update.message.from_user
    logger.info("%s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END

################### Functions for ConversationHandler (Add Recipe Info) ###############################
# Initiate states
ADD_RECIPE_NAME, ADD_NAME, ADD_QUANTITY, ADD_UNIT, ADD_MORE = range(5)

# Arrive here from first add recipe question, save recipe name, ask for ingredient name and lead to next state
def add_name_rec(bot, update):
    global current_recipe_name
    current_recipe_name=update.message.text
    update.message.reply_text("Please enter the first ingredient:")
    return ADD_NAME

# Analogous to prev. step
def add_name_ing(bot, update):
    list_ingredients[update.message.text] = {}
    list_ingredients[update.message.text]["Name"] = update.message.text
    global current_ingredient
    current_ingredient=update.message.text
    update.message.reply_text("Please enter the quantity:")
    return ADD_QUANTITY

# Analogous to prev. step
def add_quantitiy_rec(bot, update):
    list_ingredients[current_ingredient]["Quantity"] = update.message.text
    update.message.reply_text("Please enter the unit:")
    return ADD_UNIT

# Analogous to prev. step, then consolidate ingredients information and add to json file
def add_unit_rec(bot, update):
    list_ingredients[current_ingredient]["Unit"] = update.message.text

    temp_list_recipe = load_recipes()
    temp_list_recipe[current_recipe_name]=list_ingredients
    save_recipes(temp_list_recipe)

    update.message.reply_text("Would you like to add another ingredient?")
    update.message.reply_text("Please enter 'yes' or 'no'")
    return ADD_MORE

# Trigger "next round in loop" for next ingredient
def add_more_rec(bot, update):
    if str(update.message.text) == "yes":

        update.message.reply_text("Please send your next ingredient:")
        return ADD_NAME

# If "no" or anything else than "yes" is entered, process is ended
    else:
        logger.info("%s just added a new recipe", update.message.chat.first_name)
        update.message.reply_text("Thank you! The recipe was saved.")

        global list_ingredients
        list_ingredients=[]
        global current_ingredient
        current_ingredient=""
        global current_recipe_name
        current_recipe_name=""
        return ConversationHandler.END

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

    # check if user is already present in the global recipies list
    if str(update.callback_query.message.chat.id) not in str(list_selected_recipes.keys()):
        # create empty list for specified user
        list_selected_recipes[update.callback_query.message.chat.id] = []

    ##### CALLBACK COMMING FROM THE SELECTION MENU #####
    #Callback from the menu for one of the recipes
    if str(update.callback_query.data) in list_possible_callbacks_select :

        #check if recipe already is in the list
        if str(update.callback_query.data.lstrip("selection_")) not in list_selected_recipes[update.callback_query.message.chat.id]:
            list_selected_recipes[update.callback_query.message.chat.id].append(
            str(update.callback_query.data).lstrip("selection_"))

    # Callback for exporting the list of selected recipes
    elif update.callback_query.data == "export_to_telegram":
        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         parse_mode=telegram.ParseMode.HTML,
                         text=build_list_ingredients(list_selected_recipes[update.callback_query.message.chat.id]))

        # delete recipies stored in list after we sent the ingredients
        list_selected_recipes[update.callback_query.message.chat.id] = []

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
        body = build_list_ingredients(list_selected_recipes[update.callback_query.message.chat.id]).replace("\n", "<br>")
        msg.attach(MIMEText(body, 'html'))

        server.sendmail(config.email_user, email_user, msg.as_string())
        server.quit()

        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Alright! We just sent the list to {}".format(email_user))

        #delete recipies stored in list after we sent the ingredients
        list_selected_recipes[update.callback_query.message.chat.id] = []
        logger.info("%s just exported a list of ingredients to his e-mail address",
                    update.callback_query.message.chat.first_name)

    ##### CALLBACK COMING FROM THE DELETE MENU #####
    elif update.callback_query.data in list_possible_callbacks_delete:
        list_recipes = load_recipes()

        #Deleting recipe from list of recipes (JSON file)
        del list_recipes[update.callback_query.data.lstrip("Delete ")]
        save_recipes(list_recipes)

        # To avoid errors, we are also checking if a user currently has this recipe in his list
        # of selected recipes
        if update.callback_query.data.lstrip("Delete ") in list_selected_recipes[update.callback_query.message.chat.id]:
            del list_selected_recipes[update.callback_query.message.chat.id]

        bot.send_message(chat_id=update.callback_query.message.chat.id,
                         text="Alright! The recipe '{}' has just been deleted."
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

        states={ #Waiting for? State is defined at the end of prev. function
            OPTION_EDIT: [CallbackQueryHandler(user_info_inline_call_handler)],
            EDIT_EMAIL: [MessageHandler(Filters.text, edit_email)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

add_recipe_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_recipes', add_recipe)],

        states={ #Waiting for? State is defined at the end of prev. function
            ADD_RECIPE_NAME: [MessageHandler(Filters.text, add_name_rec)],
            ADD_NAME: [MessageHandler(Filters.text, add_name_ing)],
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
