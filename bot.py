"""
Sam's Counting Bot
"""

from datetime import datetime
import json
import logging
import os
import platform
import sys
import pickle
# import aiosqlite
# from database import DatabaseManager

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv


JUSTSAM = 1014373548938235914
main_dir = os.path.realpath(os.path.dirname(__file__))

if not os.path.isfile(f"{main_dir}/config.json"):
    sys.exit("error: 'config.json' not found!")
else:
    with open(f"{main_dir}/config.json") as file:
        config = json.load(file)

if os.path.exists(f'{main_dir}/config.pickle'):
    with open(f'{main_dir}/config.pickle', 'rb') as f:
        config2 = pickle.load(f)
else:
    config2 = {}

'''Setup bot intents'''
intents = discord.Intents.all()

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

logger = logging.getLogger('CC')
logger.setLevel(logging.INFO)

def setlogger():
    '''Setup the logger'''
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())
    file_handler = logging.FileHandler('./logs/CC.log', 'a', 'utf-8')
    file_handler_formatter = logging.Formatter(
        "[{asctime}] [{levelname}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
    )
    file_handler.setFormatter(file_handler_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

class DiscordBot(commands.Bot):
    '''Our Bot'''
    def __init__(self) -> None:
        super().__init__(
        command_prefix = commands.when_mentioned_or(config['prefix']),
        intents = intents,
        help_command = None
        )
        self.logger = logger
        self.main_dir = main_dir
        self.config = config
        self.database = None
        self.config2 = config2
        self.fail_role_id = config2.get('fail_role_id', None)
        self.counting_channel_id = config2.get('channel_id', None)

    # async def init_db(self) -> None:
    #     '''Initialize the database'''
    #     async with aiosqlite.connect(main_dir + '/database/database.db') as db:
    #         with open(main_dir + '/database/schema.sql') as schema:
    #             await db.executescript(schema.read())
    #         await db.commit()    

    async def load_cogs(self) -> None:
        '''Load all the cogs in the cogs folder'''
        for file in os.listdir(main_dir + '/cogs'):
            if file.endswith('.py'):
                extension = file[:-3]
                if extension == 'template':
                    continue
                try:
                    await self.load_extension(f'cogs.{extension}')
                    self.logger.info(f'Loaded extension: {extension}')
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(f"failed to load extension {extension}\n  {exception}")
    
    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        '''Set a random status every minute'''
        await self.change_presence(
            activity=discord.Activity(type = discord.ActivityType.watching, name = "numbers!"),
            status=discord.Status.idle
            )
        
    @tasks.loop(minutes=10.0)
    async def regular_ping(self) -> None:
        """Latency check after 10 minutes"""
        self.logger.info(f"{datetime.now().strftime('%B %d, %Y | %H:%M:%S')} The bot latency is {self.latency*1000}ms.")

    @regular_ping.before_loop
    @status_task.before_loop
    async def before_status_task(self) -> None:
        '''Wait until the bot is ready'''
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        '''This will be executed when the bot starts the first time.'''
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        # await self.init_db()
        await self.load_cogs()
        self.status_task.start()
        self.regular_ping.start()

        # self.database = DatabaseManager(
        #     connection=await aiosqlite.connect(main_dir + "/database/database.db")
        # )

    async def on_message(self, message: discord.Message) -> None:
        '''This will be executed every time a message is sent'''
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        '''This will be executed every time a command is successfully completed'''
        executed_command = context.command.name
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error.

        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in \
                            {f'{round(days)} days' if round(days) > 0 else ''} \
                            {f'{round(hours)} hours' if round(hours) > 0 else ''} \
                            {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} \
                            {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="You are not the owner of the bot!", color=0xE02B2B
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id})."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs."
                )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error


def synccmd(bot: commands.Bot):
    @bot.command(name="isync", description="Synchonizes the slash commands.")
    @commands.is_owner()
    async def isync(context: Context, scope: str) -> None:
        """
        Synchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global` or `guild`.
        """
        print('syncing...')
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

load_dotenv()

if __name__=='__main__':
    setlogger()
    bot = DiscordBot()
    # synccmd(bot) # use this only when first time setting up bot. After syncing once remove this line
    bot.run(os.getenv("TOKEN"))