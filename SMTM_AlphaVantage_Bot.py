#discord library
import discord
from discord.ext import commands
from discord import File
# from alpha_vantage.timeseries import TimeSeries (now using alpha_vantage online)

#Pillow library : for Stock Profile Cards
from PIL import Image, ImageDraw, ImageFont

#etc.
import io
from io import BytesIO
import asyncio #to get timeout exception
import requests
import json
import os
import urllib.request

bot_prefix = 'av.'
bot_token = 'ODAzODM0NTQ3MTIwNTA0ODMy.YBDjQg.T3pFo-K1Th27-hOaI3rIDAqHJnA'
client = commands.Bot(command_prefix = bot_prefix)
av_key = '1P8QA9MTY0HCA79A' 

@client.event #function declarator: function will represent an event
async def on_ready(): #on_ready -> when the bot is ready
    print('Bot is ready')
    print(av_key)

#.ping 
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

#get data from alpha vantage
def get_data(input, function):
    base_url = 'https://www.alphavantage.co/query?'
    symbol = input.lower()
    response = requests.get(f'{base_url}function={function}&symbol={symbol}&apikey={av_key}')
    return response

#TSD
@client.command()
async def tsd(ctx, *, mess):

    print(f'User Input: {mess}')

    await ctx.send(f'Grabbing latest Time Series Daily Data for: {mess.upper()}...')
    response = get_data(mess, 'TIME_SERIES_DAILY_ADJUSTED')

    #get meta data info
    info = response.json()['Meta Data']['1. Information']
    #get the last refreshed from meta data
    last_ref = response.json()['Meta Data']['3. Last Refreshed']
    #get data from date: last_ref
    data = response.json()['Time Series (Daily)'][last_ref]
    #get ticker symbol from meta data
    symbol = response.json()['Meta Data']['2. Symbol']
    #get type (meta data info)

    print(data)
    await ctx.send(f'Symbol: {symbol.upper()}')
    await ctx.send(f'Time Series type: {info}')
    
    #print all data
    for i in data:
        await ctx.send(f'{i}: {data[i]}')
    
    await ctx.send(f'Completed')
    #example json
    #2021-01-26: {
    # '1. open': '143.6', 
    # '2. high': '144.3', 
    # '3. low': '141.37', 
    # '4. close': '143.16', 
    # '5. adjusted close': '143.16', 
    # '6. volume': '98390555', 
    # '7. dividend amount': '0.0000', 
    # '8. split coefficient': '1.0'}

#TS(1 min)
@client.command()
async def ts1(ctx, *, mess,text=None):

    print(f'User Input: {mess}')

    await ctx.send(f'Grabbing Time Series Data for: {mess.upper()}...')

    base_url = 'https://www.alphavantage.co/query?'
    function = 'TIME_SERIES_INTRADAY'
    interval = '1min'
    symbol = mess.lower()
    response = requests.get(f'{base_url}function={function}&symbol={symbol}&apikey={av_key}&interval={interval}')

    #get meta data info
    info = response.json()['Meta Data']['1. Information']
    #get the last refreshed from meta data
    last_ref = response.json()['Meta Data']['3. Last Refreshed']
    #get data from date: last_ref
    data = response.json()['Time Series (1min)'][last_ref]
    #get ticker symbol from meta data
    symbol = response.json()['Meta Data']['2. Symbol']

    #creating stock profile cards

    # --- create empty image ---

    IMAGE_WIDTH = 450
    IMAGE_HEIGHT = 300
    INNER_IMAGE_WIDTH = IMAGE_WIDTH - 20
    INNER_IMAGE_HEIGHT = IMAGE_HEIGHT - 20 

    # create empty image 600x300 
    image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT)) # RGB, RGBA (with alpha), L (grayscale), 1 (black & white)

    # --- draw on image ---
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 0, IMAGE_WIDTH, IMAGE_HEIGHT], fill=(46,48,54))
    draw.rectangle([20, 20, INNER_IMAGE_WIDTH, INNER_IMAGE_HEIGHT], fill=(125,205,230))

    # draw function and date text in top-left corner
    text = f'Time Series Intraday'
    
    file = open('Assets/fonts/Fraunces_9pt,Soft-SemiBold.ttf', 'rb')
    bytes_font = BytesIO(file.read())
    font = ImageFont.truetype(bytes_font, 20)
    text_width, text_height = draw.textsize(text, font=font)
    x = (INNER_IMAGE_WIDTH - text_width)//2 - 70
    y = (INNER_IMAGE_HEIGHT - text_height)//2 - 90

    draw.text( (x, y), text, fill=(255,255,255), font=font)

    # draw symbol text in top-right corner
    text = f'{symbol.upper()}'
    
    file = open('Assets/fonts/Poppins-Bold.ttf', 'rb')
    bytes_font = BytesIO(file.read())
    font = ImageFont.truetype(bytes_font, 40)
    
    text_width, text_height = draw.textsize(text, font=font)
    x = (INNER_IMAGE_WIDTH - text_width)//2 + 150
    y = (INNER_IMAGE_HEIGHT - text_height)//2 - 90

    draw.text( (x, y), text, fill=(46, 48, 54), font=font)

    # draw info text in bottom-left corner
    count = 0
    for i in data:
        text = f'{i}: {data[i]}'
        
        file = open('Assets/fonts/Poppins-Light.ttf', 'rb')
        bytes_font = BytesIO(file.read())
        font = ImageFont.truetype(bytes_font, 20)
        #font = ImageFont.truetype('./SMTM/Assets/fonts/Poppins-Light.ttf', 20)
        
        text_width, text_height = draw.textsize(text, font=font)
        x = (INNER_IMAGE_WIDTH - text_width)//2 - 100
        y = (INNER_IMAGE_HEIGHT - text_height)//2 +(25 * count)
        draw.text( (x, y), text, fill=(255,255,255), font=font)
        count = count + 1
    
    #adding avatar in bottom-right corner
    AVATAR_SIZE = 128

    # get URL to avatar
    # sometimes `size=` doesn't gives me image in expected size so later I use `resize()`
    avatar_asset = ctx.author.avatar_url_as(format='jpg', size=AVATAR_SIZE)

    # read JPG from server to buffer (file-like object)
    buffer_avatar = io.BytesIO()
    await avatar_asset.save(buffer_avatar)
    buffer_avatar.seek(0)

    # read JPG from buffer to Image 
    avatar_image = Image.open(buffer_avatar)

    # resize it 
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) # 

    x = (INNER_IMAGE_HEIGHT-AVATAR_SIZE)//2 + 200
    y = (INNER_IMAGE_HEIGHT-AVATAR_SIZE)//2 + 50
    image.paste(avatar_image, (x, y))
    # --- sending image ---

    # create buffer
    buffer_output = io.BytesIO()

    # save PNG in buffer
    image.save(buffer_output, format='PNG')    

    # move to beginning of buffer so `send()` it will read from beginning
    buffer_output.seek(0) 

    # send image
    await ctx.send(file=File(buffer_output, 'stockprofilecard.png'))

client.run(bot_token) #paste in Token (from developer portal)

