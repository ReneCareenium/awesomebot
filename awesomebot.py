import os
import ast
import time
import requests
import csv
import math
from datetime import datetime, timedelta
import asyncio
import mwmatching
import csv

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$', help_command=None)

# Max 100 players
lower_bar = 10 #20k
upper_bar = 27 #1k

#file_lines=[]

admin_channel_id= 887348367036907640 # tournament-admins
#admin_channel_id= 870604751354613770 # bots-testing

#announcements_channel_id=874000674218733668 # tournament-scheduling
#announcements_channel_id=868837224203034624 # event-announcements
#announcements_channel_id= 870604751354613770 # bots-testing
announcements_channel_id= 887348367036907640 # tournament-admins

awesome_server_id= 767835617002258443
permitted_channel_ids= [874000674218733668, 887348367036907640, 870604751354613770, 874000714848927774]

white_stone= "<:white_stone:882731089548939314>"
black_stone= "<:black_stone:882730888453046342>"

with open("data/token.txt") as f:
    token = f.readlines()[0] # Get your own token and put it in data/token.txt

date_format="%Y_%m_%d_%H_%M_%S_%f"

ogs_game_url= "https://online-go.com/game/"

# Every column from then on has 9 characters with no extra spaces in between. First five are the number right aligned, then the symbol, then /w3. The column entry is either:
# 0+ or 0- for skipped players
# 12?/b3 representing opponent, result (+/-/=) colour and handicap
# Just after the pairings it looks like 12?/b3 or whatever.

@bot.command()
async def help(ctx):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return

    helptext=('$help : shows this help\n\n'+

            '$join <OGS profile url> (<OGS rank>): join the next tournament. The first argument is the url for your OGS profile. The second argument is optional and will overwrite your OGS rank.\n'+
            #'$abandon: abandon the current tournament. :(\n'+
            '$skip: skips the next round. If you don\'t plan to participate in a round skip it to prevent losing points! \n'+
            '$unskip: undoes the previous command \n\n'+
            '$result <OGS game link>: reports the winner of the game. Please use this command in #tournament-game-links! You have until Monday at 00.00 UTC to do so, or the administrators will decide the outcome.\n')

    admintext=('\n'+
            '$outcome <id> <W/L/D/N> <round>: Declares the outcome for the current game for player <id>, win/lose/draw/null. If <round> is specified, it will retroactively apply changes'+
            #'$kick <id>: Kick player <id> from the tournament'+
            '$standings: view the standings table\n'+
            '$pairings: compute and preview pairings. Will inform you of unfinished games beforehand. If this is the first round, it also prepares the files.\n' +
            #'$swap <id1> <id2>: swap the opponents for two players. Only works after $pairings and before $newround!\n'+
            '$newround: announce the next round. Prints standings and pairings in the admin channel\n\n')

    if ctx.channel.id== admin_channel_id: await ctx.send(helptext+admintext)
    else : await ctx.send(helptext)

    # ctx has guild, message, author, send, and channel (?)

# Just take the data and put it in players.csv. This is our number one priority right now.
# Inform the player of their
# FIXME commas and spaces in user names could occur
# Wipe players.csv games.csv and put state.csv to (0,[])
@bot.command()
async def join(ctx, url, rank=None):
    ctx.send("Signups are closed! Contact a tournament administrator and we will see what we can do ;)")
    return
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return

    if url[-1]=="/": player_id= url.split('/')[-2]
    else: player_id= url.split('/')[-1]

    try:
        request_result = requests.get(f'http://online-go.com/api/v1/players/{player_id}').json()

        if rank==None:
            ranking = math.floor(float(request_result["ranking"]))
            if ranking >= 30:
                rank= str(ranking-29) + "d"
            else:
                rank = str(30-ranking) + "k"

        ogsname= request_result["username"]
    except:
        await ctx.send("OGS error! Please try again later")
        return

    # Assumes the existence of an empty tournament file
    valid_ranks= ([str(i) + "k" for i in range(1,31)] +
                  [str(i)+"d" for i in range(1,9)])
                  #[str(i)+"p" for i in range(1,9)])
    valid_ranks= valid_ranks + [s.upper() for s in valid_ranks]

    rank=rank.lower()
    if rank not in valid_ranks:
        await ctx.send("Invalid rank!")
        return

    player= await ctx.guild.fetch_member(ctx.author.id)
    displayname= player.display_name

    with open("data/players.csv") as f:
        file_lines = f.readlines()

    if ctx.author.id in [int(l.split(',')[0]) for l in file_lines if l!="\n" and l!=""]:
        await ctx.send("Player already joined!")
        return

    else:
        file_lines.append(f"{ctx.author.id},{displayname},{player_id},{ogsname},{rank}\n")

    with open ("data/players.csv", "w") as f: f.writelines(file_lines)

    await ctx.send(f"{displayname} ({ogsname}) joined with rank {rank}!")

