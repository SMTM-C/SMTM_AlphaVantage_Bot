import discord
from discord.ext import commands

class Example(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    #Events
    @commands.Cog.listener() #if you want to create an event within a cog
    async def on_ready(self): #on_ready event has no parameters, must pass in self when inside of a cog
        print('Bot is online.')
    
    #Commands
    @commands.Cog.listener() #if you want to create a command within a cog
    async def ping(self, ctx):
        await ctx.send('Pong!')

def setup(client):
    client.add_cog(Example(client))