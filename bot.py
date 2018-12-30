#!/usr/bin/env python
import telebot
import sys, random, shelve
from telebot.types import Message, ForceReply
TOKEN = '747166697:AAEHDFftR28rZuxYRH6CRLD4UDm8N9QARVw'

bot = telebot.TeleBot(TOKEN)

users_dict = shelve.open('users',writeback=True)
 

# User Auth 
class User:    
    def __init__(self, name):
        self.name = name
        self.words = {}
        self.pair=[]
        self.index = 0  #index of question for navigate through words
        self.score = 0
        self.goal = 0
    
    def remember(self):
      self.words[self.pair[0]] = self.pair[1]
      self.words[self.pair[1]] = self.pair[0]
      self.pair = []
      


@bot.message_handler(commands=['start','help'])    
def send_welcome(message):
    msg = bot.reply_to(message, '''\
    Hi, I am words learning bot.\
    You can just write  /new, so i will learn new words pair,\
    and then help you to learn them...\
    But fist, tell me what is your name? 
    ''')
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        users_dict[str(chat_id)] = user
        msg = bot.send_message(chat_id,f'''Nice to meet you ,{user.name},\
        now tell me \n how many words do you want to repeat at one training?
        ''')
        bot.register_next_step_handler(msg, process_goal)

    except Exception as _:
        error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
        bot.reply_to(message, error)
users_dict.close()

def process_goal(message):
  try:
    chat_id = message.chat.id
    user = users_dict[str(chat_id)]
    user.goal =  int(message.text)
    bot.send_message(chat_id, f'''Ok,you set your goal as {user.goal} \
    now teach me some new words by command /new''')
    users_dict.sync()
  except Exception as _:
    error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
    bot.reply_to(message, error)


@bot.message_handler(commands=['new'])
def learn_new(message):
  try :
    msg = bot.reply_to(message,'Tell me a new word')
    bot.register_next_step_handler(msg,process_new_word)
  except Exception as _:
    error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
    bot.reply_to(message, error)

def  process_new_word(message):
  try :
    chat_id = message.chat.id
    word = message.text
    user = users_dict[str(chat_id)]
    user.pair.append(word) 
    msg = bot.reply_to(message, 'What is the translation?')

    bot.register_next_step_handler(msg, process_translation)
  except Exception as _:
      error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
      bot.reply_to(message, error)
    
def process_translation(message):
    try :
      chat_id = message.chat.id
      translation  = message.text
      user = users_dict[str(chat_id)]
      user.pair.append(translation)
      user.remember()
      bot.reply_to(message, 'Ok, i will remember. \n for practice type /gym   \n  or /new to add another')
      users_dict.sync()    
    except Exception as _:
      error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
      bot.reply_to(message, error)


# Training method
@bot.message_handler(commands=['gym'])    
def gym(message):
  try :
    chat_id = message.chat.id
    ask(str(chat_id))
  except Exception as _:
    error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
    bot.reply_to(message, error)

def ask(chat,i=0): 
  user = users_dict[chat]
  words = list(user.words.keys())
  word = words[user.index]
  msg = bot.send_message(chat,f'What is {word}?')
  bot.register_next_step_handler(msg, check_answer)


def check_answer(message):
  chat = str(message.chat.id)
  user = users_dict[chat]
  words = list(user.words.keys())
  if user.score < user.goal:
    if message.text == user.words[words[user.index]]:
      bot.send_message(chat,'You are correct!')
      user.score  += 1
      user.index = random.randrange(len(words))
      if user.score == user.goal :
        user.index = 0
        user.score = 0
        bot.send_message(chat,'Good for you!\n You achived your goal!')
        users_dict.sync()
      else:
        ask(chat)
    else:
      bot.send_message(chat,'ooops!')
      user.score -= 1
      user.index -= 1
      ask(chat)
  else :
    bot.send_message(chat,'ooops!')


bot.polling()
users_dict.close()
