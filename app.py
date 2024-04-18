# import everything
from flask import Flask, request
import telegram
from credentials import bot_token, bot_user_name, URL, open_ai_token

global bot
global TOKEN
TOKEN = bot_token

import re
#bot = telegram.Bot(token=TOKEN)

from openai import OpenAI
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from gradio_client import Client
from uuid import uuid4

PROMPT, RESPONSE, RESPONSE2, LOCATION, BIO = range(5)


# RESPOND = ''
save1,save2,save3,save4 = '','','',''
client = OpenAI(api_key=open_ai_token)

# Define your handler function
async def prompt(update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    #chat_id = update.message.chat.id
    #print(f'User ({update.message.chat.id})in: "{text}"')
    context.chat_data[0] = text
    # Send the user's message to the OpenAI API
    response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal:csa:96wYKadU", messages=[{"role": "user", "content": text}])
    # Get the response from the API
    ai_text = response.choices[0].message.content
    # Send the AI's response back to the user
    await update.message.reply_text(ai_text)
    return RESPONSE
    
async def respond(update, context: ContextTypes.DEFAULT_TYPE):
    text2 = update.message.text
    #chat_id = update.message.chat.id
    #print(f'User ({update.message.chat.id})in: "{text}"')
    # Send the user's message to the OpenAI API
    print(context.chat_data[0],'\n',text2)
    #response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": context.chat_data[0]+ text2}],max_tokens=4096,temperature=0.5)
    response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal:csa:96wYKadU", messages=[{"role": "system", "content":context.chat_data[0]},{"role": "user", "content": text2}],max_tokens=4096,temperature=0.5)

    # Get the response from the API
    ai_text = response.choices[0].message.content
    context.bot_data[0] = ai_text
    # Send the AI's response back to the user
    await update.message.reply_text(ai_text)
    
    return RESPONSE2

async def respond2(update, context: ContextTypes.DEFAULT_TYPE):
    text3 = update.message.text
    #chat_id = update.message.chat.id
    #print(f'User ({update.message.chat.id})in: "{text}"')
    # Send the user's message to the OpenAI API
    print(context.bot_data[0],'\n',text3)
    #response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": context.bot_data[0]+ text3}],max_tokens=4096,temperature=0)
    response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal:csa:96wYKadU", messages=[{"role": "system", "content":context.bot_data[0] + ",i wan this to strictly be in JSON format of question and answer format"},{"role": "user", "content": text3}],max_tokens=4096,temperature=0.5)

    # Get the response from the API
    ai_text = response.choices[0].message.content
    # Send the AI's response back to the user
    await update.message.reply_text(ai_text)
    return ConversationHandler.END
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and asks the user about their gender."""
    await update.message.reply_text(
       "Hi i am your study assistant, I can help you with your notes and flashcard making. What do you need help with?"
    )
    return PROMPT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    #logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    context.bot_data.clear()
    context.chat_data.clear()
    context.user_data.clear()
    return ConversationHandler.END

async def freeresponse(update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat.id
    print(f'User ({update.message.chat.id})in: "{text}"')
    # Send the user's message to the OpenAI API
    response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal:sarcasm:96r6nSsr", messages=[{"role":"system","content":"Marv is a factual chatbot that is also sarcastic"},{"role": "user", "content": text}])
    # Get the response from the API
    ai_text = response.choices[0].message.content
    # Send the AI's response back to the user
    await update.message.reply_text(ai_text)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    print("Starting bot")
    application = Application.builder().token(TOKEN).build()
    #application.add_handler(CommandHandler("start", start))
    #application.add_handler(CommandHandler("help", help_command))
    #application.add_handler(CommandHandler("custom", custom_command))
    #application.add_handler((CommandHandler("prompter", respondwithprompt)))
    # Message handler for all text messages
    
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PROMPT: [MessageHandler(filters.TEXT, prompt)],
            RESPONSE: [MessageHandler(filters.TEXT,respond)],
            RESPONSE2: [MessageHandler(filters.TEXT,respond2)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & filters.Mention("Simplifymebot"), freeresponse))
    #application.add_handler(MessageHandler(filters.TEXT, freeresponse))

    # application.add_handler(ConversationHandler())
    # Errors
    #app.add_error_handler(error)
    # Polls 
    # print('Polling...')
    application.run_polling(poll_interval=5)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()