from typing import Text
import discord
from discord.ext import commands
import asyncio
import re
from discord.utils import get
from discord_slash import cog_ext
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
from discord_slash.utils.manage_components import ComponentContext
import datetime
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

bot = commands.Bot(command_prefix="!", case_insinsative=True)

date_format = "%a, %b, %d, %Y, at %I:%M%p"

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Style.BRIGHT}{Fore.CYAN}Online {Fore.WHITE}on {Fore.MAGENTA}{datetime.datetime.now().strftime(date_format)}, EST")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{Style.BRIGHT}{Fore.GREEN}New Member: {Fore.MAGENTA}{member} - {member.id}")
        channel = discord.utils.get(member.guild.channels, id=901983187411017840)
        role = discord.utils.get(member.guild.roles, id=901271944375185418)
        nick = f"{member.name} [0]"
        await channel.send(f"Welcome {member.mention} to the **Vanilla+ Trading Discord!**")
        await member.edit(nick=nick)
        await member.add_roles(role)
    
    @commands.Cog.listner()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    @cog_ext.cog_slash(name="nick", description="Change your nickname!", guild_ids=[901267167213924373])
    async def _nick(self, ctx, nick):
        user = ctx.author
        old_amount1 = (str(user.display_name[::-1]).split("["))
        trade_count = (((old_amount1[0])[::-1])[:-1])
        await user.edit(nick=f"{nick} [{trade_count}]")
        await ctx.send(f"{user.mention} - Nickname Updated.")

    @cog_ext.cog_slash(name="rankup", description="Mark someone's trades.", guild_ids=[901267167213924373])
    @commands.has_any_role("Trade Moderator")
    async def _rankup(self, ctx, member: discord.Member):
        if bool(str(member.display_name[::-1]).startswith("]")) == False:
            new_amount = 1
            display_name = member.display_name
            old_amount = 0
        else:
            old_amount1 = (str(member.display_name[::-1]).split("["))
            old_amount = (((old_amount1[0])[::-1])[:-1])
            new_amount = int(old_amount) + 1
            display_name = member.display_name[:-int(len(str(old_amount)) + 3)]
        await member.edit(nick=f"{display_name} [{new_amount}]")

        log_embed = discord.Embed(
        title="Trade Count Updated (Added Trades)", 
        color=discord.Color.blue())
        log_embed.add_field(
        name="Trade Moderator:", 
        value=f"{ctx.author.mention} - {ctx.author.id}", 
        inline=True)
        log_embed.add_field(
        name="Member Effected:", 
        value=f"{member} - {member.id}", 
        inline=True)
        log_embed.add_field(
        name="Count (+):", 
        value=f"Before: {old_amount}\nAfter: {new_amount}", 
        inline=True)
        logs_channel = discord.utils.get(ctx.guild.text_channels, name="bot-logs")
        await logs_channel.send(embed=log_embed)
        await ctx.send(f"{display_name}'s trades have been updated.")

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def scammer(self, ctx):
        scammer_embed = discord.Embed(
        title="Vanilla+ Scammers List", 
        description="The scammers list is used to verify who is trustworthy to trade with. If you are caught scamming another player you will be given the scammer role, and you will be listed here. If a scammer wants to be removed from the list they must get 20 confirmed trades. Forms of scamming may include but are not limited to:\nNot dropping items\nStealing from traders during a trade", 
        color=discord.Color.red())
        scammer_embed.add_field(
        name="Haps321", 
        value="Known Alts: kinggamer, bobo, "
        )
        scammer_embed.add_field(
        name="T0URMENT", 
        value="Known Alts: None\nProof: [here](https://medal.tv/games/minecraft/clips/5BVUzhRFYBshs/d1337OYgyk8Z?invite=cr-MSx1UUIsMjYyMDA2LA) & [here](https://cdn.discordapp.com/attachments/901948939341795388/922907764781629470/Screenshot_2021-12-21_124458.png)\nNamemc: [here](https://namemc.com/profile/T0URMENT.1)", 
        inline=False)
        scammer_embed.add_field(
        name="_sal1x\_", 
        value="Known Alts: None\nProof: [here](https://medal.tv/games/minecraft/clips/5BcuwLG5M-JDG/d13378doOUUc?invite=cr-MSxKOXAsMjI5NjYyMDks)\nNamemc: [here](https://namemc.com/profile/_sal1x_.1)", 
        inline=False)
        await ctx.send(embed=scammer_embed)

    @bot.command(aliases=["ticket"])
    @commands.has_permissions(administrator=True)
    async def _ticket(self, ctx):

        ticket_embed = discord.Embed(
        title="Vanilla+ Ticket System", 
        description="To create a ticket click on the button with the correct label.", 
        color=discord.Color.gold())
        ticket_embed.set_footer(text="Vanilla+ Trade Ticketing System")

        buttons = [
            create_button(
                style=ButtonStyle.blurple, 
                label="Scammer Appeal", 
                emoji="❌", 
                custom_id="ticket_001"), 

            create_button(
                style=ButtonStyle.blurple, 
                label="Support Ticket", 
                emoji="⚙", 
                custom_id="ticket_002"), 
            
            create_button(
                style=ButtonStyle.blurple, 
                label="General Items", 
                emoji="💭", 
                custom_id="ticket_003")]

        action_row = create_actionrow(*buttons)

        await ctx.send(embed=ticket_embed, components=[action_row])

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        if ctx.custom_id == "ticket_001" or ctx.custom_id == "ticket_002" or ctx.custom_id == "ticket_003" or ctx.custom_id == "close_button":
            guild = ctx.guild
            member = ctx.author
            trade_mod = discord.utils.get(ctx.guild.roles, id=901268566698000405)

            close_button = [
                    create_button(
                        style=ButtonStyle.red, 
                        label="Close Ticket", 
                        emoji="⛔", 
                        custom_id="close_button"
                    )
                ]

            close_action_row = create_actionrow(*close_button)

            if ctx.custom_id == "ticket_001":

                overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True)}
                channel = await guild.create_text_channel(name=f'appeal-{ctx.author.name}', overwrites=overwrites)
                await channel.set_permissions(member, view_channel=True)
                await channel.set_permissions(trade_mod, view_channel=True)

                starting_embed = discord.Embed(
                title="Scammer Appeal Ticket", 
                description="If you would like to close this ticket, please press the '⛔ Close' button.", 
                color=discord.Color.gold())

                ping = await channel.send(f"{trade_mod.mention}")
                await ping.delete()

                await channel.send(content=f"{ctx.author.mention}", embed=starting_embed, components=[close_action_row])

            if ctx.custom_id == "ticket_002":

                overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True)}
                channel = await guild.create_text_channel(name=f'support-{ctx.author.name}', overwrites=overwrites)
                await channel.set_permissions(member, view_channel=True)
                await channel.set_permissions(trade_mod, view_channel=True)

                starting_embed = discord.Embed(
                title="Support Ticket", 
                description="If you would like to close this ticket, please press the '⛔ Close' button.", 
                color=discord.Color.gold())

                ping = await channel.send(f"{trade_mod.mention}")
                await ping.delete()

                await channel.send(content=f"{ctx.author.mention}", embed=starting_embed, components=[close_action_row])

            if ctx.custom_id == "ticket_003":

                overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True)}
                channel = await guild.create_text_channel(name=f'general-{ctx.author.name}', overwrites=overwrites)
                await channel.set_permissions(member, view_channel=True)
                await channel.set_permissions(trade_mod, view_channel=True)

                starting_embed = discord.Embed(
                title="General Ticket", 
                description="If you would like to close this ticket, please press the '⛔ Close' button.", 
                color=discord.Color.gold())

                ping = await channel.send(f"{trade_mod.mention}")
                await ping.delete()

                await channel.send(content=f"{ctx.author.mention}", embed=starting_embed, components=[close_action_row])

            if ctx.custom_id == "close_button":
                close_embed = discord.Embed(
                title="Are you sure you want to close this ticket?", 
                description="Press the '❌ Close' button to close this ticket, or the '🚫 Cancel' button to cancel.", 
                color=discord.Color.red())

                end_buttons = [
                    create_button(
                        style=ButtonStyle.red, 
                        label="Close", 
                        emoji="❌", 
                        custom_id="end_button"
                    ), 
                    create_button(
                        style=ButtonStyle.grey, 
                        label="Cancel", 
                        emoji="🚫", 
                        custom_id="cancel_end_button"
                    )
                ]

                end_actionrow = create_actionrow(*end_buttons)

                await ctx.send(embed=close_embed, content=f"{ctx.author.mention}", components=[end_actionrow])

            if ctx.custom_id == "end_button":

                await ctx.send(f"This ticket will close soon.")
                await ctx.channel.delete()

            if ctx.custom_id == "cancel_end_button":
                await ctx.send(f"This ticket will not close.")
                await ctx.origin_message.delete()

def setup(bot):
    bot.add_cog(MainCog(bot))