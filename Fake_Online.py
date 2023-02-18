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
import asyncio
import datetime
import logging
import random

from telethon import types, functions
from telethon.tl.types import UpdateUserStatus

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class FakeOnlineMod(loader.Module):
    """Фейковый онлайн"""

    strings = {"name": "FakeOnline"}
    strings_ru = {"_cls_doc": "Фейковый онлайн"}
    last_online = 0         # Последний онлайн (timestamp)
    next_morning = 37000    # Когда проснуться (timestamp)
    next_night = 86300      # Когда лечь спать (timestamp)
    user_online = True      # Онлайн ли пользователь
    online_count = 0        # Подсчет выходов в онлайн
    online_per = 1 * 60     # Выходить в онлайн каждые

    async def client_ready(self, client, db) -> None:
        self.client = client
        self.me = await client.get_me()
        self.uid = self.me.id
        self.chat, _ = await utils.asset_channel(
            client, "[Фейковый онлайн]",
            "Этот чат необходим для работы фейкового онлайна",
            channel=False, silent=True, archive=True
        )

    async def go_online(self, now=None):
        """ Выходим в онлайн """
        if now is None:  # Если не передано время
            now = datetime.datetime.now()  # Создаем новый обьект
        await self.client.send_message(  # Отправляем сообщение в чат
            self.chat, f'<emoji document_id="5818967120213445821">🛡</emoji> <b>Вышли в онлайн</b>\n<emoji document_id='
                       f'"5818865088970362886">❕</emoji> <code>{now.strftime("%H:%M:%S.%f")[:-3]}</code>'
        )
        await self.client(functions.account.UpdateStatusRequest(offline=False))  # Выходим в онлайн ещё раз
        self.last_online = now.timestamp()  # Обновляем время последнего онлайна
        logger.info('Вышли в онлайн через go_online(). '
                    f'last_online = {datetime.datetime.fromtimestamp(self.last_online)}')
        return now  # Возвращаем время

    async def go_offline(self, now=None):
        """ Выходим в оффлайн """
        if now is None:     # Если не передано время
            now = datetime.datetime.now()   # Создаем новый обьект
        await self.client(functions.account.UpdateStatusRequest(offline=True))     # Выходим в оффлайн
        logger.info('Вышли в оффлайн через go_offline(). '
                    f'last_online = {datetime.datetime.fromtimestamp(self.last_online)}')
        return now  # Возвращаем время

    async def fakeonlinecmd(self, message: types.Message):
        """ Проверка работоспособности модуля """
        now = datetime.datetime.now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        text = f'Все работает!\n\n' \
               f'Сейчас фейк-онлайн '
        if self.next_morning < seconds_since_midnight < self.next_night:
            text += 'активен\n'
        else:
            text += 'спит\n'
        text += f'last_online: {self.last_online}\n' \
                f'user_online: {self.user_online}'
        await utils.answer(message, text)

    @loader.loop(interval=5, autostart=True, wait_before=True)
    async def scheduler(self) -> None:
        if self.user_online is True:
            # Если пользователь онлайн - выходим из цикла
            return

        now = datetime.datetime.now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

        if self.next_morning > seconds_since_midnight > self.next_night:
            # Если мы спим – выходим из цикла
            return

        if self.last_online + self.online_per <= now.timestamp():
            # Если время последнего онлайна + промежуток 3 минуты меньше чем время сейчас – выходим в онлайн
            rnd = random.randrange(10)
            if rnd > 2:
                await self.go_online()
                logger.info(f'Скрипт вышел в онлайн с шансом {rnd}. '
                            f'last_online = {datetime.datetime.fromtimestamp(self.last_online)}')
            else:
                self.last_online = now.timestamp() + random.randrange(3500)
                await self.go_offline()
                logger.info(f'Скрипт НЕ вышел в онлайн с шансом {rnd}. '
                            f'last_online = {datetime.datetime.fromtimestamp(self.last_online)}')

    @loader.raw_handler(UpdateUserStatus)
    async def update_handler(self, update: UpdateUserStatus):

        if update.user_id == self.uid and type(update.status) == types.UserStatusOffline:
            # Если пользователь вышел в оффлайн
            self.user_online = False
            await self.go_online()
            logger.info('Пользователь вышел в оффлайн. '
                        f'last_online = {datetime.datetime.fromtimestamp(self.last_online)}')

        elif update.user_id == self.uid and type(update.status) == types.UserStatusOnline:
            # Если пользователь вышел в онлайн
            self.user_online = True
            logger.info('Пользователь вышел в онлайн. '
                        f'last_online = {datetime.datetime.fromtimestamp(self.last_online)}')
