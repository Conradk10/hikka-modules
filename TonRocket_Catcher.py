__version__ = (0, 0, 8)
#
#     d88P     d88P          888b    888          888
#      d88P   d88P           8888b   888          888
#       d88P d88P            88888b  888          888
#        d88888P    888888   888Y88b 888  .d88b.  888888
#        d88888P    888888   888 Y88b888 d8P  Y8b 888
#       d88P d88P            888  Y88888 88888888 888
#      d88P   d88P           888   Y8888 Y8b.     Y88b.
#     d88P     d88P          88.8    Y888  "Y8888   "Y888
#
#                      © Copyright 2022
#                    https:// x-net.pp.ua
#
#                 Licensed under the GNU GPLv3
#          https:// www.gnu.org/licenses/agpl-3.0.html
#

# meta developer: @zxcghost666
# requires: tgchequeman==0.0.8

import logging
import re

from telethon import types
from telethon.tl.patched import Message as mmmm
from tgchequeman import exceptions, activate_multicheque, parse_url

from .. import loader, utils
from ..tl_cache import CustomTelegramClient

logger = logging.getLogger(__name__)


@loader.tds
class TonRocketCatcherMod(loader.Module):
    """TonRocket-Catcher"""

    strings = {"name": "TonRocket-Catcher"}
    strings_ru = {"_cls_doc": "TonRocket-Catcher"}
    tonrocketbot_id = 5014831088
    patterns = {
        "receive": r"Receive|Получить",
        "url": r"https://t\.me/tonRocketBot\?start=[^\s]+",
    }

    async def client_ready(self, client, db) -> None:
        self.client: CustomTelegramClient = client

    async def trcinfocmd(self, message: types.Message):
        """ Проверка работоспособности модуля """
        await utils.answer(message, "Все работает!")

    async def activate(self, url: dict):
        try:
            await activate_multicheque(self.client, url, '')
        except (exceptions.ChequeFullyActivatedOrNotFound, exceptions.PasswordError) as err:
            logger.error(err)
        except (exceptions.ChequeActivated,
                exceptions.ChequeForPremiumUsersOnly,
                exceptions.CannotActivateOwnCheque) as warn:
            logger.warning(warn)
            return
        except exceptions.UnknownError as err:
            logger.error(err)
            return
        except exceptions.Success:
            return
        except Exception as err:
            logger.error(err)

    async def watcher(self, message: types.Message) -> None:
        # Если сообщение от имени @TonRocketBot
        if not isinstance(message, mmmm):
            return
        if message.from_id in [self.tonrocketbot_id]:
            return
        if message.via_bot_id in [self.tonrocketbot_id]:
            for row in message.reply_markup.rows:
                for button in row.buttons:
                    if re.search(self.patterns['receive'], button.text):
                        url = parse_url(button.url)
                        await self.activate(url)

        elif message.message and re.search(self.patterns['url'], message.message):
            link_match = re.search(self.patterns['url'], message.message)
            url = parse_url(link_match.group())
            await self.activate(url)
