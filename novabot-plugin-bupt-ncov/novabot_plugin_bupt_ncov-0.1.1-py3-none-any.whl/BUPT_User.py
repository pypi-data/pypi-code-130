import base64
import json
import re
from http.cookies import SimpleCookie, Morsel
from typing import Union, AnyStr, Optional, TypeVar, List, Callable, Set

import pymongo
from aiohttp import ClientSession
from nonebot import get_driver

from novabot.core import get_firefox_browser
from novabot.core.crypto import QQ_AES
from novabot.core.db import DB
from .exceptions import LoginFailedException, CheckinError
from .model import BUPT_Model, New_Form_Model, Report_Form_Model, Geo_Info, Report_Response
from .model import INDEX_URL, LOGIN_URL, REPORT_URL, REPORT_POST_URL

T = TypeVar('T')
sessions: List[ClientSession] = []

BUPT_ncov_MongoDB = DB['BUPT_ncov']
BUPT_ncov_MongoDB.create_index([("user", pymongo.TEXT)])
driver = get_driver()


def session_required(func: Callable) -> T:
    async def wrapper(self, *args, **kwargs) -> T:
        if not self.session:
            self.session = await self.get_session()
        return await func(self, *args, **kwargs)

    return wrapper


def login_required(func: Callable) -> T:
    async def wrapper(self, *args, **kwargs) -> T:
        if not await self.check_available() and not await self.do_login():
            raise LoginFailedException("Login Failed!")
        return await func(self, *args, **kwargs)

    return wrapper