def ranktonumber(s):
    valid_ranks= {**{str(i)+"k":30-i for i in range(1,31) }, **{str(i)+"d":29+i for i in range(1,9)}}
    return valid_ranks[s]

def ranktoscore(s, u, l):
    return max(min(ranktonumber(s),u), l)

async def skip(ctx):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    player_id= ctx.author.id
    player= await ctx.guild.fetch_member(ctx.author.id)
    displayname= player.display_name

    with open("data/skips.txt") as f: skips=[int(s[:-1]) for s in f.readlines()]

    if player_id in skips:
        await ctx.send(f"Player is already skipping the next round! Undo this with `$unskip`")
        return

    skips+= player_id

    with open("data/skips.txt", "w") as f: f.writelines([str(i)+"\n" for i in skips])

async def unskip(ctx):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    player_id= ctx.author.id
    player= await ctx.guild.fetch_member(ctx.author.id)
    displayname= player.display_name

    with open("data/skips.txt") as f: skips=[int(s[:-1]) for s in f.readlines()]

    if player_id not in skips:
        await ctx.send(f"Player is not skipping the next round! Skip it with `$skip`")
        return

    skips.remove(player_id)

    with open("data/skips.txt", "w") as f: f.writelines([str(i)+"\n" for i in skips])

# Print a .h file for the web app
def make_mrchance_happy():
    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())

    line_format="{:>4} {:20} x           {:>3} AB XXXX {:>4} {:>5} {:>5} 0"
    column_format="{:>5}{}{:3}"
    lines= ["; Pl Name                            Rk Co Club  MMS  SOSSOSOS\n"]

    index= {state[i][0]:i for i in range(len(state))}

    for i in range(len(state)):
        p = state[i]
        lines.append(line_format.format(i+1, p[0], p[1], p[2], p[3], p[4]))
        for opp in p[5]:
            if opp[0]!=0:
                opp_position= index[opp[0]]+1
                lines[-1]+= column_format.format(opp_position,opp[1],opp[2]+str(opp[3]) )
            else:
                lines[-1]+= column_format.format(0, opp[1], "")
        lines[-1]+="\n"

    with open("data/tournament.h1", "w") as f: f.writelines(lines)
    return

# 6, "Mens Rea", "5k", 15, 47, 134, "4+/b0", "OGS link", "5?/w0", ""
async def make_mrchance_happy2(ctx):
    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())

    column_format="{}{}{}"
    lines=[]

    index= {state[i][0]:i for i in range(len(state))}

    with open("data/tournament.csv", "w") as f:
        writer= csv.writer(f)

        for i in range(len(state)):
            p = state[i]
            name= await ctx.guild.fetch_member(p[0])
            name= name.display_name

            #lines.append(f"{i+1},{name},{p[1]},{p[2]},{p[3]},{p[4]}")
            fields= [i+1,name, p[1],p[2],p[3],p[4]]

            for opp in p[5]:
                if opp[0]!=0:
                    opp_position= index[opp[0]]+1
                    fields.append(column_format.format(opp_position,opp[1],opp[2]+str(opp[3]) ))
                    if opp[4]!="":
                        fields.append(ogs_game_url+opp[4])
                    else: fields.append("")
                else:
                    fields.append(column_format.format(0, opp[1], ""))
                    fields.append("")
            writer.writerow(fields)

    return

def pretty_print(state):

    line_format="{:>2} {:20}{:>3}{:>4}{:>5}{:>5}"
    column_format=" {:>2}{}{:2}"
    lines= ["   Name                 Rk MMS  SOS SOSOS\n"]

    index= {state[i][0]:i for i in range(len(state))}
    with open("data/players.csv") as f: player_lines=[l[:-1].split(",") for l in f.readlines()]

    for i in range(len(state)):
        p = state[i]
        name = next(l[1] for l in player_lines if int(l[0])==p[0])

        #name= await ctx.guild.fetch_member(p[0])
        #name= name.display_name

        lines.append(line_format.format(i+1, name, p[1], p[2], p[3], p[4]))
        for opp in p[5]:
            if opp[0]!=0:
                opp_position= index[opp[0]]+1
                lines[-1]+= column_format.format(opp_position,opp[1],opp[2]+str(opp[3]) )
            else:
                lines[-1]+= column_format.format(0, opp[1], "")
        lines[-1]+="\n"

    return "```"+"".join(lines)+"```"

