import discord
import json
import logging
from logging.config import fileConfig
import pdb
import os
from discord.ext import commands

fileConfig('logging.ini')

def isMod(author_member):
    author_roles = author_member.roles
    if len([s for s in author_roles if (mod_role_name == s.name) or (admin_role_name == s.name)]) > 0:
        return True
    else:
        return False

try:
    with open('config.json', 'r') as f:
        config = json.load(f)

    token = config['bottoken']
    help_chan_name = config['help_channel']
    bot_chan_name = config['bot_spam']
    announce_chan_name = config['announcements']
    admin_chan_list = config['admin_channels'].split(',')
    public_chan_list = config['public_channels'].split(',')
    admin_role_name = config['admin_role']
    mod_role_name = config['mod_role']
    keep_chan_list = config['channels_to_keep'].split(',')

except FileNotFoundError:
    token = os.environ['bottoken']

bot_intents = discord.Intents.default()
bot_intents.members = True
bot_intents.presences = True
client = discord.Client(intents=bot_intents)

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user.name} with id {client.user.id}')
    logging.info('------')
    logging.warning('charging the capacitors')
    logging.error('Danger, I\'m alive!')

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == client.user.id:
        return

    guild = message.guild
    secretMessage = False
    temp = [s for s in guild.channels if bot_chan_name == s.name]
    if len(temp)>0:
        bot_chan = temp[0]
    else:
        bot_chan = None
    mod_check = isMod(message.author)
    mod_role = [s for s in guild.roles if mod_role_name == s.name][0]
    message_array = message.content.strip().split(' ')

    if message_array[0] == '!tdb':
        # pdb.set_trace()
        # await message.channel.send(f'Hello {message.author}!')
        await message.channel.send(f'hey {message.author.name}! your channel info is {message.channel.mention}')

    # for resetting the server after i screwed it up
    elif message_array[0] == '!resetServer':
        if (message.channel.name != bot_chan_name):
            return
        if (not mod_check):
            return
        await message.channel.send(f'okay time to reset this server!')
        # pdb.set_trace()
        for chanId in guild.channels:
            if chanId.name in keep_chan_list:
                continue
            await chanId.delete()
    # elif message_array[0] == '!channel':
    #     await message.channel.send(f'hey {message.author.name}! your channel info is {message.channel.mention}')
    # elif message_array[0] == '!test':
    #     await message.channel.send(f'hey {message.channel.mention}! you thought this was a test?! Good news, there\'s a curve!')

    # when participants need help!
    elif message_array[0] == '!help':
        input_count = 2
        if len(message_array) < input_count:
            await message.reply(f'Please include some helpful description after the `!help` else GameControl doesn\'t know what to help you with')
            return
        newChanName = message_array[1]
        # get the help channel
        help_chan = [s for s in guild.channels if help_chan_name == s.name][0]
        # send message
        await help_chan.send(f'{message.author.mention} of team {message.channel.mention} requested \n> {message.content} \n{message.jump_url}')
        # send a reply to let the user know that we're getting help for them
        await message.reply(f'I\'ve notified GameControl that you could use some help {message.author.name}')

    # TODO
    # adding new people to a team
    elif message_array[0] == '!assignTeam':
        if (not mod_check):
            return
        input_count = 3
        # if (message.channel.name != bot_chan_name):
        #     return
        if len(message_array) < input_count:
            await bot_chan.send(f'wrong format.  Please follow `!assignTeam <team name> <mention user>`')
            return
        # find the team channels
        chans = [s for s in guild.channels if message_array[1] == s.name]
        if len(chans) != 2:
            await bot_chan.send(f'no team {message_array[1]} found')
            return
        else:
            add_user = None
            if message_array[2].startswith("<@!"):
                add_id = int(message_array[2].replace("<@!", "").replace(">", ""))
                add_user = guild.get_member(add_id)
            else:
                add_name = " ".join(message_array[2:])
                add_user = guild.get_member_named(add_name)
                if add_user is None:
                    await bot_chan.send(f'no user named found from `{message.content}')
                    return

            for chan in chans:
                await chan.edit(overwrites={add_user: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
                await bot_chan.send(f'added {add_user} to {chan.mention}')
        memberId = message_array[2]

    # Creates new teams
    elif message_array[0] == '!createTeam':
        if (not mod_check):
            return
        if (message.channel.name != bot_chan_name):
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
        mod_role = [s for s in guild.roles if mod_role_name == s.name][0]
        teamCat = [s for s in guild.categories if "team channels" == s.name][0]
        newChan = await guild.create_text_channel(newChanName, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                mod_role: discord.PermissionOverwrite(read_messages=True),
                message.author: discord.PermissionOverwrite(read_messages=True)
                },
            category=teamCat)
        print(f'created new text channel {newChan}')
        await message.channel.send(f'created new text channel {newChan.mention}')
        newChan = await guild.create_voice_channel(newChanName, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                mod_role: discord.PermissionOverwrite(read_messages=True),
                message.author: discord.PermissionOverwrite(read_messages=True)
                },
            category=teamCat)
        print(f'created new voice channel {newChan}')
        await message.channel.send(f'created new voice channel {newChan.mention}')

    elif message_array[0] == '!author':
        await message.channel.send(f'hey {message.author.mention}! Your discord id is {message.author}')

    elif 'rickroll' in message.content:
        await message.channel.send('Here ya go! https://www.youtube.com/watch?v=xn38dg0YrzY')

    elif message_array[0] == "!setupServer":
        if (not mod_check):
            return
        if (message.channel.name == "general"):
            secretMessage = True
            print('running setup')
            print(f"channel list: {[j.name for j in guild.channels]}")

            mod_role

            if "admin stuff" not in [j.name for j in guild.categories]:
                adminCat = await guild.create_category("admin stuff", overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await message.channel.send("Created the admin stuff Category only visible to admins")
            else:
                adminCat = [s for s in guild.categories if "admin stuff" == s.name][0]

            botChan = [s for s in guild.text_channels if bot_chan_name == s.name]
            botChanFound = False
            # no botcommands text channel found
            if (botChan != []):
                botChan = botChan[0]
                botChanFound = True
                # it's in the wrong category
                if (botChan.category != adminCat):
                    await botChan.edit(category=adminCat)
                    await botChan.send(f'made {botChan.mention} private')

            if (not botChanFound):
                botChan = await guild.create_text_channel(bot_chan_name, category=adminCat)
                await botChan.set_permissions(guild.default_role, read_messages=False)
                await botChan.set_permissions(guild.me, read_messages=True, send_messages=True)
                await botChan.send(f'created {botChan.mention} and made private')

            if announce_chan_name not in [j.name for j in guild.text_channels]:
                anno = await guild.create_text_channel(announce_chan_name, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                })
                await botChan.send(f'Created the {anno.mention} only typable to admins')

            for admin_chan_name in admin_chan_list:
                if admin_chan_name not in [j.name for j in guild.text_channels]:
                    admin_chan = await guild.create_text_channel(admin_chan_name, category=adminCat, overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await botChan.send(f'Created the {admin_chan.mention} only visible to admins')

            if "recent-answers" not in [j.name for j in guild.text_channels]:
                recentChan = await guild.create_text_channel("recent-answers", category=adminCat, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send(f'Created the {recentChan.mention} only visible to admins')

            if help_chan_name not in [j.name for j in guild.text_channels]:
                helpChan = await guild.create_text_channel(help_chan_name, category=adminCat, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send(f'Created the {helpChan.mention} only visible to admins')

            for public_chan_name in public_chan_list:
                if public_chan_name not in [j.name for j in guild.text_channels]:
                    public_chan = await guild.create_text_channel(public_chan_name)
                    await botChan.send(f'Created the {public_chan.mention} visible to all')

            if "team channels" not in [j.name for j in guild.categories]:
                await guild.create_category("team channels", overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send("Created the Team Channels Category only visible to admins")

    if secretMessage:
        await message.delete(delay=None)


@client.event
async def on_reaction_add(reaction, user):
    print("hello!")


client.run(token)