class BUPT_User:
    user: int
    data: BUPT_Model
    session: Optional[ClientSession]

    def __init__(self, user: Union[str, int]):
        self.user = user if isinstance(user, int) else int(user)
        self.data = self.get_user()
        self.session = None

    @staticmethod
    async def get_browser():
        return await get_firefox_browser()

    async def get_session(self):
        if not self.session:
            self.session = ClientSession()
            sessions.append(self.session)
        return self.session

    def create_or_update(self,
                         *,
                         account: str = None,
                         password: str = None,
                         cookie: str = None,
                         check_in_time: str = "00:01",
                         check_in_status: bool = True) -> BUPT_Model:
        kwargs = locals().copy()
        kwargs.pop('self')
        user_: BUPT_Model = self.get_user().copy(update={k: v for k, v in kwargs.items() if v})
        if cookie == 'None':
            user_.cookie = None
        if len(split_check_time := check_in_time.split(':')) != 2 \
                or not split_check_time[0].isdigit() \
                or not split_check_time[1].isdigit() \
                or not 0 <= int(split_check_time[0]) <= 24 \
                or not 0 <= int(split_check_time[1]) <= 60:
            raise ValueError(f"Check in time {check_in_time} is invalid!")
        BUPT_ncov_MongoDB.update_one({'user': self.user},
                                     {'$set': user_.__dict__},
                                     upsert=True)
        self.data = user_
        return user_

    def update(self):
        BUPT_ncov_MongoDB.update_one({'user': self.user},
                                     {'$set': self.data.__dict__},
                                     upsert=True)

    def get_user(self) -> BUPT_Model:
        user_ = BUPT_ncov_MongoDB.find_one({'user': self.user})
        if not user_:
            return BUPT_Model.parse_obj({"user": self.user})
        return BUPT_Model.parse_obj(user_)

    def remove_user(self) -> bool:
        return bool(BUPT_ncov_MongoDB.delete_one({'user': self.user}))

    @property
    def _password(self):
        if self.data.password is None:
            return None
        return self.decrypt(self.data.password, convert=True)

    @property
    def _cookie(self):
        if self.data.cookie is None:
            return None
        return self.decrypt(self.data.cookie, convert=True)

    def encrypt(self, content: AnyStr) -> str:
        if isinstance(content, str):
            content = content.encode()
        return base64.b64encode(QQ_AES(self.user).encrypt(content)).decode()

    def decrypt(self, content: str, convert: bool = True) -> AnyStr:
        """

        :param content:
        :param convert: Covert bytes to str?
        :return:
        """
        result = QQ_AES(self.user).decrypt(base64.b64decode(content))
        return result.decode() if convert else result

    @session_required
    async def check_available(self) -> bool:
        async with self.session.get(INDEX_URL) as resp:
            result = 'realname' in (await resp.text(encoding='utf-8'))
        return result

    @session_required
    async def do_login(self) -> bool:
        if (not self.data.cookie) and (not self.data.account and self.data.password):
            raise ValueError("You should set Account and Password or Cookie before login!")
        if self.data.cookie:
            self.session.cookie_jar.update_cookies(SimpleCookie(self._cookie))
            if await self.check_available():
                return True
        if not self.data.account and self.data.password:
            raise ValueError("Cookie is expired or invalid! Please set Account and Password or Cookie again!")
        data = {
            'username': self.data.account,
            'password': self._password,
            '_eventId': "submit",
            'submit': "登录",
            'type': "username_password"
        }
        async with self.session.get(LOGIN_URL) as resp:
            text = await resp.text()
            r = re.search(r'<input name="execution" value="([a-zA-Z0-9\-_=]+?)"/>', text)
            if r and len(r.groups()) >= 1:
                execution = r[1]
                data['execution'] = execution
            else:
                raise ValueError(f"No Execution Found in {LOGIN_URL}!")
        async with self.session.post(LOGIN_URL, data=data, allow_redirects=False) as resp:
            if resp.status == 302:
                cookie: Optional[Morsel] = resp.cookies.get('CASTGC', None)
                if cookie:
                    self.data.cookie = self.encrypt(cookie.OutputString())
                    self.update()
        result = await self.check_available()
        return result

    @session_required
    @login_required
    async def get_daily_report_data(self) -> Report_Form_Model:
        async with self.session.get(REPORT_URL) as resp:
            text = await resp.text()
            r = re.search(r'var def = (\{.+\});', text)
            if not r or len(r.groups()) < 1:
                raise ValueError("No report data found!")
            new_form = New_Form_Model.parse_obj(json.loads(r[1]))  # 获取今日数据

            r = re.search(r'oldInfo: (\{.+\}),', text)
            if not r or len(r.groups()) < 1:
                raise ValueError("No report data found!")
            old_form = Report_Form_Model.parse_obj(json.loads(r[1]))
            geo = json.loads(old_form.geo_api_info)  # 获取地理数据

            province = geo['addressComponent']['province']
            city = province if province in ["北京市", "上海市", "重庆市", "天津市"] else geo['addressComponent']['city']
            area = " ".join([province, city, geo['addressComponent']['district']])
            address = geo['formattedAddress']
            geo_info = Geo_Info(city=city, area=area, province=province, address=address)

            return old_form.copy(update=new_form.dict(exclude_unset=True)). \
                copy(update=geo_info.dict(exclude_unset=True))  # 更新生成今日数据

    @session_required
    @login_required
    async def post_report_data(self, data: Report_Form_Model) -> str:
        async with self.session.post(REPORT_POST_URL, data=data.dict(exclude_unset=True)) as resp:
            if resp.status != 200:
                raise ConnectionError(f"Status Code {resp.status}")
            result = Report_Response.parse_obj(await resp.json())
            if result.e:
                raise CheckinError(f"{result.m}")
            return result.m

    async def check_in(self) -> str:

        try:
            data = await self.get_daily_report_data()
            # await asyncio.sleep(random.randint(2, 6))  # IDK Why but in case
            result = await self.post_report_data(data)
            return "---- 填报成功 ----\n" \
                   f"今日填报结果: {result}\n" \
                   f"上次填报时间: {data.date}\n" \
                   f"上次填报地点: {data.area}"
        except (LoginFailedException, ValueError) as e:
            return "---- 填报失败 ----\n" \
                   f"错误原因: {type(e)} {e}\n" \
                   f"请检查是否设置了错误的帐号密码或Cookie\n" \
                   f"如果你是第一次使用, 请使用 `ncov add` 添加一个新的账户\n" \
                   f"详细帮助可使用 `ncov help` 查看"
        except ConnectionError as e:
            return "---- 填报失败 ----\n" \
                   f"错误原因: {type(e)} {e}\n" \
                   f"可能是网络问题或者服务器问题"
        except Exception as e:
            return "---- 填报失败 ----\n" \
                   f"错误原因: {type(e)} {e}\n"

    async def close_session(self):
        if self.session:
            sessions.remove(self.session)
            await self.session.close()


class BUPT_ncov_DB:

    @staticmethod
    def get_time_set() -> Set[str]:
        times = set()
        for i in BUPT_ncov_MongoDB.find():
            item = BUPT_Model.parse_obj(i)
            if item.check_in_time:
                times.add(item.check_in_time)
        return times

    @staticmethod
    def get_user_set() -> Set[int]:
        users = set()
        for i in BUPT_ncov_MongoDB.find():
            item = BUPT_Model.parse_obj(i)
            if item.user:
                users.add(item.user)
        return users

    @staticmethod
    def get_all() -> List[BUPT_Model]:
        return [BUPT_Model.parse_obj(i) for i in BUPT_ncov_MongoDB.find()]


@driver.on_shutdown
async def close_sessions():
    for session in sessions:
        await session.close()
