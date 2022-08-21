from nonebot.adapters.onebot.v11 import Bot, ActionFailed


async def get_qq_nickname_with_group(bot: Bot, user_id: int, current_group_id: int, target_group_id: int = None) -> str:
    if target_group_id is None:
        target_group_id = current_group_id
    if target_group_id != current_group_id:
        info = await bot.get_stranger_info(user_id=user_id)
        return info['nickname']
    try:
        info = await bot.get_group_member_info(group_id=current_group_id, user_id=user_id)
    except ActionFailed as exc:
        if exc.info['retcode'] == 100:
            info = await bot.get_stranger_info(user_id=user_id)
    return info['nickname']
