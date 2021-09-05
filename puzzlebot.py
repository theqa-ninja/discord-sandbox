import discord
import discord_emoji
from logging.config import fileConfig
import json
import logging
import os
import hashlib
from discord.ext import commands

fileConfig('logging.ini')


def isMod(author_member):
    author_roles = author_member.roles
    if len([s for s in author_roles if mod_role_name == s.name]) > 0:
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
    team_category_name = config['team_category']
    admin_chan_list = config['admin_channels'].split(',')
    public_chan_list = config['public_channels'].split(',')
    mod_role_name = config['mod_role']
    user_role_name = config['user_role']
    ToS_chan_name = config['ToS_channel']
    ToS_accept_emj = config['ToS_acceptance_emoji']
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
bot_intents.reactions = True
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
    message_array = message.content.strip().split(' ')

    if message_array[0] == '!ping':
        # pdb.set_trace()
        # await message.channel.send(f'Hello {message.author}!')
        await message.reply(f':ping_pong: hey {message.author.mention}! your channel info is {message.channel.mention}')

    # sets up the emoji that will be used for accepting ToS
    # useful for the bot being in multiple servers
    # elif message_array[0] == '!setTOSemoji':
    #     if (not mod_check):
    #         logging.warning(f'!setTOSemoji called by {message.author.name}, who is not a mod')
    #         return
    #     if (len(message_array) != 2):
    #         logging.warning(f'!setTOSemoji called by {message.author.name} in {message.channel.name} with bad parameters')
    #         return
    #     elif (message.channel.name == "general"):
    #         logging.warning('Setting up react emoji')
    #         secretMessage = True
    #         # saving the emoji from the array into config.json
    #         emj = message_array[1]
    #         logging.warning(f'Writing emoji {emj} into config.json')
    #         # file i/o to set "ToS_acceptance_emoji" = emj
    #         with open('config.json', 'r') as f:
    #             config = json.load(f)
    #             config['ToS_acceptance_emoji'] = f'{emj}'
    #         os.remove('config.json')
    #         with open('config.json', 'w') as f:
    #             json.dump(config, f, indent=2)

    # help them out and show them the commands
    elif message_array[0] == '!commands':
        # green
        green = 65280
        red = 16711680
        embedVar = discord.Embed(title="Bot Commands", color=green)
        for key in public_commands:
            embedVar.add_field(name=key, value=public_commands[key], inline=False)
        await message.channel.send(embed=embedVar)
        # only sends secret commands if mod AND in admin only channel
        if mod_check and message.channel.name in admin_chan_list:
            embedVar = discord.Embed(title='===========\nSecret Mod-only Commands\n===========', color=red)
            for key in admin_commands:
                embedVar.add_field(name=key, value=admin_commands[key], inline=False)
            await message.channel.send(embed=embedVar)

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
        # file i/o for: config['ToS_acceptance_emoji'] = ""
        # with open('config.json', 'r') as f:
        #     config = json.load(f)
        #     config['ToS_acceptance_emoji'] = ""
        # os.remove('config.json')
        # with open('config.json', 'w') as f:
        #     json.dump(config, f, indent=2)
        # back to logging
        logging.warning('SERVER HAS BEEN RESET')
        await bot_chan.send('Server has been reset.')
    # elif message_array[0] == '!channel':
    #     await message.channel.send(f'hey {message.author.name}! your channel info is {message.channel.mention}')
    # elif message_array[0] == '!test':
    #     await message.channel.send(f'hey {message.channel.mention}! you thought this was a test?! Good news, there\'s a curve!')

    # when participants need help!
    elif message_array[0] == '!help':
        input_count = 2
        if len(message_array) < input_count:
            logging.warning(f'{message.author.name} missing description for !help')
            await bot_chan.send(f'{message.author.mention} missing description for !help')
            await message.reply('Please include a helpful description after `!help`, or GameControl won\'t know how to help!')
            return
        # ensures the !help request comes from a team channel
        if message.channel.category.name != team_category_name:
            logging.warning(f'{message.author.name} called for !help outside of their team channel, in {message.channel.name}')
            await bot_chan.send(f'{message.author.mention} called for !help outside of their team channel, in {message.channel.mention}')
            await message.reply('Please use the command again inside your team\'s channel.')
            return
        # get the help channel
        help_chan = [s for s in guild.channels if help_chan_name == s.name][0]
        # help description without '!help'
        help_desc = f'{message.content}'[6:]
        # send message
        logging.info(f'{message.author.mention} of team {message.channel.mention} requested help:\n{message.jump_url}\nDescription: {help_desc}')
        await bot_chan.send(f'{message.author.mention} of team {message.channel.mention} requested help:\n<{message.jump_url}>')
        await bot_chan.send(f'> {help_desc}')
        # sending an embed in the help channel to make help requests more readable
        hash = hashlib.md5(message.channel.name.encode()).hexdigest()[-6:]
        color = int(f'0x{hash}', 0)
        embedVar = discord.Embed(title="Help Requested:", color=color)
        embedVar.add_field(name='Name', value=f'{message.author.mention}', inline=False)
        embedVar.add_field(name='Team', value=f'{message.channel.mention}', inline=False)
        # the help description is now hyperlinked
        embedVar.add_field(name='Description', value=f'[{help_desc}]({message.jump_url})', inline=False)
        await help_chan.send(embed=embedVar)
        # send a reply to let the user know that we're getting help for them
        await message.reply(f'I\'ve notified GameControl that you need help, {message.author.mention}.\nIf someone from GameControl is available, they\'ll be on their way here soon!')

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
            topic=f'Private Channel for team {newChanName}.  If you talk about puzzles here, it is easier for GameControl to figure out what you have tried when you ask for help',
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
        logging.info(f'{message.author.name} got rick rolled lmao')
        await bot_chan.send(f'{message.author.mention} got rick rolled lmao')
        await message.channel.send('Here ya go! <https://www.youtube.com/watch?v=xn38dg0YrzY>')

    elif message_array[0] == "!setupServer":
        # doing a role check

        temp = [s for s in guild.roles if user_role_name == s.name]
        user_role = temp[0] if (len(temp) > 0) else await guild.create_role(name=user_role_name)

        temp = [s for s in guild.roles if mod_role_name == s.name]
        mod_role = temp[0] if (len(temp) > 0) else await guild.create_role(name=mod_role_name)

        # The server has no other roles other than default, user, admin, and the role for this bot.
        # So make this user a mod.
        if len(guild.roles) < 4:
            message.author.add_roles(mod_role)

        if (not mod_check):
            logging.warning(f'!setupServer called by {message.author.name}, who is not a mod')
            return
        if (message.channel.name == "general"):
            logging.warning('setting up server')
            secretMessage = True
            logging.warning(f"channel list: {[j.name for j in guild.channels]}")

            # mod_role = [s for s in guild.roles if mod_role_name == s.name][0]
            if "admin stuff" not in [j.name for j in guild.categories]:
                logging.info('creating admin category')
                adminCat = await guild.create_category("admin stuff", overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    user_role: discord.PermissionOverwrite(read_messages=False),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await message.channel.send("Created the admin stuff Category only visible to admins")
            else:
                logging.info('admin category already exists')
                adminCat = [s for s in guild.categories if "admin stuff" == s.name][0]

            botChan = [s for s in guild.text_channels if bot_chan_name == s.name]
            botChanFound = False
            # no botcommands text channel found
            if (botChan != []):
                botChan = botChan[0]
                botChanFound = True
                # it's in the wrong category
                if (botChan.category != adminCat):
                    logging.info('moving bot stuff to admin category')
                    await botChan.edit(category=adminCat)
                    logging.info('changing bot stuff to private')
                    await botChan.send(f'made {botChan.mention} private')

            if (not botChanFound):
                logging.info('CREATING ADMIN CHANNEL: BOT STUFF CHANNEL')
                botChan = await guild.create_text_channel(bot_chan_name, category=adminCat)
                await botChan.set_permissions(guild.default_role, read_messages=False)
                await botChan.set_permissions(guild.me, read_messages=True, send_messages=True)
                await botChan.send(f'created {botChan.mention} and made private')

            # add_reactions must be false; it prevents users from adding new reactions in the ToS channel.
            # it still allows users to react with the existing reaction.
            if ToS_chan_name not in [j.name for j in guild.text_channels]:
                logging.info(f'creating {ToS_chan_name} channel')
                tos = await guild.create_text_channel(ToS_chan_name, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, add_reactions=False),
                    user_role: discord.PermissionOverwrite(read_messages=False),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                })
                await botChan.send(f'Created the {tos.mention} only typable to admins')

            if "public area" not in [j.name for j in guild.categories]:
                logging.info('creating public area')
                publicCat = await guild.create_category("public area", overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    user_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                })
                await message.channel.send("Created the public area Category visible to everyone")
            else:
                logging.info('public area Category already exists')
                publicCat = [s for s in guild.categories if "public area" == s.name][0]

            if (message.channel.category != publicCat):
                logging.info('moving bot stuff to public area category')
                await message.channel.edit(category=publicCat)

            if announce_chan_name not in [j.name for j in guild.text_channels]:
                logging.info('created #announcements')
                anno = await guild.create_text_channel(announce_chan_name, category=publicCat, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    user_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                    mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                })
                await botChan.send(f'Created the {anno.mention} only typable to admins')

            for admin_chan_name in admin_chan_list:
                logging.info(f'creating admin channel: {admin_chan_name}')
                if admin_chan_name not in [j.name for j in guild.text_channels]:
                    admin_chan = await guild.create_text_channel(admin_chan_name, category=adminCat, overwrites={
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await botChan.send(f'Created the {admin_chan.mention} only visible to admins')

            if "recent-answers" not in [j.name for j in guild.text_channels]:
                logging.info('creating admin channel: recent answers channel')
                recentChan = await guild.create_text_channel("recent-answers", category=adminCat, overwrites={
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send(f'Created the {recentChan.mention} only visible to admins')

            if help_chan_name not in [j.name for j in guild.text_channels]:
                logging.info('creating public channel: help request channel')
                helpChan = await guild.create_text_channel(help_chan_name, category=adminCat, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send(f'Created the {helpChan.mention} only visible to admins')

            for public_chan_name in public_chan_list:
                if public_chan_name not in [j.name for j in guild.text_channels]:
                    logging.info(f'creating public channel: {public_chan_name}')
                    public_chan = await guild.create_text_channel(public_chan_name, category=publicCat, overwrites={
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    })
                    await botChan.send(f'Created the {public_chan.mention} visible to all')

            if team_category_name not in [j.name for j in guild.categories]:
                logging.info('creating team category')
                await guild.create_category(team_category_name, overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                })
                await botChan.send("Created the Team Channels Category only visible to admins")

    if secretMessage:
        logging.info('secret message triggered, will delete the message')
        await message.delete(delay=None)


@client.event
async def on_raw_reaction_add(payload):
    # don't want the bot to act on it's react
    if payload.member.bot:
        return
    # finding the server that the reaction came from
    guild = payload.member.guild
    temp = [s for s in guild.channels if bot_chan_name == s.name]
    if len(temp) > 0:
        bot_chan = temp[0]
    else:
        bot_chan = None
    # finding the channel that the reaction came from
    curr_chan = client.get_channel(payload.channel_id)
    if ToS_chan_name == curr_chan.name:
        # verifying reaction
        emoji_text = discord_emoji.to_discord(payload.emoji.name)
        if (payload.emoji.name == ToS_accept_emj) or (emoji_text == ToS_accept_emj):
            # checking if role exists
            role_list = [s for s in guild.roles if user_role_name == s.name]
            if (len(role_list) > 0):
                role = role_list[0]
                # adding basic user role
                mem = guild.get_member(payload.user_id)
                # check if the member already has the role
                member_roles = [s for s in mem.roles if user_role_name == s.name]
                if (len(member_roles) == 0):
                    logging.info(f'{mem.mention} aka {mem.name} does not have {user_role_name}; adding it now')
                    await bot_chan.send(f'{mem.mention} does not have {user_role_name}; adding it now')
                    # adding the role since the user doesn't have it
                    await mem.add_roles(role)
                    logging.info(f'removing the default role {guild.default_role}; so they don\'t see the #{ToS_chan_name}')
                    await bot_chan.send(f'removing the default role {guild.default_role}; so they don\'t see the {curr_chan.mention}')
                    await mem.remove_roles(guild.default_role)
                logging.info(f'{mem.mention} accepted the ToS.')
                logging.info('Resetting the reactions.')
                await bot_chan.send(f'{mem.mention} accepted the ToS.')
                await bot_chan.send('Resetting the reactions.')
                # retrieving the msg
                msg = await curr_chan.fetch_message(payload.message_id)
                # fetching server emoji
                emj = client.get_emoji(payload.emoji.id)
                # removing reactions to the message
                await msg.clear_reaction(emj)
                # adding back a reaction
                await msg.add_reaction(emj)

client.run(token)