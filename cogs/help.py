import discord
import difflib
from discord.ext import commands
from bot import ChezziBot
from utils import reply


async def help_help(ctx: commands.Context):
    emb = discord.Embed(
        title="Command help",
        description="View help and how to use commands",
        color=discord.Color.blue()
    )

    # help usage
    emb.add_field(
        name="Usage",
        value=(
            "help                   : view all modules\n"
            "help `module`          : view all commands from a module\n"
            "help `module` `command`: view usage of a command\n"
            "Special case: help help will view this message\n"
        ),
        inline=False
    )

    # How to use commands
    emb.add_field(
        name="How to use commands",
        value=(
            "A prefix or bot mention indicates the sent message is a command\n"
            "**Usages:**\n"
            "<prefix><command> <param1> <param2> ...\n"
            "<bot mention> <command> <param1> <param2> ...\n"
            "**Examples:**\n"
            "t.help games\n"
            "`@ChezziBot` help games sokoban\n"
            "Some commands are marked as \"flag\", meaning users have to specify flags themselves\n"
            "Eg: \"t.ban member: `@DeezNuts` reason: being nuts\"\n"
            "This approach makes it more user-friendly but specifying flags is obligatory\n"
            "The default prefix is \"t.\"\n"
            "Changing the prefix might be possible in the future (as the owner was lazy to set up a database)\n"
        ),
        inline=False
    )

    # parameter
    emb.add_field(
        name="Types of parameter",
        value=(
            "`int`          : integer (ranging from -(2^31) to 2^31 - 1)\n"
            "`str`          : string (could be anything that you typed, or type of Any)\n"
            "`bool`         : true or false (could be either 1 or 0, true or false, t or f)\n"
            "`Member`       : a server member (could either mention or use member's id)\n"
            "`User`         : a discord user (could either mention or use user's id)\n"
            "`TextChannel`  : a server textable channel (could either mention or use channel's id)\n"
            "`Role`         : a server role (could either mention or use role's id)\n"
        ),
        inline=False
    )

    # options
    emb.add_field(
        name="Parameter options",
        value=(
            "`Optional[T]`              : `T` is optional (you could pass an corresponding argument or not)\n"
            "`Union[T, V]` or `T | V`   : the type could be either `T` or `V`\n"
            "`List[T]`                  : accept unlimited arguments of type `T`\n"
            "where `T` and `V` represent some types\n"
        ),
        inline=False
    )

    # note about parameter
    emb.add_field(
        name="*NOTES*",
        value=(
            "Default delimeter is \" \" (whitespace). If you want to pass many words as a single argument "
            "you will have to put them between quotes (string type only)\n"
            "Eg: <command> <name: str>\n"
            "If you use <command> Deez Nuts, \"Deez\" will be used for <name>\n"
            "If you use <command> \"Deez Nuts\", \"Deez Nuts\" will be used for <name>\n"
            "If you use commands using flags, no quotes are required"
        ),
        inline=False
    )

    emb.set_footer(text=f"Requested by {ctx.author}")

    await reply(ctx.message, embed=emb)


class Help(commands.Cog, description="View help command"):
    def __init__(self, bot: ChezziBot):
        self.bot = bot
        self.visible = False

    @commands.command()
    async def help(self, ctx: commands.Context, *inp: str):
        # General attribute for help embed
        emb = discord.Embed(color=discord.Color.green())
        emb.set_footer(text=f"Requested by {ctx.author}")

        match len(inp):
            # Show all modules
            case 0:
                emb.title = "MODULES"

                for module, cog in self.bot.cogs.items():
                    if hasattr(cog, "visible") and cog.visible:
                        emb.add_field(
                            name=module.capitalize(),
                            value=f"{cog.description}\n{len(cog.get_commands())} commands",
                            inline=False
                        )

                emb.description = f"Containing {len(emb.fields)} modules in total"

                await reply(ctx.message, embed=emb)
                return

            # Show a specific module
            case 1:
                module = inp[0].capitalize()

                if module == "Help":
                    return await help_help(ctx)

                cog = self.bot.cogs.get(module)

                # Module not found
                if cog is None or not (hasattr(cog, "visible") and cog.visible):
                    closest_match = difflib.get_close_matches(
                        module, self.bot.cogs.keys(), n=1, cutoff=0)[0]

                    emb.title = "Module Not Found"
                    emb.description = f"Module \"{module}\" does not exist. Did you mean \"{closest_match}\"?"
                    emb.color = discord.Color.red()

                    await reply(ctx.message, embed=emb)
                    return

                emb.add_field(
                    name="All commands",
                    value=", ".join(
                        f"`{cmd.name}`" for cmd in cog.get_commands()),
                    inline=False
                )

                await reply(ctx.message, embed=emb)

            # Show a specific command in a module
            case 2:
                module, command = inp
                module, command = module.capitalize(), command.lower()

                cog = self.bot.cogs.get(module)

                # Module not found
                if cog is None or not (hasattr(cog, "visible") and cog.visible):

                    closest_match = difflib.get_close_matches(
                        module, self.bot.cogs.keys(), n=1, cutoff=0)[0]

                    emb.title = "Module Not Found"
                    emb.description = f"Module \"{module}\" does not exist. Did you mean \"{closest_match}\"?"
                    emb.color = discord.Color.red()

                    await reply(ctx.message, embed=emb)
                    return

                cmds = cog.get_commands()
                for cmd in cmds:
                    if cmd.name == command or command in cmd.aliases:
                        command = cmd
                        break
                else:  # Not found command
                    closest_match = difflib.get_close_matches(
                        command, cmds, n=1, cutoff=0)[0]
                    emb.title = "Command Not Found"
                    emb.description = f"Command \"{command}\" does not exist. Did you mean \"{closest_match}\"?"
                    emb.color = discord.Color.red()

                    await reply(ctx.message, embed=emb)
                    return

                emb.title = f"Command {command.name}"
                emb.description = command.help
                await reply(ctx.message, embed=emb)
                return

            # wtf
            case _:
                emb.title = "Number of arguments exceeded"
                emb.description = "Please use `help help` to see the help command usage"
                emb.color = discord.Color.red()

                await reply(ctx.message, embed=emb)
                return


async def setup(bot):
    await bot.add_cog(Help(bot))
