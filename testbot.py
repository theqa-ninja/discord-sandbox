import discord
import json
import pdb
import os

try:
    with open('config.json', 'r') as f:
        config = json.load(f)

    token = config['bottoken']
except FileNotFoundError:
    token = os.environ['bottoken']


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user.name} with id {self.user.id}')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        guild = message.guild
        secretMessage = False
        message_array = message.content.split(' ')

        if message_array[0] == '!delete':
            secretMessage = True
            await message.channel.send('message has been purged!')

        elif message_array[0] == '!tdb':
            # pdb.set_trace()
            # await message.channel.send(f'Hello {message.author}!')
            await message.channel.send('testing stuff')
        elif message_array[0] == '!resetServer':
            if (message.channel.name != "botcommands"):
                return
            await message.channel.send(f'okay time to reset this server!')
            # pdb.set_trace()
            for chanId in guild.channels:
                if chanId.name in {'general', 'setup', 'botcommands'}:
                    continue
                await chanId.delete()
        elif message_array[0] == '!channel':
            await message.channel.send(f'hey {message.channel.mention}! your channel info is {message.channel}')
        elif message_array[0] == '!test':
            await message.channel.send(f'hey {message.channel.mention}! you thought this was a test?! Good news, there\'s a curve!')
        elif message_array[0] == '!assignTeam':
            input_count = 3
            if (message.channel.name != "botcommands"):
                return
            if len(message_array) > input_count:
                await message.channel.send(f'this command needs {input_count} parameters')
                return
        elif message_array[0] == '!createTeam':
            if (message.channel.name != "botcommands"):
                return
            input_count = 2
            if len(message_array) != input_count:
                await message.channel.send(f'this command needs {input_count} parameters')
                return
            newChanName = message_array[1]
            # pdb.set_trace()
            if newChanName in [j.name for j in guild.channels]:
                await message.channel.send(f'Sorry, {newChanName} already exists')
                return
            # doesn't exist so let's create it
            teamCat = [s for s in guild.categories if "team channels" in s.name][0]
            newChan = await guild.create_text_channel(newChanName, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    message.author: discord.PermissionOverwrite(read_messages=True)
                    },
                category=teamCat)
            print(f'created new text channel {newChan}')
            await message.channel.send(f'created new text channel {newChan.mention}')
            newChan = await guild.create_voice_channel(newChanName, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    message.author: discord.PermissionOverwrite(read_messages=True)
                    },
                category=teamCat)
            print(f'created new voice channel {newChan}')
            await message.channel.send(f'created new voice channel {newChan.mention}')

        elif message_array[0] == '!author':
            await message.channel.send(f'hey {message.author.mention}! Your discord id is {message.author}')

        elif 'rickroll' in message.content:
            await message.channel.send('Here ya go! https://www.youtube.com/watch?v=xn38dg0YrzY')

        elif message.content == "!setupServer":
            print(f'channel: {message.channel.name}')
            if (message.channel.name == "general"):
                secretMessage = True
                print('running setup')
                print(f"channel list: {[j.name for j in guild.channels]}")

                if "admin stuff" not in [j.name for j in guild.categories]:
                    adminCat = await guild.create_category("admin stuff", overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await message.channel.send("Created the admin stuff Category only visible to admins")
                else:
                    adminCat = [s for s in guild.categories if "admin stuff" in s.name][0]

                botChan = [s for s in guild.text_channels if "botcommands" in s.name]
                botChanFound = False
                # no botcommands text channel found
                if (botChan != []):
                    botChan = botChan[0]
                    botChanFound = True
                    # it's in the wrong category
                    if (botChan.category != adminCat):
                        # await botChan.delete(reason=None)
                        await botChan.edit(category=adminCat)

                if (not botChanFound):
                    botChan = await guild.create_text_channel("botcommands", category=adminCat)
                    await botChan.set_permissions(guild.default_role, read_messages=False)
                    await botChan.set_permissions(guild.me, read_messages=True, send_messages=True)


                # import time; time.sleep(1)
                await botChan.send(f'made {botChan.mention} private')

                if "announcements" not in [j.name for j in guild.text_channels]:
                    anno = await guild.create_text_channel("announcements", overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    })
                    await botChan.send(f'Created the {anno.mention} only typable to admins')

                if "recent-answers" not in [j.name for j in guild.text_channels]:
                    recentChan = await guild.create_text_channel("recent-answers", category=adminCat, overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await botChan.send(f'Created the {recentChan.mention} only visible to admins')

                if "team channels" not in [j.name for j in guild.categories]:
                    await guild.create_category("team channels", overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await botChan.send("Created the Team Channels Category only visible to admins")

                if "looking-for-teammate" not in [j.name for j in guild.text_channels]:
                    lfg = await guild.create_text_channel("looking-for-teammate")
                    await botChan.send(f'Created the {lfg.mention} visible to all')

        if secretMessage:
            await message.delete(delay=None)


client = MyClient()
client.run(token)
