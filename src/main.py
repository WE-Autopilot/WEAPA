import discord
from discord.ext import commands
from SECRETS import bot_token, channel_id
import pandas as pd
import numpy as np


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.guilds = True
client = commands.Bot(command_prefix="/", intents=intents)
members_file = "members.csv"


@client.event
async def on_ready():
    print(f"{client.user} is active!")


@client.command()
async def verify(ctx, uwo_id):
    await ctx.message.delete()
    print(ctx.channel.id, channel_id, ctx.channel.id != channel_id)
    if ctx.channel.id != channel_id:
        await ctx.send(f"This command can only be used in <#{channel_id}>.", delete_after=5)
        return

    print(f"Attempting to verify {uwo_id}...")
    members = pd.read_csv(members_file)

    if (members["discord"] == ctx.author.name).any():
        await ctx.send("You're already verified under another ID. Please contact a moderator if you believe this to be a mistake.")
        print(f"Failed to verify {uwo_id} because the identity is not in the file.")
        return

    uwo_id = uwo_id.strip().lower()
    if (members["id"] != uwo_id).all():
        await ctx.send("That doesn't seem to be an UWO ID.")
        print(f"Failed to verify {uwo_id} because the identity is not in the file.")
        return

    row = np.where(members["id"] == uwo_id)[0][0]
    if members.loc[row, "discord"] == members.loc[row, "discord"]:
        await ctx.send("That UWO ID is already verified. Please contact a moderator if you believe this to be a mistake.")
        print(f"Failed to verify {uwo_id} because the identity was already taken.")
        return

    name = "".join(members.loc[row, ["first name", "last name"]])
    team = members.loc[row, "team"]
    await ctx.send(f"Welcome {name} to the {team}!")

    role = discord.utils.get(ctx.guild.roles, name=team)
    await ctx.author.add_roles(role)

    members.loc[row, "discord"] = ctx.author.name
    members.to_csv(members_file, index=False)
    print(f"Verified {uwo_id} successfully!")


client.run(bot_token)
