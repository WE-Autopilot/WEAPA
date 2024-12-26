import discord
from discord.ext import commands
from SECRETS import bot_token, verification_channels, file_channels
import pandas as pd
import numpy as np


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.guilds = True
client = commands.Bot(command_prefix="/", intents=intents)
members_file = "members.csv"
EXEC_ROLE = "WEAP Exec"


@client.event
async def on_ready():
    print(f"{client.user} is active!")


@client.command()
async def verify(ctx, uwo_id):
    await ctx.message.delete()
    if not ctx.channel.id in verification_channels:
        await ctx.send(f"This command can only be used in <#{verification_channels[0]}>.", delete_after=5)
        return

    print(f"Attempting to verify {uwo_id}...")
    members = pd.read_csv(members_file)

    if (members["discord"] == ctx.author.name).any():
        await ctx.send("You're already verified under another ID. Please contact a moderator if you believe this to be a mistake.", delete_after=5)
        print(f"Failed to verify {uwo_id} because the identity is not in the file.")
        return

    uwo_id = uwo_id.strip().lower()
    if (members["id"] != uwo_id).all():
        await ctx.send("That doesn't seem to be an UWO ID.", delete_after=5)
        print(f"Failed to verify {uwo_id} because the identity is not in the file.")
        return

    row = np.where(members["id"] == uwo_id)[0][0]
    if members.loc[row, "discord"] == members.loc[row, "discord"]:
        await ctx.send("That UWO ID is already verified. Please contact a moderator if you believe this to be a mistake.", delete_after=5)
        print(f"Failed to verify {uwo_id} because the identity was already taken.")
        return

    name = " ".join(members.loc[row, ["first name", "last name"]])
    team = members.loc[row, "team"]
    await ctx.send(f"Welcome {name} to the {team}!")

    role = discord.utils.get(ctx.guild.roles, name=team)
    await ctx.author.add_roles(role)

    members.loc[row, "discord"] = ctx.author.name
    members.to_csv(members_file, index=False)
    print(f"Verified {uwo_id} successfully!")


@client.command()
async def getmembers(ctx):
    if not ctx.channel.id in file_channels:
        await ctx.send(f"This command can only be used in <#{file_channels[0]}>.", delete_after=5)
        return
    
    exec_role = discord.utils.get(ctx.guild.roles, name=EXEC_ROLE)
    if not exec_role in ctx.author.roles:
        await ctx.send(f"You need to be an {EXEC_ROLE} to use this command.", delete_after=5)
        return

    await ctx.send(file=discord.File(members_file))
    print("Sent the members.csv file.")


client.run(bot_token)
