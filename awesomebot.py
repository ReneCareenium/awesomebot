import os
import ast
import time
from datetime import datetime, timedelta
import asyncio

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$', help_command=None)

# People with admin rights :O
# Later we might replace this with checking for a role.
admins=[ 756220448118669463, # Young Sun
         732403731810877450, # Yeonwoo
         145294584077877249, # Mrchance
         873592977497395301, # Harleqin
         477895596141707264  # René
        ]

white_stone= "<:white_stone:882731089548939314>"
black_stone= "<:black_stone:882730888453046342>"

with open("data/token.txt") as f:
    token = f.readlines()[0] # Get your own token and put it in data/token.txt

format="%Y_%m_%d_%H_%M_%S_%f"

@bot.command()
async def help(ctx):
    helptext='$help : shows this help\n\n'+

            '$join <OGS username> <OGS rank>: join the next tournament\n'+
            '$abandon: abandon the current tournament. :(\n'+
            '$skip: skips the round next week. If you don\'t plan to participate a week skip it to prevent losing points! \n'+
            '$unskip: undoes the previous command \n\n'+

            '$result <B/W/Annuled> <OGS game link>: reports the winner of the game. Please use this command in the assigned thread for your game! You have until Monday at 00.00 UTC to do so, or the administrators will decide the outcome.\n'+

    admintext='\n'+
            '$round: lists the games played this round and their results.\n'+
            '$assign <game number> <B/W/Annuled>: assigns the point of the game numbered <game number> in $round.\n'+
            '$standings: enumerates the standings and pairings for the next round.\n'+
            '$redopairings [(<number,number>)]: overwrite the pairings. Format is for example `$redopairings (1,2),(4,5),(6,7)`. Observe the lack of spaces! \n'+
            '$start: confirms the start of the tournament or the next round. You can only do this in Monday, and with all games resolved!'

    if ctx.author.id in admins: ctx.send(helptext+admintext)
    else : ctx.send(helptext)

    # ctx has guild, message, author, send, and channel (?)

# FILES
# players.csv contains the info of the players:
# discord servername <escaped>, discord user id, ogs user, ogs rank, skip "yes/no", abandon "yes/no"

# pairings <round>

@bot.command()
async def join(ctx, arg1, arg2): #put the player in players.csv: discord servername <escaped please>, discord user id, ogs user, ogs rank, skip round "yes/no", abandoned "yes/no"
    TODO

@bot.command()
async def abandon(ctx): #Doesn't remove the player from players.csv. Sets up a flag. But this one is irreversible
    TODO

@bot.command()
async def result(ctx, arg1, arg2): #Adds to round<number>.csv the outcome of the game
    TODO

@bot.command()
async def skip(ctx): #just write in players.csv that you plan to skip the next round. The flag gets overwritten next Monday.
    TODO

@bot.command()
async def unskip(ctx):
    TODO



