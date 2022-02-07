import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
from discord_slash.utils.manage_components import ComponentContext
from pymongo import MongoClient
import datetime
import asyncio

bot = commands.Bot(command_prefix="!", case_insinsative=True)

cluster = MongoClient("mongodb+srv://King:Supdog27@cluster0.q3pqn.mongodb.net/VanillaPlusTrading?retryWrites=true&w=majority")
Trading = cluster["VanillaPlusTrading"]
Processing = Trading["Processing"]
Completed = Trading["Completed"]

date_format = "%a, %b, %d, %Y, at %I:%M%p"

class TradeUpdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="report", description="Report A Trade!", guild_ids=[901267167213924373])
    @commands.has_any_role("Trade Moderator")
    async def report(self, ctx, user: discord.Member, *, items):

        stop = {}

        if user.id == ctx.author.id:

            embed = discord.Embed(
            title="<a:Cross:937830066514182235> You cannot trade with yourself!", 
            color=discord.Color.red())

            await ctx.send(embed=embed, hidden=True)

        else:
            
            embed = discord.Embed(
            title="Trade Reported!", 
            description="Please confirm if you completed this trade:", 
            color=discord.Color.gold())
            embed.add_field(
            name="With User", 
            value=f"{ctx.author.mention}",
            inline=True)
            embed.add_field(
            name="Items Traded", 
            value=f"{items}", 
            inline=True)
            embed.set_footer(text=f"Please make a ticket if this user keeps reporting false trades.")

            count = (f"0-{int(Processing.find().count())+1}")

            buttons = [
                create_button(
                    style=ButtonStyle.green, 
                    label="Confirm", 
                    emoji="✅", 
                    custom_id=f"{count}-Trade Confirm"),
                create_button(
                style=ButtonStyle.red, 
                label="Deny", 
                emoji="❌", 
                custom_id=f"{count}-Trade Deny")]

            action_row = create_actionrow(*buttons)

            try:

                await user.send(content=user.mention, embed=embed, components=[action_row])

            except discord.Forbidden:

                embed = discord.Embed(
                title="<a:Cross:937830066514182235> Tell that user to open their Dms!", 
                color=discord.Color.red())

                await ctx.send(embed=embed, hidden=True)

                stop = True

            if stop != True:

                post = {"_id": (count), "User 1": ctx.author.id, "User 2": user.id, "Items": items, "Confirmed": False}
                Processing.insert_one(post)

                logs = discord.utils.get(ctx.guild.channels, id=938188280841789470)

                embed = discord.Embed(
                title="Trade Initiated", 
                color=discord.Color.red())
                embed.add_field(
                name="Users", 
                value=f"User 1: {ctx.author.mention} | [`{ctx.author.id}`]\nUser 2: {user.mention} | [`{user.id}`]",
                inline=False)
                embed.add_field(
                name="Items", 
                value=f"{items}", 
                inline=False)
                embed.set_footer(text=f"Trade ID: {count} | Trade Initiated on {datetime.datetime.now().strftime(date_format)}")

                await logs.send(embed=embed)

                embed = discord.Embed(
                title="<a:Check:937830119710552094> Tell that user to check their DMs!", 
                color=discord.Color.green())

                await ctx.send(embed=embed, hidden=True)

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):

        stop1 = {}
        stop2 = {}

        if ctx.custom_id.endswith("Trade Confirm") == True:

            trade_id = ctx.custom_id[:-14]

            try:

                trade = Processing.find({"_id": trade_id})

            except:

                embed = discord.Embed(
                title="<a:Cross:937830066514182235> An error occoured.", 
                description="Most likely this trade has already been marked.",
                color=discord.Color.red())

                await ctx.send(embed=embed)

                stop1 = True

            for i in trade:

                confirmed = (i["Confirmed"])

            if confirmed == True:

                embed = discord.Embed(
                title="<a:Cross:937830066514182235> You already confirmed this trade!", 
                description="It is being processed by the moderators.",
                color=discord.Color.red())

                await ctx.send(embed=embed)

                stop2 = True

            if stop1 != True and stop2 != True:

                marking_channel: discord.TextChannel = await self.bot.fetch_channel(938600881044201492)
                logs_channel: discord.TextChannel = await self.bot.fetch_channel(938188280841789470)

                for i in trade:

                    user_one_id = (i["User 1"])
                    items = (i["Items"])
                    user_two_id = (i["User 2"])

                user_one: discord.User = await self.bot.fetch_user(user_one_id)
                user_two: discord.User = await self.bot.fetch_user(user_two_id)

                embed = discord.Embed(
                title="Trade Confirmed",
                color=discord.Color.orange())
                embed.add_field(
                name="Users", 
                value=f"User 1: {user_one.mention} | [`{user_one.id}`]\nUser 2: {user_two.mention} | [`{user_two.id}`]", 
                inline=False)
                embed.add_field(
                name="Items", 
                value=f"{items}", 
                inline=False)
                embed.set_footer(text=f"Trade ID: {trade_id} | Trade confirmed on {datetime.datetime.now().strftime(date_format)}")

                await logs_channel.send(embed=embed)

                embed = discord.Embed(
                title="<a:Check:937830119710552094> This trade has been confirmed!",
                color=discord.Color.green())

                await ctx.send(embed=embed)

                embed = discord.Embed(
                title="Trade needs verification!", 
                color=discord.Color.gold())
                embed.add_field(
                name="Users", 
                value=f"User 1: {user_one.mention} | [`{user_one.id}`]\nUser 2: {user_two.mention} | [`{user_two.id}`]", 
                inline=False)
                embed.add_field(
                name="Items", 
                value=f"{items}", 
                inline=False)
                embed.set_footer(text=f"Trade ID: {trade_id} | Trade confirmed on {datetime.datetime.now().strftime(date_format)}")

                buttons = [
                    create_button(
                        style=ButtonStyle.green, 
                        label="Verify", 
                        emoji="✅", 
                        custom_id=f"{trade_id}-Trade Verify"),
                    create_button(
                        style=ButtonStyle.red, 
                        label="Deny", 
                        emoji="❌", 
                        custom_id=f"{trade_id}-Trade Anti-Verify")]

                action_row = create_actionrow(*buttons)

                await marking_channel.send(embed=embed, components=[action_row])

        if ctx.custom_id.endswith("Trade Verify"):

            trade_id = ctx.custom_id[:-13]

            stop = {}

            try:

                trade = Processing.find({"_id": trade_id})

            except:

                embed = discord.Embed(
                title="<a:Cross:937830066514182235> An error ocourred.", 
                description="The bot was unable to find this trade.", 
                color=discord.Color.red())

                message = await ctx.send(embed=embed, hidden=True)

                await asyncio.sleep(3)

                message.delete()

                stop = True

            if stop != True:

                for i in trade:
                    items = (i["Items"])
                    user_one_id = (i["User 1"])
                    user_two_id = (i["User 2"])

                count = (f"1-{int(Completed.find().count())+1}")

                guild: discord.Guild = self.bot.get_guild(901267167213924373)

                user_one: discord.Member = guild.get_member(user_one_id)
                user_two: discord.Member = guild.get_member(user_two_id)

                if bool(str(user_one.display_name[::-1]).startswith("]")) == False:

                    new_amount = 1
                    display_name = user_one.display_name
                    old_amount = 0

                else:

                    old_amount1 = (str(user_one.display_name[::-1]).split("["))
                    old_amount = (((old_amount1[0])[::-1])[:-1])
                    new_amount = int(old_amount) + 1

                display_name = user_one.display_name[:-int(len(str(old_amount)) + 3)]

                await user_one.edit(nick=f"{display_name} [{new_amount}]")

                if bool(str(user_two.display_name[::-1]).startswith("]")) == False:

                    new_amount = 1
                    display_name = user_two.display_name
                    old_amount = 0

                else:

                    old_amount1 = (str(user_two.display_name[::-1]).split("["))
                    old_amount = (((old_amount1[0])[::-1])[:-1])
                    new_amount = int(old_amount) + 1

                display_name = user_two.display_name[:-int(len(str(old_amount)) + 3)]

                await user_two.edit(nick=f"{display_name} [{new_amount}]")

                Processing.remove({"_id": trade_id})

                post = ({"_id": count, "User 1": user_one_id, "User 2": user_two_id, "Items": items})

                Completed.insert_one(post)


            if ctx.custom_id.endswith("Trade Anti-Verify"):

                trade_id = ctx.custom_id[:-18]

                try:

                    Processing.delete_one({"_id": trade_id})

                except:

                    pass
                
                embed = discord.Embed(
                title="This trade has been not verified and will now be deleted.", 
                description="This message will delete in 1 second.", 
                color=discord.Color.red())

                msg = await ctx.send(embed=embed, hidden=True)

                asyncio.sleep(1.25)

                await msg.delete()

            if ctx.custom_id.endswith("Trade Deny") == True:
                
                trade_id = ctx.custom_id[:-11]

                try:
                    
                    Processing.delete_one({"_id": trade_id})

                except:

                    pass

                embed = discord.Embed(
                title="This trade has not been confirmed and will now be deleted.", 
                color=discord.Color.red())

                await ctx.send(embed=embed)
                
def setup(bot):
    bot.add_cog(TradeUpdates(bot))