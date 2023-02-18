__version__ = (1, 0, 0)
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
# scope: hikka_only
# scope: hikka_min 1.2.10

import openai
import logging

from telethon import types

from .. import loader, utils

logger = logging.getLogger(__name__)
openai.api_key = "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"
model_engine = "text-davinci-003"


@loader.tds
class OpenAIChatGPTMod(loader.Module):
    """OpenAIChatGPT"""

    strings = {"name": "OpenAIChatGPT"}
    strings_ru = {"_cls_doc": "OpenAIChatGPT"}

    users = [121020442, 1496429325]

    async def client_ready(self, client, db) -> None:
        self.client = client

    async def chatgptcmd(self, message: types.Message):
        """ Проверка работоспособности модуля """
        await utils.answer(message, "Все работает!")

    async def watcher(self, message: types.Message) -> None:
        try:
            if not message.message or message.from_id not in self.users:
                return
        except Exception as err:
            print(err)
            return

        prompt = message.message

        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response = completion.choices[0].text

        await utils.answer(message, response)
