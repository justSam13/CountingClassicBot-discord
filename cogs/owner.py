import os
import random
import sys
from typing import Literal
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="sync",
        description="Synchonizes the slash commands.",
    )
    @app_commands.describe(scope="The scope of the sync. Can be `global` or `guild`")
    @commands.is_owner()
    async def sync(self, context: Context, scope: Literal['global', 'guild']) -> None:
        """
        Synchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global` or `guild`.
        """

        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Slash commands have been synchronized in this guild.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unsync",
        description="Unsynchonizes the slash commands.",
    )
    @app_commands.describe(
        scope="The scope of the sync. Can be `global` or `guild`"
    )
    @commands.is_owner()
    async def unsync(self, context: Context, scope: Literal['global', 'guild']) -> None:
        """
        Unsynchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global` or `guild`.
        """

        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally unsynchronized.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Slash commands have been unsynchronized in this guild.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    # @commands.hybrid_command(
    #     name="load",
    #     description="Load a cog",
    # )
    # @app_commands.describe(cog="The name of the cog to load")
    # @commands.is_owner()
    # async def load(self, context: Context,
    #                cog: Literal['fun', 'general', 'mod', 'owner', 'redeem']
    #                ) -> None:
    #     """
    #     The bot will load the given cog.

    #     :param context: The hybrid command context.
    #     :param cog: The name of the cog to load.
    #     """
    #     try:
    #         await self.bot.load_extension(f"cogs.{cog}")
    #     except Exception:
    #         embed = discord.Embed(
    #             description=f"Could not load the `{cog}` cog.", color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return
    #     embed = discord.Embed(
    #         description=f"Successfully loaded the `{cog}` cog.", color=0xBEBEFE
    #     )
    #     await context.send(embed=embed)

    # @commands.hybrid_command(
    #     name="unload",
    #     description="Unloads a cog.",
    # )
    # @app_commands.describe(cog="The name of the cog to unload")
    # @commands.is_owner()
    # async def unload(self, context: Context,
    #                  cog: Literal['fun', 'general', 'mod', 'owner', 'redeem']
    #                  ) -> None:
    #     """
    #     The bot will unload the given cog.

    #     :param context: The hybrid command context.
    #     :param cog: The name of the cog to unload.
    #     """
    #     try:
    #         await self.bot.unload_extension(f"cogs.{cog}")
    #     except Exception:
    #         embed = discord.Embed(
    #             description=f"Could not unload the `{cog}` cog.", color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return
    #     embed = discord.Embed(
    #         description=f"Successfully unloaded the `{cog}` cog.", color=0xBEBEFE
    #     )
    #     await context.send(embed=embed)

    # @commands.hybrid_command(
    #     name="reload",
    #     description="Reloads a cog.",
    # )
    # @app_commands.describe(cog="The name of the cog to reload")
    # @commands.is_owner()
    # async def reload(self, context: Context, 
    #                  cog: Literal['fun', 'general', 'mod', 'owner', 'redeem']
    #                  ) -> None:
    #     """
    #     The bot will reload the given cog.

    #     :param context: The hybrid command context.
    #     :param cog: The name of the cog to reload.
    #     """
    #     try:
    #         await self.bot.reload_extension(f"cogs.{cog}")
    #     except Exception as e:
    #         embed = discord.Embed(
    #             description=f"Could not reload the `{cog}` cog.\n {e}", color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return
    #     embed = discord.Embed(
    #         description=f"Successfully reloaded the `{cog}` cog.", color=0xBEBEFE
    #     )
    #     await context.send(embed=embed)

    # @commands.hybrid_command(
    #     name="shutdown",
    #     description="Make the bot shutdown.",
    # )
    # @commands.is_owner()
    # async def shutdown(self, context: Context) -> None:
    #     """
    #     Shuts down the bot.

    #     :param context: The hybrid command context.
    #     """
    #     embed = discord.Embed(description="Shutting down. Bye! :wave:", color=0xBEBEFE)
    #     await context.send(embed=embed)
    #     await self.bot.close()
    #     sys.exit()

    # @commands.hybrid_command(
    #     name="say",
    #     description="The bot will say anything you want.",
    # )
    # @app_commands.describe(message="The message that should be repeated by the bot")
    # @app_commands.describe(channel="The channel to send the message to")
    # @app_commands.describe(delete="Number of seconds after which delete the message or 'no' to not delete")
    # @commands.is_owner()
    # async def say(self, context: Context, channel: discord.TextChannel, delete: str, *, message: str) -> None:
    #     """
    #     The bot will say anything you want.

    #     :param context: The hybrid command context.
    #     :param message: The message that should be repeated by the bot.
    #     """
    #     try:
    #         await context.message.delete()
    #     except: pass
    #     try:
    #         delete = float(delete)
    #     except: delete = None
    #     await channel.send(message, delete_after=delete)
    #     await context.send("Done", delete_after=1.5)

    # @commands.hybrid_command(
    #     name="embed",
    #     description="The bot will say anything you want, but within embeds.",
    # )
    # @app_commands.describe(message="The message that should be repeated by the bot")
    # @app_commands.describe(channel="The channel to send the embed to")
    # @app_commands.describe(delete="Number of seconds after which delete the embed or 'no' to not delete")
    # @commands.is_owner()
    # async def embed(self, context: Context, channel: discord.TextChannel, delete: str, *, message: str) -> None:
    #     """
    #     The bot will say anything you want, but using embeds.

    #     :param context: The hybrid command context.
    #     :param message: The message that should be repeated by the bot.
    #     """
    #     try:
    #         await context.message.delete()
    #     except: pass
    #     clr = random.choice([discord.Colour.blue(),
    #                         discord.Colour.brand_red(),
    #                         discord.Colour.dark_embed(),
    #                         discord.Colour.dark_orange(),
    #                         discord.Colour.dark_teal(),
    #                         discord.Colour.greyple(),
    #                         discord.Colour.orange(),
    #                         discord.Colour.teal()])
    #     embed = discord.Embed(description=message, color=clr)
    #     try:
    #         delete = float(delete)
    #     except: delete = None
    #     await channel.send(embed=embed, delete_after=delete)
    #     await context.send("Done", delete_after=1.5)

    # @commands.hybrid_command(
    #     name = "edit_embed",
    #     description = "Edit a previously sent embed"
    # )
    # @app_commands.describe(message="ID/Link of the message containing the embed")
    # @app_commands.describe(new_message="The new content of the embed")
    # @commands.is_owner()
    # async def edit_embed(self, context: Context, message: discord.Message, new_message: str):
    #     embed = message.embeds[0]
    #     new_embed = discord.Embed(description=new_message, color=embed.color)
    #     await message.edit(embed=new_embed)
    #     try:
    #         await context.message.delete()
    #     except: pass
    #     await context.send("Done!", delete_after=1.5)

    # @commands.hybrid_group(
    #     name="blacklist",
    #     description="Get the list of all blacklisted users.",
    # )
    # @commands.is_owner()
    # async def blacklist(self, context: Context) -> None:
    #     """
    #     Lets you add or remove a user from not being able to use the bot.

    #     :param context: The hybrid command context.
    #     """
    #     if context.invoked_subcommand is None:
    #         embed = discord.Embed(
    #             description="You need to specify a subcommand.\n\n**Subcommands:**\n`add` - Add a user to the blacklist.\n`remove` - Remove a user from the blacklist.",
    #             color=0xE02B2B,
    #         )
    #         await context.send(embed=embed)

    # @blacklist.command(
    #     base="blacklist",
    #     name="show",
    #     description="Shows the list of all blacklisted users.",
    # )
    # @commands.is_owner()
    # async def blacklist_show(self, context: Context) -> None:
    #     """
    #     Shows the list of all blacklisted users.

    #     :param context: The hybrid command context.
    #     """
    #     blacklisted_users = await self.bot.database.get_blacklisted_users()
    #     if len(blacklisted_users) == 0:
    #         embed = discord.Embed(
    #             description="There are currently no blacklisted users.", color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return

    #     embed = discord.Embed(title="Blacklisted Users", color=0xBEBEFE)
    #     users = []
    #     for bluser in blacklisted_users:
    #         user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(
    #             int(bluser[0])
    #         )
    #         users.append(f"• {user.mention} ({user}) - Blacklisted <t:{bluser[1]}>")
    #     embed.description = "\n".join(users)
    #     await context.send(embed=embed)

    # @blacklist.command(
    #     base="blacklist",
    #     name="add",
    #     description="Lets you add a user from not being able to use the bot.",
    # )
    # @app_commands.describe(user="The user that should be added to the blacklist")
    # @commands.is_owner()
    # async def blacklist_add(self, context: Context, user: discord.User) -> None:
    #     """
    #     Lets you add a user from not being able to use the bot.

    #     :param context: The hybrid command context.
    #     :param user: The user that should be added to the blacklist.
    #     """
    #     user_id = user.id
    #     if await self.bot.database.is_blacklisted(user_id):
    #         embed = discord.Embed(
    #             description=f"**{user.name}** is already in the blacklist.",
    #             color=0xE02B2B,
    #         )
    #         await context.send(embed=embed)
    #         return
    #     total = await self.bot.database.add_user_to_blacklist(user_id)
    #     embed = discord.Embed(
    #         description=f"**{user.name}** has been successfully added to the blacklist",
    #         color=0xBEBEFE,
    #     )
    #     embed.set_footer(
    #         text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
    #     )
    #     await context.send(embed=embed)

    # @blacklist.command(
    #     base="blacklist",
    #     name="remove",
    #     description="Lets you remove a user from not being able to use the bot.",
    # )
    # @app_commands.describe(user="The user that should be removed from the blacklist.")
    # @commands.is_owner()
    # async def blacklist_remove(self, context: Context, user: discord.User) -> None:
    #     """
    #     Lets you remove a user from not being able to use the bot.

    #     :param context: The hybrid command context.
    #     :param user: The user that should be removed from the blacklist.
    #     """
    #     user_id = user.id
    #     if not await self.bot.database.is_blacklisted(user_id):
    #         embed = discord.Embed(
    #             description=f"**{user.name}** is not in the blacklist.", color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return
    #     total = await self.bot.database.remove_user_from_blacklist(user_id)
    #     embed = discord.Embed(
    #         description=f"**{user.name}** has been successfully removed from the blacklist",
    #         color=0xBEBEFE,
    #     )
    #     embed.set_footer(
    #         text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
    #     )
    #     await context.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
