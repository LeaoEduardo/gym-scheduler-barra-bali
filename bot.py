import os
import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
CHAT_ID = os.environ.get('CHAT_ID', None)
WEBHOOK = os.environ.get('WEBHOOK', None)
PORT = int(os.environ.get('PORT', 5000))

days_of_the_week = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
}

today_hours_dictionary = {
    6:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    7:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    8:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    9:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    10:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    17:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    18:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    19:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    20:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    }, 
    21:{
        'musc':[],
        'aerobio':[],
        'salinha':[],
    },
}

tomorrow_hours_dictionary = today_hours_dictionary.copy()

def reset(hour_dict):
    for key in hour_dict:
        hour_dict[key].clear()

def format_message(curr_hour, today, tomorrow):
    s = ''
    s += f'*{today}*\n\n'
    for hour in today_hours_dictionary:
        if hour >= curr_hour:
            s += f'*{hour}h*\n'
            for m in range(5):
                if len(today_hours_dictionary[hour]['musc']) <= m:
                    s += 'Musculação: \n'
                else:
                    name = today_hours_dictionary[hour]['musc'][m]
                    s += f'Musculação: {name}\n'
            for a in range(2):
                if len(today_hours_dictionary[hour]['aerobio']) <= a:
                    s += 'Aerobio: \n'
                else:
                    name = today_hours_dictionary[hour]['aerobio'][a]
                    s += f'Aerobio: {name}\n'
            if len(today_hours_dictionary[hour]['salinha']) < 1:
                s += 'Salinha: \n'
            else:
                name = today_hours_dictionary[hour]['salinha'][0]
                s += f'Salinha: {name}\n'
            s += '\n'
        else:
            reset(today_hours_dictionary[hour])
    if curr_hour >= 16:
        s += f'*{tomorrow}*\n\n'
        for hour in tomorrow_hours_dictionary:
            s += f'*{hour}h*\n'
            for m in range(5):
                if len(tomorrow_hours_dictionary[hour]['musc']) <= m:
                    s += 'Musculação: \n'
                else:
                    name = tomorrow_hours_dictionary[hour]['musc'][m]
                    s += f'Musculação: {name}\n'
            for a in range(2):
                if len(tomorrow_hours_dictionary[hour]['aerobio']) <= a:
                    s += 'Aerobio: \n'
                else:
                    name = tomorrow_hours_dictionary[hour]['aerobio'][a]
                    s += f'Aerobio: {name}\n'
            if len(tomorrow_hours_dictionary[hour]['salinha']) < 1:
                s += 'Salinha: \n'
            else:
                name = tomorrow_hours_dictionary[hour]['salinha'][0]
                s += f'Salinha: {name}\n'
            s += '\n' 
    return s

def list_schedule(update, context):
    """Send a message when the command /horarios is issued."""
    current_hour = datetime.datetime.now().hour
    today = days_of_the_week[datetime.datetime.today().weekday()]
    tomorrow = days_of_the_week[datetime.datetime.today().weekday()+1]
    
    update.message.reply_text(format_message(current_hour, today, tomorrow), parse_mode='Markdown')

def schedule_musc(update, context):
    """Send a message when the command /marcar is issued."""
    try:
        name, hour = tuple(context.args)
        hour = int(hour)
    except:
        update.message.reply_text(f"Argumentos inválidos por favor digite:\n /marcar_musc SeuNome Horario.")
        return
    today_hours_dictionary[hour]['musc'].append(name)
    print(today_hours_dictionary)

    update.message.reply_text(f'Marcado {name} para musculação hoje as {hour} horas!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text('Não entendi esse comando. Tente novamente.')


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("listar_horarios", list_schedule))
    dp.add_handler(CommandHandler("marcar_musc", schedule_musc))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # # log all errors
    # dp.add_error_handler(error)

    # Uncomment this part when deploing to heroku
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=BOT_TOKEN,
                          webhook_url=WEBHOOK + BOT_TOKEN)

    # Uncomment to test locally
    # updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()