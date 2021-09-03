import discord
from logging.config import fileConfig
import json
import logging
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

public_commands = {
    '!commands': 'prints this list that you\'re already viewing',
    '!addMember': '`!addMember <USERNAME>` only works in your team channel.  Needs to match exactly the name of the user or you might get someone else!',
    '!help': '`!help <message>` this sends a message to GameControl saying you would like some help on what you\'re stuck on',
}

admin_commands = {
    '!ping': 'prints back `pong` so you know I\'m alive',
    '!createTeam': '`!createTeam <TEAMNAME>` creates the text & voice for the team.  If the team name has spaces in it, it will substitute it with -.  ',
    '!assignTeam': '`!assignTeam <team name> <mention user or user name>` this will add a person to the team listed.',
    '!setupServer': 'this command posted in #general will generate the structure for the server',
    '!resetServer': f'this command posted in #{bot_chan_name} will delete everything from the server except the channels it will keep',
}

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
    if len(temp) > 0:
        bot_chan = temp[0]
    else:
        bot_chan = None
    mod_check = isMod(message.author)
    mod_role = [s for s in guild.roles if mod_role_name == s.name][0]
    message_array = message.content.strip().split(' ')

    if message_array[0] == '!ping':
        # pdb.set_trace()
        # await message.channel.send(f'Hello {message.author}!')
        await message.reply(f':ping_pong: hey {message.author.mention}! your channel info is {message.channel.mention}')

    # help them out and show them the commands
    elif message_array[0] == '!commands':
        temp_msg = ""
        for key in public_commands:
            temp_msg += f'\n{key}: {public_commands[key]}'
        await message.channel.send(f'Here\'s a list of the commands you can run{temp_msg}')
        if mod_check:
            temp_msg = ""
            for key in admin_commands:
                temp_msg += f'\n{key}: {admin_commands[key]}'
            await message.channel.send(f'===========\nSecret Mod-only Commands\n==========={temp_msg}')
            
    # for resetting the server after i screwed it up
    elif message_array[0] == '!resetServer':
        if (message.channel.name != bot_chan_name):
            logging.warning(f'!resetServer called in {message.channel.name}')
            await bot_chan.send(f'!resetServer called in {message.channel.mention}')
            return
        if (not mod_check):
            logging.warning(f'!resetServer called by {message.author.name}, who is not a mod')
            await bot_chan.send(f'!resetServer called by {message.author.mention}, who is not a mod')
            return
        logging.warning('RESETTING SERVER')
        await bot_chan.send('```#################RESETTING THE SERVER#################```')
        await message.channel.send('okay time to reset this server!')
        # pdb.set_trace()
        for chanId in guild.channels:
            if chanId.name in keep_chan_list:
                logging.info(f'KEEPING {chanId}')
                await bot_chan.send(f'KEEPING {chanId}')
                continue
            logging.warning(f'DELETING {chanId}')
            await chanId.delete()
        logging.warning('SERVER HAS BEEN RESET')
        await bot_chan.send(f'DELETING {chanId}')
    # elif message_array[0] == '!channel':
    #     await message.channel.send(f'hey {message.author.name}! your channel info is {message.channel.mention}')
    # elif message_array[0] == '!test':
    #     await message.channel.send(f'hey {message.channel.mention}! you thought this was a test?! Good news, there\'s a curve!')

    # when participants need help!
    elif message_array[0] == '!help':
        input_count = 2
        if len(message_array) < input_count:
            logging.warning('User missing description for !help')
            await bot_chan.send('User missing description for !help')
            await message.reply('Please include some helpful description after the `!help` else GameControl doesn\'t know what to help you with')
            return
        # get the help channel
        help_chan = [s for s in guild.channels if help_chan_name == s.name][0]
        # send message
        # can potentially make this an embed to appear fancier
        help_msg = f'{message.author.mention} of team {message.channel.mention} requested \n> {message.content} \n{message.jump_url}'
        logging.info(help_msg)
        await bot_chan.send(help_msg)
        await help_chan.send(help_msg)
        # send a reply to let the user know that we're getting help for them
        await message.reply(f'I\'ve notified GameControl that you could use some help, {message.author.name} \nIf someone from GameControl is available, they\'ll be on their way here soon!')

    # TODO
    # adding new people to a team
    elif message_array[0] == '!assignTeam':
        if (not mod_check):
            logging.warning(f'!assignTeam called by {message.author.name}, who is not a mod')
            await bot_chan.send(f'!assignTeam called by {message.author.mention}, who is not a mod')
            return
        input_count = 3
        # if (message.channel.name != bot_chan_name):
        #     return
        # discord names can contain spaces
        if len(message_array) < input_count:
            logging.warning('Missing arguments for !assignTeam')
            await bot_chan.send('Missing arguments for !assignTeam')
            await message.reply('Invalid formatting. Please follow `!assignTeam <team name> <mention user>`')
            return
        # find the team channels
        chans = [s for s in guild.channels if message_array[1] == s.name]
        if len(chans) != 2:
            err_msg = f'404: Team "{message_array[1]}" not found'
            logging.warning(err_msg)
            await bot_chan.send(err_msg)
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
                    err_msg = f'No user named found from `{message.content}'
                    logging.warning(err_msg)
                    await bot_chan.send(err_msg)
                    return

            for chan in chans:
                add_msg = f'Added {add_user} to {chan.mention}'
                logging.info(add_msg)
                await bot_chan.send(add_msg)
                await chan.edit(overwrites={add_user: discord.PermissionOverwrite(read_messages=True, send_messages=True)})

    # Creates new teams
    elif message_array[0] == '!createTeam':
        if (not mod_check):
            logging.warning(f'!createTeam called by {message.author.name}, who is not a mod')
            await bot_chan.send(f'!createTeam called by {message.author.mention}, who is not a mod')
            return
        if (message.channel.name != bot_chan_name):
            logging.warning(f'!createTeam called outside of {bot_chan}')
            await bot_chan.send(f'!createTeam called outside of {bot_chan}')
            return
        input_count = 2
        if len(message_array) < input_count:
            logging.warning('!createTeam called with incorrect parameters')
            await bot_chan.send('!createTeam called with incorrect parameters')
            await message.reply(f'This command needs {input_count} parameters')
            return
        newChanName = ' '.join(message_array[1:])
        # pdb.set_trace()
        if newChanName in [j.name for j in guild.channels]:
            logging.warning(f'!createTeam called for existing team "{newChanName}"')
            await bot_chan.send(f'!createTeam called for existing team "{newChanName}"')
            await message.reply(f'Sorry, {newChanName} already exists')
            return
        # doesn't exist so let's create it
        mod_role = [s for s in guild.roles if mod_role_name == s.name][0]
        teamCat = [s for s in guild.categories if "team channels" == s.name][0]
        add_msg = f'Created new text channel {newChanName}'
        logging.info(add_msg)
        await bot_chan.send(add_msg)
        newChan = await guild.create_text_channel(newChanName, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                mod_role: discord.PermissionOverwrite(read_messages=True),
                message.author: discord.PermissionOverwrite(read_messages=True)
                },
            category=teamCat)
        await message.reply(f'Created new text channel {newChan.mention}')
        logging.info(add_msg)
        await bot_chan.send(add_msg)
        newChan = await guild.create_voice_channel(newChanName, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                mod_role: discord.PermissionOverwrite(read_messages=True),
                message.author: discord.PermissionOverwrite(read_messages=True)
                },
            category=teamCat)
        await message.reply(f'Created new voice channel {newChan.mention}')

    elif message_array[0] == '!author':
        await message.reply(f'hey {message.author.mention}! Your discord id is {message.author}')

    elif 'rickroll' in message.content:
        logging.info(f'{message.author} got rick rolled lmao')
        await bot_chan.send(f'{message.author} got rick rolled lmao')
        await message.channel.send('Here ya go! <https://www.youtube.com/watch?v=xn38dg0YrzY>')

    elif message_array[0] == "!setupServer":
        if (not mod_check):
            logging.warning(f'!resetServer called by {message.author.name}, who is not a mod')
            return
        if (message.channel.name == "general"):
            logging.warning('SETTING UP SERVER')
            secretMessage = True
            logging.warning(f"channel list: {[j.name for j in guild.channels]}")

            mod_role

            if "admin stuff" not in [j.name for j in guild.categories]:
                logging.info('CREATING ADMIN CATEGORY')
                adminCat = await guild.create_category("admin stuff", overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await message.channel.send("Created the admin stuff Category only visible to admins")
            else:
                logging.info('ADMIN CATEGORY ALREADY EXISTS')
                adminCat = [s for s in guild.categories if "admin stuff" == s.name][0]

            botChan = [s for s in guild.text_channels if bot_chan_name == s.name]
            botChanFound = False
            # no botcommands text channel found
            if (botChan != []):
                botChan = botChan[0]
                botChanFound = True
                # it's in the wrong category
                if (botChan.category != adminCat):
                    logging.info('MOVING BOT STUFF TO ADMIN CATEGORY')
                    await botChan.edit(category=adminCat)
                    logging.info('CHANGING BOT STUFF TO PRIVATE')
                    await botChan.send(f'made {botChan.mention} private')

            if (not botChanFound):
                logging.info('CREATING ADMIN CHANNEL: BOT STUFF CHANNEL')
                botChan = await guild.create_text_channel(bot_chan_name, category=adminCat)
                await botChan.set_permissions(guild.default_role, read_messages=False)
                await botChan.set_permissions(guild.me, read_messages=True, send_messages=True)
                await botChan.send(f'created {botChan.mention} and made private')

            if announce_chan_name not in [j.name for j in guild.text_channels]:
                logging.info('CREATING ANNOUNCEMENTS CHANNEL')
                anno = await guild.create_text_channel(announce_chan_name, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                })
                await botChan.send(f'Created the {anno.mention} only typable to admins')

            for admin_chan_name in admin_chan_list:
                logging.info('CREATING ADMIN CHANNEL: ADMIN CHANNEL')
                if admin_chan_name not in [j.name for j in guild.text_channels]:
                    admin_chan = await guild.create_text_channel(admin_chan_name, category=adminCat, overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await botChan.send(f'Created the {admin_chan.mention} only visible to admins')

            if "recent-answers" not in [j.name for j in guild.text_channels]:
                logging.info('CREATING ADMIN CHANNEL: RECENT ANSWERS CHANNEL')
                recentChan = await guild.create_text_channel("recent-answers", category=adminCat, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send(f'Created the {recentChan.mention} only visible to admins')

            if help_chan_name not in [j.name for j in guild.text_channels]:
                logging.info('CREATING PUBLIC CHANNEL: HELP REQUEST CHANNEL')
                helpChan = await guild.create_text_channel(help_chan_name, category=adminCat, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send(f'Created the {helpChan.mention} only visible to admins')

            for public_chan_name in public_chan_list:
                if public_chan_name not in [j.name for j in guild.text_channels]:
                    logging.info(f'CREATING PUBLIC CHANNEL: {public_chan_name}')
                    public_chan = await guild.create_text_channel(public_chan_name)
                    await botChan.send(f'Created the {public_chan.mention} visible to all')

            if "team channels" not in [j.name for j in guild.categories]:
                logging.info('CREATING TEAM CATEGORY')
                await guild.create_category("team channels", overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send("Created the Team Channels Category only visible to admins")

    if secretMessage:
        logging.info('secret message triggered, will delete the message')
        await message.delete(delay=None)


@client.event
async def on_reaction_add(reaction, user):
    print("hello!")


client.run(token)