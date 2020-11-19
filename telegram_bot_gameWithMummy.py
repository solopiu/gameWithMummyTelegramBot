# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 17:19:45 2020

@author: arianna
"""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import random
import os
import urllib

import bs4

random.seed(1234)

def import_vocab():
    def create_vocab():
        '''
        link sono fatti con lettera.html la prima pagina
        poi _i andando avanti
        '''
        alfabeto = "A – B – C – D – E – F – G – H – I – J – K – L – M – N \
        – O – P – Q – R – S – T – U – V – W – X – Y – Z".split(" – ")
        alfabeto = [a.lower() for a in alfabeto]
        parole = []
        for a in alfabeto[2:]:
            print("[INFO] Adding vocabulary letter: ", a)
            i = 1
            while True:
                if i == 1: 
                    link = "https://dizionari.repubblica.it/Italiano/{}.html".format(a)
                else:
                    link = "https://dizionari.repubblica.it/Italiano/{}_{}.html".format(a,i)
                try:
                    webpage = str(urllib.request.urlopen(link).read().decode('utf-8'))
                    soup = bs4.BeautifulSoup(webpage)
                    mydivs = soup.find("div", {"id": "lettera","class": "descrizione"}).findAll('li')
                    #print(mydivs)
                    
                    for hit in mydivs:
                        parole.append(hit.text)
                    
                    i+=1
                except Exception as e:
                    print(i)
                    break
        import csv
        with open('ita_dict.csv', 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(parole)
        return parole
    
    
    data_path = 'ita_dict.csv'
    if not os.path.exists(data_path):
        text_words = create_vocab()
    else:
        import csv
        with open(data_path, newline='') as infile:
            text_words = list(csv.reader(infile))[0]
    return text_words

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Ciaooo! Gioco che facevamo io e mamma.\nLo scopo del gioco è scrivere una parola che inizi con le ultime due lettere della parola precedente.\nEsempio. io dico pane, il bot risponde nespola, io dico lampione ecc.\nNon si può dire una parola già detta\nSe non sai andare avanti scrivi non lo so')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Gioco che facevamo io e mamma.\nLo scopo del gioco è scrivere una parola che inizi con le ultime due lettere della parola precedente.\nEsempio. io dico pane, il bot risponde nespola, io dico lampione ecc.\nNon si può dire una parola già detta\nSe non sai andare avanti scrivi non lo so')

def elimina_accenti(parola):
    if "à" in parola:
        parola = parola.replace("à", "a")
    if "é" in parola:
        parola = parola.replace("é", "e")
    if "è" in parola:
        parola = parola.replace("è", "e")
    if "ì" in parola:
        parola = parola.replace("ì", "i")
    if "ò" in parola:
        parola = parola.replace("ò", "o")
    if "ù" in parola:
        parola = parola.replace("ù", "u")
    return parola

def echo(update, context):
    """."""
    global vocab
    global parole_usate
    fine = False
    io = update.message.text.lower()
    
    io = elimina_accenti(io)
    
    new = io[-2:]
    #compara nuova parola con l'ultima
    if len(parole_usate) > 0:
        ult = parole_usate[-1]
        if not io.startswith(ult[-2:]):
            update.message.reply_text("Hai perso, non hai usato le ultime due lettere della parola precedente.\nNuova partita.")
            parole_usate = []
            fine = True
            
    if io in parole_usate and fine==False:
        update.message.reply_text("Hai perso, l'hai già detto.\nNuova partita.")
        parole_usate = []
    
    if io not in vocab and fine==False:
        update.message.reply_text("Mai sentita questa parola. Te la do buona. Esiste davvero?")
        
    
    parole_usate.append(io)
    if io != "non lo so":
        first2let = [w for w in vocab if w.startswith(new)]
        if len(first2let) > 0:
            while True:
                idx = random.randint(0, len(first2let)-1)
                print(idx, len(first2let))
                if first2let[idx] not in parole_usate:
                    update.message.reply_text(first2let[idx])
                    parole_usate.append(first2let[idx])
                    break
        else:
            update.message.reply_text("Non so rispondere. Hai vinto :(.\nNuova partita.")
            parole_usate = []
            
    else:
        update.message.reply_text("Hai persooooo. Nuova partita.")
        parole_usate = []

#def stop(update, context):
#    update.message.reply_text('Ok. Se vuoi facciamo una nuova partita.')
#    main()


def main():
    """Start the bot."""
    global vocab
    global parole_usate
        
    vocab = import_vocab()
    parole_usate=[]
        
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

#    dp.add_handler(CommandHandler('r', stop))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()