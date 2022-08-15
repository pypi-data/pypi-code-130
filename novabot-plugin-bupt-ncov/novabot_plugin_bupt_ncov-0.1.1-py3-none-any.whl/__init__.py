from collections import defaultdict
from typing import Dict, List, Union

from nonebot import get_driver, get_bot, on_shell_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.log import logger
from nonebot.params import ShellCommandArgs
from nonebot.rule import Namespace, ParserExit
from nonebot_plugin_apscheduler import scheduler

from .BUPT_User import BUPT_ncov_DB, BUPT_User
from .parser import ncov_parser

checkin: Dict[str, List[int]] = defaultdict(list)
driver = get_driver()

checker = on_shell_command("ncov", parser=ncov_parser)


@checker.handle()
async def _(event: PrivateMessageEvent, args: Union[Namespace, ParserExit] = ShellCommandArgs()):
    """
    args.cmd:
        None: Check_in
        add: Add Check_in User
        remove: Remove Check_in User
        modify: Modify Check_in User
    """
    if isinstance(args, ParserExit):
        await checker.finish(args.message)
        return

    user = BUPT_User(event.sender.user_id)
    try:
        if args.cmd is None:
            result = await user.check_in()

        elif args.cmd == 'add':
            user.remove_user()
            user.create_or_update(account=args.user,
                                  password=user.encrypt(args.password),
                                  check_in_time=args.time)
            await user.do_login()
            result = "---- 添加用户 ----\n" \
                     f"帐号: {user.data.account}\n" \
                     f"签到时间: {user.data.check_in_time}\n\n" \
                     f"登录状态: {await user.check_available()}"
            await initialize_bupt_ncov_scheduler()

        elif args.cmd == 'remove':
            result = "---- 删除用户 ----\n" \
                     f"结果: {user.remove_user()}"
            await initialize_bupt_ncov_scheduler()

        elif args.cmd == 'modify':
            status = args.status != 'disable'
            user.create_or_update(account=args.user,
                                  password=user.encrypt(args.password) if args.password else None,
                                  check_in_time=args.time,
                                  check_in_status=status,
                                  cookie='None')
            await user.do_login()
            result = "---- 修改用户 ----\n" \
                     f"帐号: {user.data.account}\n" \
                     f"签到时间: {user.data.check_in_time}\n" \
                     f"签到状态: {user.data.check_in_status}\n\n" \
                     f"登录状态: {await user.check_available()}"
            await initialize_bupt_ncov_scheduler()

        elif args.cmd == 'list':
            await user.do_login()
            result = "---- 用户状态 ----\n" \
                     f"帐号: {user.data.account}\n" \
                     f"签到时间: {user.data.check_in_time}\n" \
                     f"签到状态: {user.data.check_in_status}\n\n" \
                     f"登录状态: {await user.check_available()}"

        else:
            result = "---- nCovError ----\n" \
                     f"错误的请求参数 {str(args)}"
    except Exception as e:
        result = "---- nCovError ----\n" \
                 f"{type(e)} {e}"

    await checker.finish(result)


async def do_checkin(time: str):
    logger.info("Prepare to Check in ...")
    for user in checkin[time]:
        user_ = BUPT_User(user)
        result = await user_.check_in() + f"\n\n    -- 自动签到 Working on {time} for user {user}"
        await get_bot().call_api('send_msg', user_id=user, message=result)


@driver.on_startup
async def initialize_bupt_ncov_scheduler():
    logger.info("Handling BUPT ncov users...")
    users = BUPT_ncov_DB.get_all()
    times = set(map(lambda x: x.check_in_time, users))
    global checkin
    checkin = defaultdict(list)
    for job in scheduler.get_jobs():
        if job.name.startswith('BUPT_checkin_'):
            scheduler.remove_job(job.id)
    for time in times:
        checkin[time] = list(map(lambda x: x.user, filter(lambda x: x.check_in_time == time, users)))
        scheduler.add_job(do_checkin,
                          "cron",
                          hour=time.split(':')[0],
                          minute=time.split(':')[1],
                          second=0,
                          name=f"BUPT_checkin_{time}",
                          args=[time])
