# Telegram Bot to Shopping List

This bot was written as a group project for the HSG Lecture "*Advanced programming languages*"

It was written in a Python 3.6 environment with the following additional packages

Required packages to run this script. They should all be available with pip.
 - **python-telegram-bot**: https://github.com/python-telegram-bot/python-telegram-bot
 - **json**: should be included by default with Python 3.6
 - **smtplib**: should be included by default with Python 3.6
 - **email**: should be included by default with Python 3.6
 
 
 ## Instructions:
 
 ###### Configuration of bot:
 The config.py file contains the required keys and passwords to run the bot.
 It should contain a Bot-Token for the Telegram-Bot, which can be created with the Bot-Father. For more information follow [this link](https://core.telegram.org/bots). 
 
In addition, the bot needs credentials of an SMTP-server to be able to send e-mails. The following should be added to the config.py file:
  - Username
  - Password
  - SMTP server address
  - SMTP server port
 
 ###### Starting bot:
 1. Make sure you have properly configured your bot in config.py
 2. Run UI.py
 3. Talk to your bot on telegram
 
 ###### Interaction with user:
 The user interacts with the bot through a set of determined commands:
  - **/start**: This command is used to start the interaction with the bot. It shows you the list of available commands and creates your account if it's your first time talking to the bot.
  - **/show_recipes**: Shows the stored recipes. You can select as many as you want and and choose how you would like to receive the corresponding list of ingredients. You have the choice between receiving a telegram message or an e-mail.
  - **/add_recipes**: With this command you can add a recipe to the list of stored recipes.
  - **/delete_recipe**: Delete a recipe from the catalogue.
  - **/edit_profile**: This will show what information the bot has stored about you. If you want to be able to send the list of ingredients to you e-mail address, this is the place where you add it.
