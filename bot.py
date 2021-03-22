import asyncio 

import spotipy
import spotipy.util as ut

from pyrogram import Client, filters
from pyrogram.types import *

bot = Client('stopify',api_id=2810072,api_hash='2b1873a1e07e6c6c26319b6963d9aa4c',bot_token='1431085343:AAEy-AWMGiCvNUbC5K7mWvqgXjJaL9O8Y0Q')

async def getCurrentSong():
    token = spotipy.util.prompt_for_user_token(client_id='3334ecb597d0468b9d69fb6d09993a12',client_secret='6418baa27d734c3fb6695bbadf53bef2',username='Maybe Alive',scope='user-read-currently-playing',redirect_uri='http://localhost:8080/callback')

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
    messageId = 11
    chatId = -1001298132275

    while True:
        await asyncio.sleep(1)

        data = await getCurrentSong()

        if not data:
            text = 'ɴᴏᴛ ʟɪꜱᴛᴇɴɪɴɢ ᴀɴʏᴛʜɪɴɢ...ᴘʀᴏʙᴀʙʟʏ ꜱʟᴇᴇᴘɪɴɢ...'
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

bot.run(updateCurrentSong())