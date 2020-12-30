import discord
import json
import pdb

with open('config.json', 'r') as f:
    config = json.load(f)

token = config['bottoken']


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        found = False

        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')

        if message.content.startswith('!channel'):
            found = True
            await message.channel.send(f'hey {message.channel.mention}! your channel info is {message.channel}')

        if message.content.startswith('!author'):
            found = True
            await message.channel.send(f'hey {message.author.mention}! Your discord id is {message.author}')

        # if message.content.contains('rickroll'):
        #     found = True
        #     await message.channel.send(f'Here ya go! https://www.youtube.com/watch?v=xn38dg0YrzY')

        if message.content.startswith('!tdb'):
            pdb.set_trace()
            await message.channel.send(f'Hello {message.author}!')
            await message.channel.send('testing stuff')

        if found:
            await message.delete


client = MyClient()
client.run(token)
