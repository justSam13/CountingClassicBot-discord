import random
from discord.ext import commands
from discord.ext.commands import Context
import discord
from bot import DiscordBot
import pickle

def update_config(bot : DiscordBot):
    with open(f'{bot.main_dir}/config.pickle', 'wb') as f:
        pickle.dump(bot.config2, f)

# Here we name the cog and create a new class for the cog.
class General(commands.Cog, name="general"):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="failrole",
        description="Set the fail role",
    )
    @commands.is_owner()
    async def failrole(self, context: Context, role: discord.Role = None) -> None:
        """
        Sets the fail role.

        :param context: The application command context.
        :param role: The role to be assigned.
        """
        if role is not None:
            self.bot.fail_role_id = role.id
            embed = discord.Embed(
                color=discord.Colour.dark_purple(),
                description=f"The fail role has been set to {role.mention}."
            )
        else:
            self.bot.fail_role_id = None
            embed = discord.Embed(
                color=discord.Colour.dark_purple(),
                description="The fail role has been disabled."
            )
        self.bot.config2['fail_role_id'] = self.bot.fail_role_id
        update_config(self.bot)
        await context.send(embed = embed)
    
    @commands.hybrid_command(
        name="setchannel",
        description="Set the channel for counting"
    )
    @commands.is_owner()
    async def setchannel(self, context: Context, channel: discord.TextChannel = None):
        """
        Sets the channel for counting.

        :param context: The application command context.
        :param channel: The channel to set.
        """
        if channel is not None:
            self.bot.counting_channel_id = channel.id
        else:
            self.bot.counting_channel_id = context.channel.id
            channel = context.channel
        
        embed = discord.Embed(
            color=discord.Colour.purple(),
            description=f"The counting channel has been set to {channel.mention}."
        )
        self.bot.config2['channel_id'] = self.bot.counting_channel_id
        update_config(self.bot)
        await context.send(embed = embed)

    @commands.hybrid_command(
        name="add-correct-reactions",
        description="Add reactions to correct number reactions"
    )
    @commands.is_owner()
    async def addcorrect(self, context: Context, reactions: str):
        """
        Add reactions to correct number reactions.

        :param context: The application command context.
        :param reactions: The reactions to add.
        """
        global correct_reactions
        for reaction in reactions.split():
            print(reaction)
            self.bot.config2['correct_reactions'] = self.bot.config2.get('correct_reactions', ['✅', '☑️']) + [reaction]
            correct_reactions = self.bot.config2['correct_reactions']
        embed = discord.Embed(
            color=discord.Colour.purple(),
            description=f"{', '.join(reactions.split())} successfully added to correct number reactions."
        )
        update_config(self.bot)
        await context.send(embed = embed)
    
    @commands.hybrid_command(
        name="add-wrong-reactions",
        description="Add reactions to wrong number reactions"
    )
    @commands.is_owner()
    async def addincorrect(self, context: Context, reactions: str):
        """
        Add a reaction to wrong number reactions.

        :param context: The application command context.
        :param reactions: The reactions to add.
        """
        global wrong_reactions
        for reaction in reactions.split():
            print(reaction)
            self.bot.config2['wrong_reactions'] = self.bot.config2.get('wrong_reactions', ['❌']) + [reaction]
            wrong_reactions = self.bot.config2['wrong_reactions']
        embed = discord.Embed(
            color=discord.Colour.purple(),
            description=f"{', '.join(reactions.split())} successfully added to wrong number reactions."
        )
        update_config(self.bot)
        await context.send(embed = embed)
    
    @commands.hybrid_command(
        name="show-reactions",
        description="Show all the reactions added"
    )
    @commands.is_owner()
    async def showreactions(self, context: Context):
        """
        Show all the saved reactions.
        """
        correct = ", ".join(self.bot.config2.get('correct_reactions', ['✅', '☑️']))
        wrong = ", ".join(self.bot.config2.get('wrong_reactions', ['❌']))
        embed = discord.Embed(
            color=discord.Colour.green(),
            description=f"Right: {correct}\nWrong: {wrong}"
        )
        await context.send(embed = embed)
    
    @commands.hybrid_command(
        name = "remove-reactions",
        description="Remove the given reactions"
    )
    @commands.is_owner()
    async def removereactions(self, context: Context, reactions: str = None):
        global correct_reactions, wrong_reactions
        if not reactions:
            correct_reactions = ['✅', '☑️']
            wrong_reactions = ['❌']
            self.bot.config2['correct_reactions'] = correct_reactions
            self.bot.config2['wrong_reactions'] = wrong_reactions
            embed = discord.Embed(
                color=discord.Colour.green(),
                description="Reactions reset successfully!"
            )
            await context.send(embed = embed)
            update_config(self.bot)
            return
        removed = []
        for reaction in reactions.split():
            try :
                correct_reactions.remove(reaction)
                removed.append(reaction)
            except:
                pass
            try:
                wrong_reactions.remove(reaction)
                removed.append(reaction)
            except:
                pass
        embed = discord.Embed(
            color=discord.Colour.green(),
            description= f"{', '.join(removed)} removed successfully."
        )
        await context.send(embed=embed)
        update_config(self.bot)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot: DiscordBot) -> None:
    global correct_reactions, wrong_reactions, last_member_id, next_number, last_message
    await bot.add_cog(General(bot))

    next_number = bot.config2.get('number', 1)
    last_member_id = bot.config2.get('member', None)
    last_message = bot.config2.get('message', None)
    correct_reactions = bot.config2.get('correct_reactions', ['✅', '☑️'])
    wrong_reactions = bot.config2.get('wrong_reactions', ['❌'])

    @bot.event
    async def on_message(message: discord.Message):
        global last_member_id, next_number, correct_reactions, wrong_reactions, last_message
        if bot.counting_channel_id is None:
            return
        if message.channel.id == bot.counting_channel_id:
            try:
                num = eval(message.content.split()[0])
            except:
                return
            if last_member_id is not None and last_member_id == message.author.id:
                curr_number = next_number - 1
                next_number = 1
                last_member_id = None
                last_message = None
                bot.config2['number'] = 1
                bot.config2['member'] = None
                bot.config2['message'] = None
                for emoji in random.choices(wrong_reactions, k=3):
                    await message.add_reaction(emoji)

                    failrole = message.author.get_role(bot.fail_role_id)
                    if not failrole:
                        failrole = message.guild.get_role(bot.fail_role_id)
                        await message.author.add_roles(failrole)
                        addedrole = f"You got the {failrole.name} role. Enjoy!<:holyhell:1192488575401463889>"
                    else:
                        addedrole = f"You already have the {failrole.name} <:pog_smirk:1192487193017581648>"

                await message.reply(f"{message.author.mention} RUINED IT AT **{curr_number}**!! Tf dude! **You can't count two numbers in a row!** {addedrole}\nStart Over from **1** now.")
                update_config(bot)
                return
                
            if num != next_number:
                if next_number < 3:
                    await message.add_reaction('⚠️')
                    await message.reply(f"Whatcha doin' dude?? <:cmon:1192487266640220230> Next number is **{next_number}** ")
                else:
                    curr_number = next_number - 1
                    next_number = 1
                    last_member_id = None
                    last_message = None
                    bot.config2['member'] = None
                    bot.config2['number'] = 1
                    bot.config2['message'] = None
                    for emoji in random.choices(wrong_reactions, k = 4):
                        await message.add_reaction(emoji)

                    failrole = message.author.get_role(bot.fail_role_id)
                    if not failrole:
                        failrole = message.guild.get_role(bot.fail_role_id)
                        await message.author.add_roles(failrole)
                        addedrole = f"You got the {failrole.name} role. Enjoy!<:holyhell:1192488575401463889>"
                    else:
                        addedrole = f"You already have the {failrole.name} <:pog_smirk:1192487193017581648>"

                    await message.reply(f"{message.author.mention} RUINED IT AT **{curr_number}**!! Tf dude! **Wrong number!** {addedrole}\nStart Over from **1** now.")
                    update_config(bot)
                return
            
            next_number += 1
            last_member_id = message.author.id
            last_message = message.id
            await message.add_reaction(random.choice(correct_reactions))
            bot.config2['number'] = next_number
            bot.config2['member'] = last_member_id
            bot.config2['message'] = message.id
            update_config(bot)
            if next_number >= bot.config2.get('pass_number', 30):
                failrole = message.author.get_role(bot.fail_role_id)
                if failrole:
                    await message.author.remove_roles(failrole)
                    await message.reply(f"GG {message.author.mention}, your failrole has been removed!")

    @bot.event
    async def on_message_delete(message: discord.Message):
        if message.id == last_message:
           await message.channel.send(f"Hey hey!! Whatchu doin <:cmon:1192487266640220230>\n" + \
                                f"{message.author.mention} deleted their number!! Next Number is {next_number}\n" +\
                                f"C'mon man don't play these cheap tricks..they won't work on me <:swag:1192487205042651166>") 