#@bot.command()
#async def play(ctx, arg):
#    channel_id= ctx.channel.id
#    user = ctx.author
#    guild= ctx.guild
#
#    # lowest effort serialization
#    with open("state.txt") as f: state = ast.literal_eval(f.read())
#
#    filter_state= [i for i in range(len(state))  if state[i][0] == channel_id]
#    if not filter_state:
#        await ctx.send("No active game in this channel!")
#        return
#
#    i= filter_state[0]
#
#    if state[i][1] == "queue" and user.id not in state[i][4][0]+state[i][4][1]:
#        await ctx.send("Player hasn't joined yet! Join us with `$join`")
#        return
#
#    if state[i][1] == "queue" and (len(state[i][4][0])<min_players or len(state[i][4][1]) <min_players):
#
#        await ctx.send("Waiting for more players to join! Minimum {} per team".format(min_players))
#        return
#
#    colour= sgfengine.next_colour(str(channel_id))
#
#    if state[i][1] == "queue" and user.id!= state[i][4][colour][0]:
#        await ctx.send("It is not your turn yet!")
#        return
#
#    if state[i][1] == "random":
#        assert( len(state[i][2]) == len(state[i][3]))
#
#        if len(state[i][2])>0 and state[i][2][-1] == user.id:
#            await ctx.send("No two consecutive moves by the same player!")
#            return
#
#        for j in range(len(state[i][2])):
#            if (state[i][2][j] == user.id and
#                datetime.now() - datetime.strptime(state[i][3][j],format) < min_time_player):
#                await ctx.send("At most one move per player per day!")
#                return
#
#
#    if state[i][3] != [] and datetime.now()-datetime.strptime(state[i][3][-1],format)<timedelta(seconds=4):
#        return #silent error
#
#    legal_moves=[chr(col+ord('A')-1)+str(row) for col in range(1,21) if col!=9 for row in range(1,20)]
#    legal_moves+=[chr(col+ord('a')-1)+str(row) for col in range(1,21) if col!=9 for row in range(1,20)]
#    if arg not in legal_moves:
#        await ctx.send("I don't understand the move! Please input it in the format `$play Q16`")
#        return
#
#    try:
#        sgfengine.play_move(str(channel_id), arg, user.display_name)
#    except ValueError as e:
#        await ctx.send(str(e))
#        return
#
#    # move registered, let's do the other things
#    state[i][2].append(user.id)
#    state[i][3].append(datetime.now().strftime(format))
#
#    if state[i][1] == "queue":
#        state[i][4][colour].pop(0)
#        state[i][4][colour].append(user.id)
#
#    file = discord.File(str(ctx.channel.id)+".png")
#    if state[i][1]=="queue":
#        next_player=(await guild.fetch_member(state[i][4][1-colour][0]))
#        await ctx.send(file=file, content="{}'s turn! ⭐".format(next_player.mention))
#    else:
#        await ctx.send(file=file)
#
#    with open("state.txt", "w") as f: f.write(repr(state))
#
#@bot.command()
#async def join(ctx):
#    channel_id= ctx.channel.id
#    user = ctx.author
#
#    # lowest effort serialization
#    with open("state.txt") as f: state = ast.literal_eval(f.read())
#
#    filter_state= [i for i in range(len(state))  if state[i][0] == channel_id]
#    if not filter_state:
#        await ctx.send("No active game in this channel!")
#        return
#
#    i= filter_state[0]
#
#    if user.id in (state[i][4][0]+state[i][4][1]):
#        await ctx.send("Player already in this game!")
#        return
#
#    if state[i][1] != "queue":
#        await ctx.send("This game has no queue! No need to join, just `$play` whenever you want :P")
#        return
#
#    colour = 0 if len(state[i][4][0])<=len(state[i][4][1]) else 1
#    state[i][4][colour].append(user.id)
#
#    await ctx.send("User {} joined Team {}!".format(user.display_name, ("Black" if colour==0 else "White")))
#
#    with open("state.txt", "w") as f: f.write(repr(state))
#
#@bot.command()
#async def leave(ctx):
#    channel_id= ctx.channel.id
#    user = ctx.author
#
#    # lowest effort serialization
#    with open("state.txt") as f: state = ast.literal_eval(f.read())
#
#    filter_state= [i for i in range(len(state))  if state[i][0] == channel_id]
#    if not filter_state:
#        await ctx.send("No active game in this channel!")
#        return
#
#    i= filter_state[0]
#
#    if user.id not in (state[i][4][0]+state[i][4][1]):
#        await ctx.send("Player not in this game!")
#        return
#
#    if state[i][1] != "queue":
#        await ctx.send("This game has no queue! No need to leave!")
#        return
#
#    colour = 0 if (user.id in state[i][4][0]) else 1
#    state[i][4][colour].remove(user.id)
#
#    await ctx.send("User {} left :(".format(user.display_name))
#
#    with open("state.txt", "w") as f: f.write(repr(state))
#
#@bot.command()
#async def queue(ctx):
#    channel_id= ctx.channel.id
#    channel= bot.get_channel(channel_id) # thonk the order
#    guild = channel.guild
#
#    # lowest effort serialization
#    with open("state.txt") as f: state = ast.literal_eval(f.read())
#
#    filter_state= [i for i in range(len(state))  if state[i][0] == channel_id]
#    if not filter_state:
#        await ctx.send("No active game in this channel!")
#        return
#
#    i= filter_state[0]
#    colour= sgfengine.next_colour(str(channel_id))
#
#    if state[i][1] != "queue":
#        await ctx.send("This game has no queue! No need to join, just `$play` whenever you want :P")
#        return
#
#    output= "Player list:\n"
#    if state[i][4][0]==[] and state[i][4][1] == []:
#        output+="Nobody yet! Join us with `$join`"
#        await ctx.send(output)
#        return
#
#    if state[i][4][0] == []:
#        for j, player_id in enumerate(state[i][4][1]):
#            player_name=(await guild.fetch_member(player_id)).display_name
#            output+=white_stone+str(j+1).rjust(3)+". "+ player_name+"\n"
#        output+="\n Team Black needs more members!"
#        await ctx.send(output)
#        return
#
#    if state[i][4][1] == []:
#        for j, player_id in enumerate(state[i][4][0]):
#            player_name=(await guild.fetch_member(player_id)).display_name
#            output+=black_stone+str(j+1).rjust(3)+". "+ player_name+"\n"
#        output+="\n Team White needs more members!"
#        await ctx.send(output)
#        return
#
#    # Which team has more members? Or in case of a tie, which team goes first?
#    if len(state[i][4][colour]) > len(state[i][4][1-colour]):
#        last_player = state[i][4][colour][-1]
#    else: last_player= state[i][4][1-colour][-1]
#
#    j=1
#    pointers=[0,0]
#    while(True):
#        #print(channel_id, j, pointers, colour, state[i][0], state[i][4])
#        output+= white_stone if ((colour+1) % 2 ==0)  else black_stone
#        output+= str(j).rjust(3)+". "
#
#        player_name= (await guild.fetch_member(state[i][4][colour][pointers[colour]])).display_name
#        output+= player_name+"\n"
#
#        if state[i][4][colour][pointers[colour]] == last_player: break
#
#        pointers[colour] = (pointers[colour]+1) % len(state[i][4][colour])
#        colour=1-colour
#
#        j+=1
#
#    if len(state[i][4][0])<min_players:
#        output+="\n Team Black needs more members!"
#
#    if len(state[i][4][1])<min_players:
#        output+="\n Team White needs more members!"
#
#    await ctx.send(output)
#
#async def background_task():
#    # When it's monday, announce in the admin channel the standings, pairings for the next round and wait for approval.
#    # When it's Friday, ping unplayed games for a result.
#
#    await bot.wait_until_ready()
#    print("bot ready!")
#
#    guild=discord.utils.get(bot.guilds, name="Awesome Baduk")
#    game=discord.Game("multiplayer Baduk! $help for command list")
#    await bot.change_presence(status=discord.Status.online, activity=game)
#
#    while not bot.is_closed():
#        try:
#            # lowest effort serialization
#            with open("state.txt") as f: state = ast.literal_eval(f.read())
#            #print(state)
#
#            #TODO find who has to move, skip players accordingly, notify if any has to move
#            for i in range(len(state)):
#                if state[i][3] == [] or state[i][1]!="queue": continue
#
#                channel_id= state[i][0]
#                channel= bot.get_channel(channel_id)
#
#                colour = sgfengine.next_colour(str(channel_id))
#
#                last_time= datetime.strptime(state[i][3][-1],format)
#                time_left= last_time + time_to_skip-datetime.now()
#
#                if time_left < time_to_skip/3.0 and time_left > time_to_skip/3.0-timedelta(seconds=10): # Probably remove? Depends on how passive aggressive it is
#                    next_user = await guild.fetch_member(state[i][4][colour][0])
#                    await channel.send("{}'s turn! Time is running up!".format(next_user.mention))#, time_left.total_seconds()/3600) )
#                if time_left < timedelta():
#                    state[i][3][-1]= datetime.strftime(datetime.now(),format)
#                    state[i][2][-1]= None
#                    user_id= state[i][4][colour][0]
#                    state[i][4][colour].pop(0)
#                    state[i][4][colour].append(user_id)
#                    next_player=(await guild.fetch_member(state[i][4][colour][0]))
#                    await channel.send(content="{}'s turn! ⭐".format(next_player.mention))
#
#            with open("state.txt", "w") as f: f.write(repr(state))
#            await asyncio.sleep(10)
#
#        except ConnectionResetError:
#            print("Connection error")

bot.loop.create_task(background_task())
bot.run(token)
