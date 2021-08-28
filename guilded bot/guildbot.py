# import asyncio
import guilded
import pdb
# import websockets
# import requests

token = 'LXzltYEOLtju/Rea4kQcIWQPKPbJ/53EBZIIu9OQu1h/zJLAQFFbJc6jb9fbLyuDiFiohaN9S3jubsQSle4ySQ=='
# base_url = 'https://www.guilded.gg/api/v1/channels/'
# headers = {
#     'Authorization': f'Bearer {token}',
#     'Accept': 'application/json',
#     'Content-type': 'application/json'}

# websocket_url = 'wss://api.guilded.gg/v1/websocket'


client = guilded.Client('1c23fe15-761d-40f9-9948-a5cdc6d6ea65')

@client.event
async def on_ready():
    print('Ready')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'ping':
        await message.channel.send('pong')

client.run(token)

# async def echo(websocket, path):
#     pdb.set_trace()

#     print("blargh")
#     async for message in websocket:
#         await websocket.send(message)

# async def main():
#     async with websockets.serve(echo, websocket_url, 8765):
#         await asyncio.Future()  # run forever

# asyncio.run(main())
# # r = requests.get(base_url + '{channelId}/messages', headers = headers)


# # #Get the HTTP Response Code
# # print(r.status_code)

# # #Get HTTP Response Body
# # print(r.text)


