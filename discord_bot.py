import discord
from discord.ext import commands, tasks
import randfacts
import youtube_dl
import nacl
import asyncio
import os
from dotenv import load_dotenv


class CustomHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.no_category = None  # Set to None to remove the "No category" section
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        embed = discord.Embed(
            title="RileyBot 😍",
            description="This is RileyBot, your personal bot for all your discord needs! 😂.\n"\
                "A full list of commands are given below under **RileyBot Commands**.\n"\
                "To query a command, enter **!help [command]**."\
                ,
            color=discord.Color.blue()
        )

        for cog, commands in mapping.items():
            if cog is None:
                continue

            # Customize the category name here (e.g., remove 'Cog')
            category_name = cog.__class__.__name__.replace("Cog", "")

            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                embed.add_field(name=category_name, value="\n".join(command_signatures), inline=False)

        # Add a list of all available commands
        all_commands = bot.commands
        command_list = "\n".join([self.get_command_signature(c) for c in all_commands])
        if command_list:
            embed.add_field(name="RileyBot Commands", value=command_list, inline=False)

        await ctx.send(embed=embed)

class DiscordBot:

    def __init__(self) -> None:
        # Private token member
        load_dotenv()
        self.__discord_token = os.getenv("DISCORD_TOKEN")
        
        # Define the intents your bot needs
        intents = discord.Intents.default()

        # Enable the ability to read message content
        intents.message_content = True 

        # Setting the commands & default command data
        self.__bot = commands.Bot(
            command_prefix = commands.when_mentioned_or('!'), 
            intents=intents, 
            help_command = CustomHelpCommand()
        ) 

        # Voting System
        self.total_votes = 0
        self.options_arr = []
        self.votes_arr = []
        self.vote_display = ""
        self.vote_won = False

        @self.__bot.event
        async def on_ready():
            print(f'We have logged in as {self.__bot.user.name}')

        @self.__bot.event
        async def on_member_update(before, after):
            if before.status != after.status and after.status == discord.Status.online:
                # User came online
                print(f'{after.display_name} is now online')

        @self.__bot.event
        async def on_message(message):
            if message.author == self.__bot.user:
                return

            await self.__bot.process_commands(message)

        @self.__bot.command()
        async def funfact(ctx):
            """Sends a random fun fact."""
            await ctx.send(randfacts.get_fact())
        
        @self.__bot.command()
        async def vote(ctx, *args):

            if not args:
                embed = discord.Embed(
                    title="Voting System",
                    description="Invalid Voting System usage.\n",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return


            # Check if vote has won, if so reset
            if self.vote_won is True:
                self.total_votes = 0
                self.options_arr = []
                self.votes_arr = []
                self.vote_display = ""
                self.vote_won = False

            # Count the args
            args_count = 0
            for _ in args:
                args_count += 1

            # Initialise Vote count array
            self.votes_arr = [0] * args_count

            # Total users in channel
            online_members = [member for member in ctx.guild.members]

            self.total_votes = len(online_members)

            for idx, arg in enumerate(args):
                self.vote_display += "**{}** ({}/{})\n".format(arg, self.votes_arr[idx], self.total_votes)
                self.options_arr.append(arg)

            embed = discord.Embed(
                title="Voting System",
                description=self.vote_display,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

        @self.__bot.command()
        async def cast(ctx, vote):
            if not vote:
                embed = discord.Embed(
                    title="Voting System",
                    description="Invalid Cast usage.\n",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            # Voting system is closed
            if self.vote_won is True:
                embed = discord.Embed(
                    title="Voting System",
                    description="The Voting System is closed.\n",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return  

            # Print invalid vote
            elif vote not in self.options_arr:
                embed = discord.Embed(
                    title="Voting System",
                    description="Invalid voting option.\n",
                    color=discord.Color.red()
                )  
                await ctx.send(embed=embed)
                return

            # Check for winners/ Adding votes
            for idx, option in enumerate(self.options_arr):
                # Update vote count for match
                if vote == option:
                    self.votes_arr[idx] += 1

                if self.votes_arr[idx] ==  self.total_votes:
                    embed = discord.Embed(
                        title="Voting System",
                        description="Winner is **{}**\n".format(option),
                        color=discord.Color.purple()
                    )
                    await ctx.send(embed=embed)
                    self.vote_won = True
                    return
                
            for idx, arg in enumerate(self.options_arr):
                self.vote_display += "**{}** ({}/{})\n".format(arg, self.votes_arr[idx], self.total_votes)

            # Create Embedded print to terminal
            embed = discord.Embed(
                title="Voting System",
                description=self.vote_display,
                color=discord.Color.blue()
            )
            self.vote_display = ""
            await ctx.send(embed=embed)

        @self.__bot.event
        async def on_voice_state_update(member, before, after):
            if before.channel is None and after.channel is not None:
                # Member joined a voice channel
                guild = member.guild
                channel = discord.utils.get(guild.text_channels, name="general")
                if channel is not None:
                    await channel.send(f'{member.mention} has joined the Voice Chat!')

            elif before.channel is not None and after.channel is None:
                # Member left a voice channel
                guild = member.guild
                channel = discord.utils.get(guild.text_channels, name="general")
                if channel is not None:
                    await channel.send(f'{member.mention} has left the Voice Chat!')
        


    def run_bot(self):
        self.__bot.run(self.__discord_token)

if __name__ == "__main__":
    bot = DiscordBot()
    bot.run_bot()


