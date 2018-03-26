import json
import requests
import time
import urllib
#import markov
from textblob import TextBlob

import chatbot_config
from util import all_keystrings, determine_text_type, calc_part_of_day, response_howre_you, generate_poem, bring_to_poem_style


TOKEN = chatbot_config.token()
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
sentiment_analysis = False

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_image_url(url):
    response = requests.get(url)
    #content = response.content.decode("base64")
    return response


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text) # urllib.parse.quote_plus(text) # (python3)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def send_photo(chat_id):
    url = URL + "sendMessage?photo={}&chat_id={}".format(open('meme.jpg', 'rb'), chat_id)
    get_image_url(url)


def process_text(update):
    text = update['message']['text']
    chat = update['message']['chat']['id']

    first_name = update['message']['from']['first_name']

    text_type_similarities = [determine_text_type(text, keystrings) for keystrings in all_keystrings]

    max_similarity = max(text_type_similarities)
    max_similarity_index = text_type_similarities.index(max(text_type_similarities))


    if max_similarity > 0.3:
        if max_similarity_index == 0:
            send_message("Good day to thee " + first_name + "! How dost thou, my friend? ", chat)

        elif max_similarity_index == 1:
            part_of_day = calc_part_of_day()
            message = response_howre_you(part_of_day)
            send_message(message, chat)
            time.sleep(2)
            send_message("Or to answer the question thou askest: I'm doing most wondrous", chat)

        elif max_similarity_index == 2:
            send_message("I will help you", chat) #nog veranderen

        elif max_similarity_index == 3:
            send_message("I wilt writeth a poem special for thee", chat)
            send_message("do thee want to heareth a poem about love, about nature, or about the mythology?", chat)

        elif max_similarity_index == 4:
            poem = generate_poem("love")
            string_message = ''.join(poem)
            right_style = bring_to_poem_style(string_message)
            send_message("Ah, I feel so very much inspired! I hope thee likest my poem about love", chat)
            time.sleep(3)
            send_message(right_style, chat)
            time.sleep(3)
            send_message("May I ask thee, my friend. Did you enjoyeth the poem?", chat)
            global sentiment_analysis
            sentiment_analysis = True

        elif max_similarity_index == 5:
            poem = generate_poem("nature")
            string_message = ''.join(poem)
            right_style = bring_to_poem_style(string_message)
            send_message("Inspiration has striken me like thunder. Enjoyest this poem about the beauty of nature!", chat)
            time.sleep(3)
            send_message(right_style, chat)
            time.sleep(3)
            send_message("May I ask thee, my friend. Did you enjoyeth the poem?", chat)
            global sentiment_analysis
            sentiment_analysis = True

        elif max_similarity_index == 6:
            poem = generate_poem("mythology")
            string_message = ''.join(poem)
            right_style = bring_to_poem_style(string_message)
            send_message("Greek gods, the most wondrous fairytale creatures... Let thy be amused about this poem on mythology", chat)
            time.sleep(3)
            send_message(right_style, chat)
            time.sleep(3)
            send_message("May I ask thee, my friend. Did you enjoyeth the poem?")
            global sentiment_analysis
            sentiment_analysis = True



        # als heel kort berichtje gestuurd wordt (en dat berichtje ook niet echt op 'hi' ofzo lijkt) gaat Shakespeare van onderwerp veranderen
        elif len(text) < 4:
            send_message("What do you want to talk about?", chat)

    # If the maxiumum similar
    else:
        send_message("Alack, I do not understand what it is thy is saying " + first_name + ". I cry you mercy,  can thou say that again", chat)

def process_sticker(update):
    chat = update['message']['chat']['id']
    send_photo(chat)
    send_message("That's a nice sticker", chat)

def process_sentiment(update):
    text = update['message']['text']
    chat = update['message']['chat']['id']

    blob = TextBlob(text)
    subjectivity = blob.sentiment[1]
    polarity = blob.sentiment[0]


    if polarity < -0.2:
        send_message("Alack, I tried so hard to maketh a sonnet worthy of thee. Mea culpa thee did not liketh it. Maybe I "
                     "can writeth the a new poem? Does thee wanteth to hear about love, nature or mythology?", chat)
    elif polarity > -0.2 and polarity < 0.2:
        send_message("Ah suspicion always haunts the guilty mind, I am not sure whether it is true what thy sayest about my"
                     "poem. Maybe I can writeth thee a new poem? Does thee wanteth to hear about love, nature or mythology?", chat)
    else:
        send_message("O Lord that lends me life, Lend me a heart replete with thankfulness! I am glad thou likest the sonnet. Does thee wanteth to hear another one about love, nature or mythology?", chat)
    global sentiment_analysis
    sentiment_analysis = False




def main():
    #chatbotconfig.init_nltk()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            print("Here")
            last_update_id = get_last_update_id(updates) + 1
            #echo_all(updates)
            for update in updates['result']:
                print(update)
                print(sentiment_analysis)
                if 'text' in update['message'] and sentiment_analysis:
                    process_sentiment(update)
                elif 'text' in update['message']:
                    print(update)
                    process_text(update)
                elif 'sticker' in update['message']:
                    process_sticker(update)
                #print(update['message']['sticker'])
                #print(update)
        time.sleep(0.5)


if __name__ == '__main__':
    main()


'''
Ideas:
- determine text type verbeteren!! (hij is nu nogal dom)
- mss als Shakespeare het onderwerp niet herkent een random ander gedicht geven
'''