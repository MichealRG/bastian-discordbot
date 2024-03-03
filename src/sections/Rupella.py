import random

from discord import slash_command
from discord.ext import commands

from src.const.paths import LOCAL_LOGS_RUPELLA_BLACKLIST_PATH, WISE_QUOTES_PATH
from src.helpers.constants import LEGIT_SERVERS
from src.services.config import Config
from src.services.general_utils import write_to_actions_logs, read_json_file, role_and_channel_valid, reset_localLogs_file
from src.services.translation import Translation


class RupellaGuard(commands.Cog):
    def __init__(self, config, translation, roles, channels, admin_roles, admins_channels):
        self.config = config or Config()
        self.translation = translation or Translation()
        self.channels = channels
        self.admin_channels = admins_channels
        self.admin_channels_ids = [channel.id for channel in admins_channels]
        self.allowed_channels_ids = [channel.id for channel in channels]
        self.allowed_role_ids = roles
        self.bel_shelorin_quotes = read_json_file(WISE_QUOTES_PATH)
        self.admins_roles = admin_roles

    async def rupella_actions_check(self, message):
        message_content = message.content.lower().strip()

        if message_content == "!rupella" or message_content == "/rupella":
            what_are_u_doing_here = self.translation.translate("ACTIONS.RUPELLA.SURPRISED")

            await message.reply(f"**Rupella**:\n{what_are_u_doing_here}")

            self.__write_on_rupella_blacklist(message.author.id)

    def __write_on_rupella_blacklist(self, id: str):
        write_to_actions_logs("rupella-blacklist.txt", id)

    @slash_command(name="cytat", guild_ids=LEGIT_SERVERS, description="Poproś o cytat")
    async def display_available_player(self, ctx):
        if role_and_channel_valid({
            "author_roles": ctx.author.roles,
            "channel_source": ctx.channel.id,
            "allowed_roles":  self.allowed_role_ids,
            "allowed_channel_ids": self.allowed_channels_ids
        }):
            description_of_elven = self.translation.translate("ACTIONS.RUPELLA.ELVEN.DESCRIPTION")
            introduction_of_elven = self.translation.translate("ACTIONS.RUPELLA.ELVEN.INTRODUCTION")

            quote = random.choice(self.bel_shelorin_quotes).get("quote", "Twoje życie staje się lepsze tylko wtedy, gdy stajesz się lepszym człowiekiem.")

            await ctx.respond(f"**Głos z Eteru:**\n{description_of_elven}\n\n**Bel-Sherhorin Mądry:**\n{introduction_of_elven}\n\n***{quote}***")

    @slash_command(name="reset-rupella-status", guild_ids=LEGIT_SERVERS,
                   description="[Admin command]: reset status for Rupella")
    async def rest_rupella_stats(self, ctx):
        data = {
            "author_roles": ctx.author.roles,
            "channel_source": ctx.channel.id,
            "allowed_roles": self.admins_roles,
            "allowed_channel_ids": self.admin_channels_ids
        }

        if role_and_channel_valid(data):
            reset_localLogs_file(LOCAL_LOGS_RUPELLA_BLACKLIST_PATH)

            success_translation = self.translation.translate("ADMINS.RESET_BOTS_SUCCESSFULLY_PASSED")
            await ctx.respond(f"**Głos z Eteru**:\n{success_translation}")