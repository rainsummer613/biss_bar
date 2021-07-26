import telebot
import re
import pickle
import argparse
from ome import Genome
from utils import *

bot = telebot.TeleBot('1913636701:AAEyF8Yym-tp2a5vlxO6ympHGR0TPftPWag')
states_dict = {0: 'wait start', 1: 'wait url', 2: 'wait name'}
state = states_dict[0]
name, url = None, None

model_path = 'res/models/rf11_kmer31.pkl'
vectorizer_path = 'res/vectors/kmer31_plus_tfidf_vectorizer.pkl'
labels= ['непатогенная', 'патогенная']
error_msg = 'Что-то пошло не так. Пожалуйста, проверьте корректность ссылки или попробуйте загрузить другую!'

def load_models(model_path, vectorizer_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

print('models loading')
model, vectorizer = load_models(model_path, vectorizer_path)
print('models loaded')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global state
    bot.send_message(message.chat.id, 'Привет, я биобот. Немножко разбираюсь в микробиоме кишечника! Хотите проверить патогенность бактерии? Напишите команду /bact')
    
@bot.message_handler(commands=['bact'])
def handle_hello(message):
    global state
    state = states_dict[0]
    bot.send_message(message.chat.id, 'Пришлите мне рабочую ссылку на скачивание архива с геномом в формате .fna.gz\nА я определю, насколько эта бактерия патогенная.')  
                 
@bot.message_handler(regexp='https?.+\.fna\.gz')
def handle_url(message):
    global state
    if state == states_dict[1]:
        url = message.text
        bot.send_message(message.chat.id, 'Отлично, спасибо! Как называется ваша бактерия?')
        state = states_dict[2]
                     
@bot.message_handler(regexp='.+')
def handle_name(message):
    global state
    if state == states_dict[2]:
        name = message.text  
        bot.send_message(message.chat.id, f'Супер, начинаю анализировать бактерию {message.text}')
        
        try:
            bot.send_message(message.chat.id, f'скачиваю файл...')
            genome = Genome(name, opt.url)
            bot.send_message(message.chat.id, f'анализирую геном...')
            genome.get_kmers()
            vector = vectorizer.transform([' '.join(genome.kmers['all'])])
            pred = model.predict(vector)   
            res = labels[pred[0]]
        except:
            res = error_msg
            state = 0
        bot.send_message(message.chat.id, res)
        state = 0
                     
@bot.message_handler(commands=['help'])
def handle_help(message):
    global state
    if state == 0:
        msg = 'Хотите проверить патогенность бактерии? Напишите команду /bact'
    elif state == 1:
        msg = 'Пришлите мне рабочую ссылку на скачивание архива с геномом в формате .fna.gz\nА я определю, насколько эта бактерия патогенная.'
    elif state == 2:
        msg = 'Пожалуйста, напишите название бактерии'
    bot.send_message(message.chat.id, msg)
                     
bot.polling(none_stop=True)
print('bot started')
