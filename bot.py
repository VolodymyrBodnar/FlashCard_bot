#!/usr/bin/env python
import telebot
import sys, random, sqlite3
from telebot.types import Message

TOKEN = 'TOKEN'

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('users.db',check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE users
             (name text, goal integer, id integer
        )''')

conn.commit()

users_dict = {}
players_dict = {}


class User:    
    def __init__(self, name, _id):
        self.name = name
        self._id = str(_id)
        self.pair=[]

    def remember(self):
      streight = (self.pair[0],self.pair[1])
      revers = (self.pair[1],self.pair[0])
      with sqlite3.connect("users.db") as con:
          cur = con.cursor()
          cur.execute(f"INSERT INTO words{str(self._id)} VALUES (?, ?)",streight)
          cur.execute(f"INSERT INTO words{str(self._id)} VALUES (?, ?)",revers)
          con.commit()

class Player:
  def __init__(self,_id,i):
    self._id = _id
    self.i = i
    self.score = 0
    self.words = {}
  
  def ask(self):
    question = tuple(self.words.keys())[self.i]
    msg = bot.send_message(self._id,f'what is translation for {question}?')
    bot.register_next_step_handler(msg, check)

## User authenthification
@bot.message_handler(commands=['start'])    
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
        user = User(name,chat_id)
        users_dict[chat_id] = user
        msg = bot.send_message(chat_id,f'''Nice to meet you ,{user.name},\
        now tell me how many words do you want to repeat at one training?
        ''')
        bot.register_next_step_handler(msg, process_goal)

    except Exception as _:
        error = f'Error {sys.exc_info()[0]} at line: {sys.exc_info()[2].tb_lineno}'
        bot.reply_to(message, error)

def process_goal(message):
  try:
    chat_id = message.chat.id
    user = users_dict[chat_id]
    user.goal =  int(message.text)
    data = (user.name,user.goal,chat_id)
    c.execute("INSERT INTO users VALUES (?, ?, ?)", data)
    c.execute(f'''CREATE TABLE words{str(chat_id)}
             (word text, translation text
        )''')
    conn.commit()
    bot.send_message(chat_id, f'''Ok,you set your goal as {user.goal} \
    now teach me some new words by command /new''')
  except Exception as _:
    error = f'Error {sys.exc_info()[0]}, {sys.exc_info()[1]} \n at line: {sys.exc_info()[2].tb_lineno}'
    bot.reply_to(message, error)


## Learn new words
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
    user = User('user',chat_id)
    users_dict[chat_id] = user 
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
      user = users_dict[chat_id]
      user.pair.append(translation)
      user.remember()
      bot.reply_to(message, 'Ok, i will remember... for practice type /gym, or /new to add another')
    except Exception as _:
      error = f'Error {sys.exc_info()[0]},{sys.exc_info()[1]} at line: {sys.exc_info()[2].tb_lineno}'
      bot.reply_to(message, error)


# Training method
@bot.message_handler(commands=['gym'])    
def training(message):
  try :
    chat_id = message.chat.id
    player = Player(chat_id,0)
    players_dict[chat_id] = player
    words_db = c.execute(f'SELECT * FROM words{str(chat_id)}')
    player.words = {word:translation for word, translation in words_db}
    goal = c.execute(f'SELECT goal FROM users WHERE id={chat_id}').fetchone()[0]
    player.goal = goal
    player.score = 0
    player.ask()
  except Exception as _:
    error = f'Error {sys.exc_info()[0]},{sys.exc_info()[1]} at line: {sys.exc_info()[2].tb_lineno}'
    bot.reply_to(message, error)

def check(message):
  
  chat_id = message.chat.id
  player = players_dict[chat_id]
  i = player.i
  goal = player.goal
  words = player.words
  keys = tuple(words.keys())
  if player.score < goal:
    if message.text == words[keys[i]]:
      bot.send_message(chat_id,' You are correct')
      player.score += 1
      player.i = random.randrange(len(keys))
      if player.score == goal:
        bot.send_message(chat_id,'Great! You have achived your goal')
        return 
      player.ask()
    else:
      bot.send_message(chat_id,'ooops')
      player.i += 1
      player.ask()
    

@bot.message_handler(commands=['data'])
def user_data(message):
  chat_id = message.chat.id 
  data = c.execute(f"SELECT * FROM users WHERE id={chat_id}")
  bot.send_message(chat_id,f'{data.fetchone()}')


bot.polling()
