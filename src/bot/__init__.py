from asyncio import sleep
from datetime import datetime
from glob import glob
import os
from discord.ext.commands import AutoShardedBot as BotBase
from discord.ext.commands import (
    CommandNotFound,
    Context,
    BadArgument,
    MissingRequiredArgument,
    CommandOnCooldown,
    ArgumentParsingError,
    BadUnionArgument,
    BadLiteralArgument,
    TooManyArguments,
    UserInputError,
    NotOwner,
    MissingPermissions,
    BotMissingPermissions,
    MissingRole,
)
from discord.errors import HTTPException, Forbidden
from discord import Intents, DMChannel, app_commands, Object as DiscordObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import os
import logging


COGS = [path.split(os.sep)[-1][:-3] for path in glob("./src/cogs/*.py")]
_log = logging.getLogger(__name__)
with open("./src/bot/config.json") as config_file:
    config = json.load(config_file)

OWNER_IDS = config.get("discord").get("owner_ids")
GUILD_IDS = config.get("discord").get("guilds_ids")

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.config = config
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        # database.autosave(self.scheduler)
        super().__init__(
            command_prefix=self.PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    async def setup(self):
        for cog in COGS:
            await self.load_extension(f"src.cogs.{cog}")
            _log.info(f" /src/cogs/{cog}.py setup")

        _log.info("  Cogs Setup")

    def update_db(self):
        pass
        # database.multiexec(
        #     "INSERT OR IGNORE INTO users (UserID) VALUES (?)",
        #     ((member.id,) for member in self.guild.members if not member.bot),
        # )

        # stored_members = database.column("SELECT UserID FROM users")
        # to_remove = []
        # for _id in stored_members:
        #     if not self.guild.get_member(_id):
        #         to_remove.append(_id)

        # database.multiexec(
        #     "DELETE FROM users WHERE UserID = ?", ((id_,) for id_ in to_remove)
        # )

        # database.commit()

    def run(self, version):
        self.VERSION = version

        _log.info("Running Bot...")
        super().run(os.getenv("token"), reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("Bot is still setting up please wait.")

    async def setup_hook(self):
        # Copy global commands to local guild to not wait 20 years for commands to show up
        _log.info("Running Cog Setup...")
        await self.setup()

        for guildid in GUILD_IDS:
            guild = DiscordObject(id=guildid)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_connect(self):
        _log.info("Bot Connected")

    async def on_disconnect(self):
        _log.info("Bot Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if self.ready:
            await self.stdout.send(f"An unhandled error has occured.\n`{err}`")

        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif (
            isinstance(exc, BadArgument)
            or isinstance(exc, ArgumentParsingError)
            or isinstance(exc, BadUnionArgument)
            or isinstance(exc, BadLiteralArgument)
            or isinstance(exc, TooManyArguments)
            or isinstance(exc, UserInputError)
        ):
            await ctx.send(
                f"You inputed an invalid argument, use {self.PREFIX}help to see all the required arguments."
            )

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(
                f"You left out a vital argument, use {self.PREFIX}help to see all the required arguments."
            )

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown for {exc.retry_after:,.2f} more seconds."
            )

        elif (
            isinstance(exc, NotOwner)
            or isinstance(exc, MissingPermissions)
            or isinstance(exc, MissingRole)
        ):
            await ctx.send("You are not authorized to use this command.")

        elif isinstance(exc, HTTPException):
            await ctx.send("I was unable to send the message.")

        elif isinstance(exc, BotMissingPermissions):
            await ctx.send("I do not have permission to do that.")

        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permission to do that.")

            raise exc.original

        else:
            await ctx.send(
                "An unhandled error has occured. If this continue's to happen please report it to parker02311."
            )

        raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(config.get("discord").get("primary_guild"))
            self.stdout = self.get_channel(config.get("discord").get("stdout"))
            # self.logs = self.get_channel(869824566774628402)
            # self.logs2 = self.get_channel(869824586072608778)

            await self.stdout.purge(limit=1000)

            self.update_db()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            await self.stdout.send("`Bot Ready`")
            _log.info("  Bot Ready")

            # meta = self.get_cog("Meta")
            # await meta.set()

        else:
            _log.warn("Bot Reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            if not isinstance(message.channel, DMChannel):
                await self.process_commands(message)


bot = Bot()