@bot.command()
async def pairings(ctx):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    if ctx.channel.id != admin_channel_id: return

    file_lines=[]

    # The tournament state, state.txt is encoded as a tuple with a round counter and a list of:
    # player id, rank, score, sos, sosos, opponents.
    #
    # And opponents is in turn a list of: opponent id, result, color, handicap, ogs_game_id.
    # This file is lazily serialized with ast.literal_eval

    # 1. Check if the tournament hasn't begun. Then create a state.txt file
    # with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())
    # with open("data/state.txt", "w") as f: f.write(repr((r,state)))

    if not os.path.isfile("data/state.txt"):

        with open("data/players.csv") as f: player_lines=[l[:-1].split(",") for l in f.readlines()]

        #print(sorted(player_lines, key=lambda l: -ranktonumber(l[4])))
        r=0
        state= \
            [[int(player[0]), player[4], ranktoscore(player[4],upper_bar, lower_bar), 0,0,[]]
             for player in sorted(player_lines, key=lambda l: -ranktonumber(l[4]))]

        with open("data/state.txt", "w") as f: f.write(repr((r,state)))

    #return

    # 2. Check for unfinished matches in the last round.
    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())

    if len(state[0][5])==r+1:
        await ctx.send("Some error happened! Players are already paired up!")
        return

    assert(len(state[0][5])==r)

    if r!=0:
        unfinished_games=[(p[0], p[5][r-1][0]) for p in state if p[5][r-1][2]=="b" and p[5][r-1][1]=="?" and p[5][r-1][0]>0]

        unfinished_games_text=""
        for (pid1, pid2) in unfinished_games:
            p1= await ctx.guild.fetch_member(int(pid1))
            p2= await ctx.guild.fetch_member(int(pid2))
            unfinished_games_text+=f"{p1.display_name} vs {p2.display_name}\n"

        if unfinished_games:
            await ctx.send("Pairings are impossible! The following matches are not over yet!\n\n" + unfinished_games_text)
            return

    # 2.5 Compute MMS, SOS, SOSOS
    for i in range(len(state)):
        state[i][2]= ranktoscore(state[i][1], upper_bar,lower_bar) + len([g for g in state[i][5] if g[1]=="+"])
    for i in range(len(state)):
        state[i][3]= sum( next((p[2] for p in state if p[0]==game[0]), 0) for game in state[i][5])
    for i in range(len(state)):
        state[i][4]= sum( next((p[3] for p in state if p[0]==game[0]), 0) for game in state[i][5])

    # Lexicographic sort
    state= sorted(state, key=lambda p: p[4], reverse=True)
    state= sorted(state, key=lambda p: p[3], reverse=True)
    state= sorted(state, key=lambda p: p[2], reverse=True)

    # 3. Prepare the weights for the blossom algorithm. In descending priority:
    #    - no repeated matches or bye
    #    - bye only people in the lower half of the standings.
    #    - minimize the number of n-stone handicap games.
    #    - prioritize handicap games between people close in the rank list.
    #    - prioritize even games between people far in the rank list

    pairs=[]
    index= {state[i][0]:i for i in range(len(state))}

    with open("data/skips.txt") as f: skips=[int(s[:-1]) for s in f.readlines()]

    # These players will get a chance of being paired with 0
    if (len(state) - len(skips))%2 !=0:
        for p in state[(len(state)//2):]:
            if p[0] in skips: continue
            if not any(game[0]==0 and game[1]=="+" for game in p[5]):
                pairs.append((index[p[0]]+1, 0, 0))

    # These are the normal matches.
    for i in range(len(state)):
        for j in range(i+1,len(state)):
            p1= state[i]; p2=state[j]
            if (p1[0] in skips) or (p2[0] in skips): continue
            if any(game[0]==p2[0] for game in p1[5]): continue

            #if p1[2]==p2[2]: weight= 100**100+(i-j)**2 #Thanks, python bignums!
            #else: weight= 100**(100-abs(p1[2]-p2[2])) - 10000*(i-j)**2
            #if p1[2]==p2[2]: weight= (100**100-1)*10**12 + (i-j)**2
            #else: weight= (100**100-100**abs(p1[2]-p2[2]))*10**12 - 10**6*(i-j)**2
            if p1[2]==p2[2]: weight= (100**100-1)*10**12 -(100-abs(i-j))**2
            else: weight= (100**100-100**abs(p1[2]-p2[2]))*10**12 + 10**6*(i-j)**2
            pairs.append((index[p1[0]]+1, index[p2[0]]+1, weight))

    # call the blossom algorithm to compute a maximum matching.
    mates= mwmatching.maxWeightMatching(pairs, maxcardinality=True)

    # 4. Update the state and compute colors for each match
    #    - For handicap games assign the color normally
    #    - Assign Black to maximize Bernoulli posterior likelihood (more random than random!)
    #    - Turns out this means give Black to the player maximizing (W+1)/(B+1)

    for i in range(1,len(mates)):
        #if mates[i]==0:
        #    if i in skips: state[i-1][5].append([0, "-", "", 0, ""])
        #    else: state[i-1][5].append([0,"+","",0,""])
        if mates[i]==0:
            state[i-1][5].append([0,"+","",0,""])
        elif mates[i]==-1:
            state[i-1][5].append([0, "-", "", 0, ""])
        else:
            if -1<=state[i-1][2]-state[mates[i]-1][2] <=1:

                b1= len([0 for p in state[i-1][5][:r] if p[2]=="b" and p[0]!=0 and p[3]==0])
                w1= len([0 for p in state[i-1][5][:r] if p[2]=="w" and p[0]!=0 and p[3]==0])
                b2= len([0 for p in state[mates[i]-1][5][:r] if p[2]=="b" and p[0]!=0 and p[3]==0])
                w2= len([0 for p in state[mates[i]-1][5][:r] if p[2]=="w" and p[0]!=0 and p[3]==0])

                if (b1+1)*(w2+1) == (b2+1)*(w1+1): color = "b" if i>mates[i] else "w"
                else: color = "w" if (b1+1)*(w2+1) > (b2+1)*(w1+1) else "b"

                handicap = 0
            else:
                handicap = max (0, abs(state[i-1][2]-state[mates[i]-1][2])-1)
                color = "b" if i > mates[i] else "w"

            state[i-1][5].append( [state[mates[i]-1][0], "?", color, handicap, ""])

    # 5. Make Mrchance happy. Display the standings/pairings in the admin channel
    with open("data/state.txt", "w") as f: f.write(repr((r,state)))

    make_mrchance_happy()

    text= pretty_print(state)
    await ctx.send(text)


@bot.command()
async def newround(ctx):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    if ctx.channel.id != admin_channel_id: return

    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())

    # 1. Check that pairings have been made.
    if r == len(state[0][5]):
        await ctx.send("Parings have not been done yet! Please begin the pairing process with $pairings")
        return

    # 2. Advance the round counter. Delete skips.txt
    r+=1
    with open("data/skips.txt", "w") as f: f.writelines([])

    # 3. Announce current standings and next round pairings in the public channel
    #    Remind users the rules (public game, handicap, colors, time settings, AI)
    with open("data/state.txt", "w") as f: f.write(repr((r,state)))

    channel = bot.get_channel(announcements_channel_id)
    await channel.send("This is the new round! Placeholder text explaining the rules here! This would go in a public channel!")

    text= pretty_print(state)
    await ctx.send(text)

    await make_mrchance_happy2(ctx)
    await ctx.send("Admin-only csv file!", file=discord.File("data/tournament.csv"))

# byes are games of the form 0+, while skips are 0-
@bot.command()
async def result(ctx, url):

    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    # check the current game of this person.
    # identify the opponent's user id and colour
    # assign the point.

    #with open("data/tournament.csv") as f: file_lines= f.readlines()
    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())

    for i in range(len(state)):
        if ctx.author.id == state[i][0]:
            if state[i][5][r-1][1]!="?":
                await ctx.send("You don't have new games to report! Please wait until the next round.")
                return

            colour = state[i][5][r-1][2];
            opponent_id= state[i][5][r-1][0]

            if opponent_id == 0:
                await ctx.send("You don't have an opponent this round!")
                return

            # 1. extract both ogs ids from players.csv
            with open("data/players.csv") as f:
                lines= [l[:-1].split(',') for l in f.readlines()]

                ogs_id1= int(next(l[2] for l in lines if l[0]==str(ctx.author.id)))
                ogs_id2= int(next(l[2] for l in lines if l[0]==str(opponent_id)))

            # 2. extract ogs ids from the api and verify if they are right.
            game_id= url.split('/')[-1]
            try:
                request_result = requests.get(f'http://online-go.com/api/v1/games/{game_id}').json()

                # XXX perhaps check for correct handicap and time settings too?

                if(request_result["outcome"]==""):
                    await ctx.send("This game is not finished! Report it again once it is please!")
                    return

                if(ogs_id1== request_result["white" if colour=='b' else "black"]):
                    await ctx.send("This game was played with the wrong colors. It is okay but please be careful next time!")
                    colour="b" if colour =="w" else "w"

                if (ogs_id1 != request_result["white" if colour=='w' else "black"] or ogs_id2 != request_result["white" if colour=='b' else "black"]):
                    await ctx.send("This game was played with unexpected accounts! Please contact the tournament administrators")
                    return

                black_lost= request_result["black_lost"]
                arg1= "w" if black_lost else "b" # what a mess!
            except:
                await ctx.send("OGS error! Please try again later")
                return

            # 3. set symbol2,symbol2

            if black_lost == (colour=="b") : symbol1="-"; symbol2= "+"
            else:                            symbol1="+"; symbol2="-"

            state[i][5][r-1][1]=symbol1
            opponent_idx= next(i for i in range(len(state)) if state[i][0]==opponent_id)
            state[opponent_idx][5][r-1][1]=symbol2

            ogs_game_id= url.split("/")[-1]
            state[i][5][r-1][4]=ogs_game_id
            state[opponent_idx][5][r-1][4]=ogs_game_id

            await ctx.send("Game result recorded! "+ {"b":"Black won!", "w":"White won!", "null":"Game anulled!"}[arg1.lower()])

            with open("data/games.csv", "a") as f:
                p1 = await ctx.guild.fetch_member(ctx.author.id)
                p2 = await ctx.guild.fetch_member(opponent_id)
                if colour=="w": p1,p2 = p2, p1

                f.write("{},{},{},{},{},{},{}\n".format(str(p1.id), str(p2.id), p1.display_name, p2.display_name, r, arg1.lower(), url))

            break

    with open("data/state.txt", "w") as f: f.write(repr((r,state)))

