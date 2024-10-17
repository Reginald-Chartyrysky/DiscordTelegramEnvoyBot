#импортируем функционал из нужных библиотек
import discord
import telegram
import requests #библиотека для запросов к api
import json

#читаем файл, где храним нужную информацию, которую лучше скрывать или иметь возможность настраивать без изменения кода
with open('config.json', 'r') as file:
        config = json.load(file)

# инфа из конфига
telegram_token = config["telegram_token"]
telegram_chat_id = config["telegram_chat_id"]
telegram_message_thread_id = config["telegram_message_thread_id"]
discord_token = config["discord_token"]

#основной метод, запускающий бота
def runBot():
    #даем возможность клиенту дискорд бота читать сообщения (специфика ботов дискорда)
    message_intents = discord.Intents.default()
    message_intents.message_content = True

    #создаем клиент бота с этими привилегиями
    client = discord.Client(intents=message_intents)

    # у клиента бота есть определенные события, на которые мы здесь подписываемся
    # и будем на них определенным образом реагировать

    #реакция на запуск бота
    @client.event
    async def on_ready():
        print({client.user}, 'is live')

    # реакция на сообщения в дискорде
    @client.event
    async def on_message(message):

        #если автор – наш бот, выходим из функции
        if message.author == client.user:
            return
        
        #если канал не называется "объявления", выходим из функции
        if message.channel.name != "объявления":
            return
        
        # запускаем метод реакции на сообщение
        processMessage(message, message.content)

    # запускаем бота, передавая наш токен
    client.run(discord_token)


# метод обработки сообщения
def processMessage(message, user_message):
    # пробуем что-то сделать с возможной ошибкой
    try:
        # для каждого вложения в сообщении просто добавим ссылку в сам текст
        # телеграм дает превью ссылок, поэтому таким образом мы можем вставить в телеграмное сообщение
        # картинку из сообщения в дискорде
        for attach in message.attachments:

            # здесь мы используем формат HTML, при объявлении тега "a" мы указываем саму ссылку (в href =)
            # а внутри тега мы указываем, как ссылка будет отображаться: в нашем случае символом &#x200B, т.е. пустым местом,
            # чтобы ссылку не было видно в тексте сообщения, но телеграм все равно показал ее превью (т.е. картинку)
            user_message += f" <a href='{attach.url}'>&#x200B</a>" 
        
        # вызываем функцию отправки сообщения
        sendMessageTelegram(f"{message.author.name}: {user_message}")
    
    # при ошибке приложение не упадет, а сделает то, что описано ниже (т.е. запринтит ошибку в консоль)
    except Exception as error:
        print(error)

# метод отправки сообщения
def sendMessageTelegram(messageText):
    try:
        #ссылка на запрос api телеграма для отправки сообщений
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        #параметры запроса
        params = dict(
        chat_id = telegram_chat_id,
        text = messageText,
        parse_mode='HTML', #нужный нам парсинг для ссылок
        disable_web_page_preview='false', # запрет сокрытия превью ссылок
        message_thread_id = telegram_message_thread_id
        )

        #принтим ответ api телеграма на http запрос post
        print(requests.post(url, params).json())
    except Exception as error:
        print(error)
