import datetime
from typing import Dict, List
from aiomongo import Collection
from pymongo.results import UpdateResult


class StatsType(dict):
    power: int
    defence: int
    agility: int
    instinct: int
    life: int

    def __init__(self, *args, **kwargs):
        super(StatsType, self).__init__(*args, **kwargs)
        self.__dict__ = self

class ProfileType(dict):
    order: str
    leader: bool
    admin: bool
    power: int
    stats: StatsType
    original: str
    updatetime: datetime.datetime

    def __init__(self, *args, **kwargs):
        super(ProfileType, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.stats = (StatsType(args[0]["stats"]))


class UserType(dict):
    """
    Объект для Пользователя
    """

    _id: int
    name: str
    ban: bool
    profile: ProfileType

    def __init__(self, *args, **kwargs):
        super(UserType, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.profile = (ProfileType(args[0]["profile"]))

    def updatedb(self, db: Collection):
        self._db = db

    async def save(self) -> UpdateResult:
        """
        Перезаписывает документ пользователя по айди
        """
        db = self._db
        del self["_db"]
        Result = await db.replace_one({"_id": self._id}, self, True)
        self._db = db
        return Result


class ChatType(dict):
    _id: int
    order: str
    currentpin: str
    datepin: datetime.datetime

    def __init__(self, *args, **kwargs):
        super(ChatType, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def updatedb(self, db: Collection):
        self._db = db

    async def save(self) -> UpdateResult:
        """
        Перезаписывает документ чата по айди
        """
        db = self._db
        del self["_db"]
        Result = await db.replace_one({"_id": self._id}, self, True)
        self._db = db
        return Result


class Battle(dict):
    _id: datetime.datetime
    targets: Dict[str, Dict[str, List[int]]]

    def __init__(self, *args, **kwargs):
        super(Battle, self).__init__(*args, **kwargs)
        self.__dict__ = self


clear_user_type = {"_id": None, "name": None, "ban": False, "profile": {"order": None, "leader": False, "admin": False, "power": 0,
              "original": None, "updatetime": datetime.datetime.fromtimestamp(0), "stats": {"power": 0, "defence": 0,
              "agility": 0, "instinct": 0, "life": 0}}}

clear_chat_type = {"_id": None, "order": None, "currentpin": r"¯\_(ツ)_/¯", "datepin": datetime.datetime.fromtimestamp(0)}