#@bot.command()
#async def swap(ctx, id1, id2):
#    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
#    if ctx.channel.id != admin_channel_id: return
#
#    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())
#    i= state.find(id1)
#    j= state.find(id2)
#
#    with open("data/state.txt", "w") as f: f.write(repr((r,state)))
#    return #XXX

#TODO outcome should receive an OGS game link as an optional argument
@bot.command()
async def outcome(ctx, idx1, result):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    if ctx.channel.id != admin_channel_id: return

    if result not in ["+","-"]:
        await ctx.send("Error: outcome should be '+' or '-'")
        return

    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())

    #Only allow for this if we aren't in the middle of a pairings step
    if r==0 or r!=len(state[0][5]):
        await ctx.send("Deciding outcomes manually is currently impossible!")
        return

    r=int(r); idx1=int(idx1)

    match = state[idx1-1][5][r-1]
    state[idx1-1][5][r-1][1]=result

    opp_id=state[idx1-1][5][r-1][0]
    if opp_id!=0:
        opp_index= next(j for j in range(len(state)) if state[j][0]==opp_id)
        match = state[opp_index][5][r-1]
        #state[opp_index][5][r-1]=(match[0],'+' if result=='-' else '-', match[2],match[3],match[4])
        state[opp_index][5][r-1][1]='+' if result=='-' else '-'

    with open("data/state.txt", "w") as f: f.write(repr((r,state)))
    #await make_mrchance_happy2(ctx)
    #await ctx.send(file=discord.File("data/tournament.csv"))

    text= pretty_print(state)
    await ctx.send(text)
    return

@bot.command()
async def standings(ctx):
    if ctx.guild.id!= awesome_server_id or ctx.channel.id not in permitted_channel_ids: return
    if ctx.channel.id!= admin_channel_id: return

    with open("data/state.txt") as f: r,state = ast.literal_eval(f.read())
    text= pretty_print(state)
    await ctx.send(text)

    await make_mrchance_happy2(ctx)
    await ctx.send(file=discord.File("data/tournament.csv"))

#bot.loop.create_task(background_task())
bot.run(token)
