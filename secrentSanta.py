import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")
secretSantas = []
assignments = {}
isStarted = False
description = "Have fun!"

async def getNickname(ctx, user: discord.User):
    member = ctx.guild.get_member(user.id)
    if (member is None):
        await ctx.send(f'Could not find {user.name} in this server')
        return None

    nickname = member.nick if member.nick else user.name
    return nickname

@bot.event
async def on_ready():
    await print(f'{bot.user} has connected to Discord!')

@bot.command('add')
async def addSanta(ctx, user: discord.User = None):
    if (user == None):
        await ctx.send(f'Ping user after command to make them a Secret Santa')
        return

    if (user in secretSantas):
        nickname = await getNickname(ctx, user)
        await ctx.send(f'{nickname} is already a Secret Santa')
        return

    nickname = await getNickname(ctx, user)
    if nickname is None:
        await ctx.send(f'Can not add user to Secret Santa. Invalid username')
        return
    secretSantas.append(user)
    await ctx.send(f'{nickname} is a Secret Santa')

@bot.command('remove')
async def removeSanta(ctx, user: discord.User = None):
    if (user == None):
        await ctx.send(f'Ping user after command to remove them from being a Secret Santa')
        return

    if (user not in secretSantas):
        nickname = await getNickname(ctx, user)
        await ctx.send(f'{nickname} is not currently a Secret Santa')
        return

    secretSantas.remove(user)
    if user in assignments:
        del assignments[user]
    nickname = await getNickname(ctx, user)
    await ctx.send(f'{nickname} has been removed from Secret Santas')

@bot.command('list')
async def listSantas(ctx):
    if (len(secretSantas) == 0):
        await ctx.send('There are no users participating in Secret Santa')
        return

    message = ""
    for user in secretSantas:
        nickname = await getNickname(ctx, user)
        message += nickname + "\n"

    await ctx.send(f'The following users are participating:\n{message}')

@bot.command('start')
async def startSecretSanta(ctx):
    if (len(secretSantas) <= 2):
        await ctx.send('There must be at least 3 Santas to start Secret Santa')
        return

    await ctx.send('**Starting Rod Wave`s Secret Santa**')
    message = ""
    for user in secretSantas:
        nickname = await getNickname(ctx, user)
        message += nickname + "\n"

    await ctx.send(f'The following users are participating:\n{message}')

    for user in secretSantas:
        shuffled = secretSantas[:]
        random.shuffle(shuffled)
        for i in range(len(secretSantas)):
            key = secretSantas[i]
            value = shuffled[i]
            if key == value:
                if i == len(secretSantas) - 1:
                    shuffled[i], shuffled[i - 1] = shuffled[i - 1], shuffled[i]
                else:
                    shuffled[i], shuffled[i + 1] = shuffled[i + 1], shuffled[i]

            assignments[key] = shuffled[i]

    for giver, receiver in assignments.items():
        nickname = await getNickname(ctx, receiver)
        await giver.send(f"**Secret Santa has started!**\nYou are giving a gift to {nickname}! Be creative\n{description}")

    global isStarted
    isStarted = True

@bot.command('sneakPeek')
async def print(ctx):
    for key, value in assignments.items():
        giverNickname = await getNickname(ctx, key)
        receiverNickname = await getNickname(ctx, value)
        await ctx.send(f'{giverNickname} is giving a gift to {receiverNickname}')

@bot.command('verify')
async def verify(ctx):
    if not isStarted:
        await ctx.send(f'Start Secret Santa to verify')
        return

    for key, value in assignments.items():
        if (key == value):
            await ctx.send(f'Secret Santa is invalid. Start it again')
            return

    await ctx.send('Secret Santa is valid. Everyone will be getting a gift')

@bot.command('setDescription')
async def setDescription(ctx, *, _description):
    global description
    description = _description
    await ctx.send("Description saved")

bot.run(TOKEN)