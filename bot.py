import asyncio 

import spotipy
import spotipy.util as ut

from pyrogram import Client, filters
from pyrogram.types import *

import os

apiId = int(os.getenv('Api_Id'))
apiHash = os.getenv('Api_Hash')
botToken = os.getenv('Bot_Token')

spotifyClientId = os.getenv('Spotify_Client_Id')
spotifyClientSecret = os.getenv('Spotify_Client_Secret')
spotifyUsername = os.getenv('Spotify_Username')

bot = Client('stopify',api_id=apiId,api_hash=apiHash,bot_token=botToken)

async def getCurrentSong():
    token = spotipy.util.prompt_for_user_token(client_id=spotifyClientId,client_secret=spotifyClientSecret,username=spotifyUsername,scope='user-read-currently-playing',redirect_uri='http://localhost:8080/callback')

    if token:
        sp = spotipy.Spotify(auth=token)
        response = sp.currently_playing()
    else:
        return None 

    if not response:
        return None

    data = {
    "name": response['item']['name'],
    "artists": ', '.join([f'''<a href="{artist['external_urls']['spotify']}">{artist['name']}</a>''' for artist in response['item']['artists']]),
    "album": f'''<a href="{response['item']['album']['external_urls']['spotify']}">{response['item']['album']['name']}</a>''',
    "link": response['item']['external_urls']['spotify'],
    "image": response['item']['album']['images'][0]['url'],
    "isPlaying": response['is_playing']
    }

    if response['context']:
        if response['context']['type'] == 'playlist':
            playlistLink = response['context']['external_urls']['spotify']
            playlistId = playlistLink.split('/')[-1]
            playlistName = sp.user_playlist(user=None,playlist_id=playlistId,fields='name')['name']
            data['playlistName'] = playlistName
            data['playlistLink'] = playlistLink

    return data
        

async def updateCurrentSong():
    messageId = int(os.getenv('Message_Id'))
    chatId = int(os.getenv('Chat_Id'))

    while True:
        await asyncio.sleep(1)

        for _ in range(5):
            try:
                data = await getCurrentSong()
            except:
                data = None 
        
        if not data:
            continue

        if not data:
            text = os.getenv('AFK_Text')
            link = 'https://open.spotify.com/user/31kjpvfkckxjyoxst3l25ok7jf4y'
            button = InlineKeyboardMarkup([[
            InlineKeyboardButton('Profile 🤍',url=link)
                        ]])
            try:
                async with bot:                
                    await bot.edit_message_media(chat_id=chatId,message_id=messageId,media=InputMediaPhoto(media=link,caption=text,parse_mode='html'),reply_markup=button)
            except Exception as e:
                pass
        
        else:
            text = f'''ʟɪꜱᴛᴇɴɪɴɢ: <b>{data['name']}</b>''' + '<i> *Paused</i>' if not data['isPlaying'] else f'''ʟɪꜱᴛᴇɴɪɴɢ: <b>{data['name']}</b>'''
            text += f'''\nʙʏ: {data['artists']}'''
            text += f'''\nꜰʀᴏᴍ: {data['album']}'''

            if 'playlistName' in data.keys():
                text += f'''\nᴘʟᴀʏʟɪꜱᴛ: <a href="{data['playlistLink']}">{data['playlistName']}</a>'''
            
            pic = data['image']
            link = data['link']
            button = InlineKeyboardMarkup([[
                InlineKeyboardButton('Listen Along 🖤',url=link)
            ]])

            try:
                async with bot:
                    await bot.edit_message_media(chat_id=chatId,message_id=messageId,media=InputMediaPhoto(media=pic,caption=text,parse_mode='html'),reply_markup=button)
            except Exception as e:
                pass

@bot.on_message(filters.command('start'))
async def start(client:Client,msg:Message):
    startText = os.getenv('Start_Text')
    await msg.reply_text(startText)
    await msg.reply_sticker('CAACAgQAAxkBAAKtfmBYwwNSejLyJwSuHAmVZclNq5vXAALCCAACMC2BUSZejXISPFloHgQ')

bot.run(updateCurrentSong())