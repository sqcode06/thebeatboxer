import telebot
import config
import downloader

bot = telebot.TeleBot(config.TOKEN)

mk_button_search = telebot.types.KeyboardButton('🔍 Search')
mk_button_playlists = telebot.types.KeyboardButton('▶ Playlists')
# mk_button_options = telebot.types.KeyboardButton('⚙ Settings')

main_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(mk_button_search)
main_keyboard.add(mk_button_playlists)
# main_keyboard.add(mk_button_options)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, config.START_MESSAGE, parse_mode='Markdown', reply_markup=main_keyboard)


@bot.message_handler(commands=['reset'])
def start(message):
    config.IS_WAITING_FOR_SEARCH = False
    config.IS_SEARCH_PROCESS_RUNNING = False
    config.IS_WAITING_FOR_SEARCH_OPTION_SELECTION = False
    config.IS_PROCESSING_AUDIO = False
    bot.send_message(message.chat.id, "Reset successful!")


@bot.message_handler(content_types=['text'])
def process(message):
    if message.text == '🔍 Search' and not config.IS_WAITING_FOR_SEARCH and not config.IS_SEARCH_PROCESS_RUNNING and not config.IS_WAITING_FOR_SEARCH_OPTION_SELECTION and not config.IS_PROCESSING_AUDIO:
        bot.send_message(message.chat.id, "What song do you want to listen?")
        config.IS_WAITING_FOR_SEARCH = True
    elif config.IS_WAITING_FOR_SEARCH:
        bot.send_message(message.chat.id, "Searching...")
        config.IS_SEARCH_PROCESS_RUNNING = True
        config.IS_WAITING_FOR_SEARCH = False
        select_message, config.IDS = downloader.get_search_list(message.text)
        bot.send_message(message.chat.id, "*Choose one of the following:*\n" + select_message, parse_mode='Markdown')
        config.IS_SEARCH_PROCESS_RUNNING = False
        config.IS_WAITING_FOR_SEARCH_OPTION_SELECTION = True
    elif config.IS_WAITING_FOR_SEARCH_OPTION_SELECTION:
        if represents_int(message.text) and int(message.text) in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
            bot.send_message(message.chat.id, "Good! The audio is downloading...")
            config.IS_WAITING_FOR_SEARCH_OPTION_SELECTION = False
            config.IS_PROCESSING_AUDIO = True
            downloader.download_audio(config.IDS[int(message.text)])
            config.IDS.clear()
            type_markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            type_markup.add(telebot.types.InlineKeyboardButton("Voice message", callback_data='voice'), telebot.types.InlineKeyboardButton("Audio file", callback_data='file'))
            bot.send_message(message.chat.id, "How should I send you the music?", reply_markup=type_markup)
        else:
            bot.send_message(message.chat.id, "The number is irregular, please select one of the options")
    if message.text == '▶ Playlists' and not config.IS_WAITING_FOR_SEARCH and not config.IS_SEARCH_PROCESS_RUNNING and not config.IS_WAITING_FOR_SEARCH_OPTION_SELECTION and not config.IS_PROCESSING_AUDIO:
        bot.send_message(message.chat.id, "In development now!")


@bot.callback_query_handler(func=lambda call: True)
def callback_method(call):
    audio = open(config.TEMP_AUDIO_FOLDER + 'audio.mp3', "rb")
    try:
        if call.message:
            if call.data == 'voice':
                bot.send_voice(call.message.chat.id, audio)
            elif call.data == 'file':
                bot.send_document(call.message.chat.id, audio)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="How should I send you the music?", reply_markup=None)
            config.IS_PROCESSING_AUDIO = False
            audio.close()
    except Exception as e:
        print(repr(e))


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


bot.polling(none_stop=True)
