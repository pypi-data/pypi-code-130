from typing import Optional

from RCC.types.rcc_player import RCCPlayer
from RCC.types.response import RCCResponse
from RCC.api.abc import ABCAPI
from RCC.exceptions import ReasonLenError


class APIMethods(ABCAPI):
    async def start_check(
        self,
        player_steamid: int,
        moder_steamid: Optional[int] = None,
    ) -> RCCResponse:
        """Выдает доступ к чекеру на 30 минут.

        Args:
            player_steamid: int - стимайди игрока, которому нужно выдать доступ
            moder_steamid: Optional[int] - стимайди модератора, кому засчитать эту проверку.
                Если не указано или модератора нету в списке, проверка будет засчитана серверу
        Return:
            Ответ от чекера со статусом ответа и с ошибкой, если она произошла
        """
        params = {"player": player_steamid, "moder": moder_steamid}
        response = await self.api_instance.request("addPlayer", params)
        model = RCCResponse
        return model(**response)

    async def get_info(self, player_steamid: int) -> RCCPlayer:
        """Выводит всю информацию об игроке из чекера.

        Более подробная схема находится https://rustcheatcheck.ru/panel/getapi.
        Все значения записы в снейк_кейсе, также некоторые поля были названы более правильно(на мой взгляд),
        но все примитивно понятно, любой редактор подскажет.

        Args:
            player_steamid: int - стимайди игрока, чью информацию нужно получить

        Return:
            Возвращает экземпляр модели RCCPlayer

        Example:
        >>> player = await RCC.get_info(76561198021247080)
        >>> player.rcc_checks  # 7
        >>> bans = player.bans
        >>> bans[0].reason  # мамкин_крашер
        >>> bans[0].active  # False
        >>> bans[0].ban_date  # datetime.datetime(2019, 6, 11, 12, 1, 7, tzinfo=datetime.timezone.utc)
        >>> checks = player.checks
        >>> checks[1].time  # datetime.datetime(2019, 1, 8, 16, 53, 13, tzinfo=datetime.timezone.utc)
        >>> checks[1].server_name  # MagicRust
        """
        params = {"player": player_steamid}
        response = await self.api_instance.request("getInfo", data=params)
        model = RCCPlayer
        return model(**response)

    async def ban_player(self, player_steamid: int, reason: str) -> RCCResponse:
        """Добавляет бан в панель чекера.

        Args:
            player_steamid: int - стимайди игрока, которому нужно добавить бан
            reason: str - причина добавления бана

        Raises:
            ReasonLenError - Если длина причины бана превышает 60 символов

        Return:
            Ответ от чекера со статусом ответа и с ошибкой, если она произошла
        """
        if len(reason) > 60:
            raise ReasonLenError("Длина причины бана превышает 60 символов")
        params = {"player": player_steamid, "reason": reason}
        response = await self.api_instance.request("addBan", data=params)
        model = RCCResponse
        return model(**response)

    async def unban_player(self, player_steamid: int) -> RCCResponse:
        """Убирает бан из панели чекера.

        Args:
            player_steamid: int - Стимайди игрока, с которого нужно снять бан
        Return:
            Ответ от чекера со статусом ответа и с ошибкой, если она произошла
        """
        params = {"player": player_steamid}
        response = await self.api_instance.request("removeBan", data=params)
        model = RCCResponse
        return model(**response)
