import discord
import asyncio

from os import environ
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

load_dotenv()
token = environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
MY_GUILD = discord.Object(id=591155506219843584)
MY_ID = 234016394621091841


class Lucian(commands.Bot):
    def __init__(self,intents:discord.Intents,command_prefix:str,description: str):
        super().__init__(intents=intents,command_prefix=command_prefix,description=description)


    async def setup_hook(self):
        print("Running setup hook")

    async def on_ready(self):
        activity = discord.Activity(type=discord.ActivityType.watching,name="his own code")
        await self.change_presence(activity=activity)
        await self.load_extension("cogs.werewolf")



lucian = Lucian(intents,"$","Werewolf game")

@lucian.command()
async def sync(ctx):
    if ctx.author.id == MY_ID:
        await lucian.tree.sync()
        print("syncing commands...")
        await ctx.channel.send("Syncing commands...")

@lucian.command()
async def guild(ctx):
    if ctx.author.id == MY_ID:
        file = open("werewolf.jpg","rb")
        byte = file.read()
        newGuild = await lucian.create_guild(name="Werewolf",icon=byte)
        channel = await newGuild.create_text_channel("general")
        invite = await channel.create_invite(max_age=0,max_uses=0)
        await ctx.channel.send("Heres the invite link : " + str(invite))

@lucian.command()
async def invite(ctx):
    if ctx.author.id == MY_ID:
        print(lucian.guilds)
        for guild in lucian.guilds:
            print(guild.name)
            if guild.name == "Werewolf":
                print("found guild")
            
                
            

lucian.run(token)