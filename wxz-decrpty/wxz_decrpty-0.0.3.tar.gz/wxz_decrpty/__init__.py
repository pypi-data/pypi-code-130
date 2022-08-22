"""微信解密相关"""
from ctypes import c_int32, windll, byref, create_string_buffer
from os import path
from re import search
from winreg import OpenKey, HKEY_CURRENT_USER, QueryValueEx
from win32api import CloseHandle, OpenProcess
from win32con import PROCESS_ALL_ACCESS
from win32process import (
    EnumProcessModules,
    GetModuleFileNameEx,
)


def find_database_folder(wechat_id: str) -> str:
    """取默认数据库存放路径"""
    key_handle = OpenKey(HKEY_CURRENT_USER, r"Software\Tencent\WeChat")
    try:
        folder, _ = QueryValueEx(key_handle, "FileSavePath")
    except FileNotFoundError:
        ini_file = path.expanduser(
            "~\\AppData\\Roaming\\Tencent\\WeChat\\All Users\\config\\3ebffe94.ini"
        )
        with open(ini_file, "r", encoding="utf-8") as file_ini:
            folder = file_ini.read()
    if folder == "MyDocument:":
        key_handle = OpenKey(
            HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        )
        folder, _ = QueryValueEx(key_handle, "Personal")
    CloseHandle(key_handle)
    if len(folder) == 2:
        # 如果设置目录在根目录拿到的路径是E:
        folder = folder.replace(":", ":\\")
    return path.join(folder, "WeChat Files", wechat_id)


def find_process_module_address(process_handle: OpenProcess, module_name: str) -> int:
    """取进程模块地址（句柄），失败返回 None"""
    module_address = 0
    for module_handle in EnumProcessModules(process_handle):
        the_name = path.basename(
            GetModuleFileNameEx(process_handle, module_handle)
        ).lower()

        if the_name == module_name:
            module_address = module_handle  # 模块句柄实际上就是模块地址
            break
    return module_address


def read_database_raw_key(
    process_handle: OpenProcess,
    address: int,
    key_length: int = 32,
    offset: int = 0,
    validation: bool = True,
) -> bytes:
    """从内存中读取数据库 key，key 需要经过 calculate_key 处理后 sqlcipher 才能使用"""
    raw_process_handle = process_handle.handle
    key_address = c_int32()
    read_process_memory = windll.kernel32.ReadProcessMemory
    # 这里获取数据库密钥的开头可能是00 不能加判断
    if (
        not read_process_memory(
            raw_process_handle, address, byref(key_address), 4, None
        )
        and validation
    ):
        return b""
    key_address_int = key_address.value + offset
    key = create_string_buffer(key_length)
    read_process_memory(
        raw_process_handle, key_address_int, byref(key), key_length, None
    )
    if not key.value and validation:
        return b""
    return key.raw


def read_wechat_id(
    process_handle: OpenProcess, address: int, check: bool = True
) -> str:
    """读取 wechat id，用于自动取数据库路径，失败返回 None"""
    raw_process_handle = process_handle.handle
    wechat_id_length = 32
    wechat_id = create_string_buffer(wechat_id_length)
    read_process_memory = windll.kernel32.ReadProcessMemory
    read_process_memory(
        raw_process_handle, address, byref(wechat_id), wechat_id_length, None
    )
    try:
        www: str = wechat_id.value.decode()
        # 即使解码成功也不行，还要看它是不是字符，包含下划线
        if check and not bool(search(r"^[A-Za-z0-9_-]+$", www)):
            www = ""
    except UnicodeDecodeError:
        www = ""
    if not www:
        # 有的时候，微信号很长的时候，这里存放的是指针，不能直接获取，而必须根据指针获取
        temp_user_name = read_database_raw_key(process_handle, address, 64)
        print("temp_user_name---->", temp_user_name)
        if temp_user_name is not None:
            print("temp_user_name----->split", temp_user_name.split(b"\0", 1))
            try:
                www = temp_user_name.split(b"\0", 1)[0].decode()
            except UnicodeDecodeError:
                www = ""
    return www


def get_wechat_user(
    pid: int,
    offset_wechat_id: int,
    offset_username: int,
    offset_nickname: int,
    offset_db_key_pointer: int,
    offset_avatar: int,
) -> None:
    """获取微信用户信息
    :pid: 进程id
    :offset_wechat_id: 微信号偏移量
    :offset_username: 微信id偏移量
    :offset_nickname: 用户昵称偏移量
    :offset_db_key_pointer: 数据库密钥指针偏移量
    :offset_avatar: 头像偏移量
    """
    # 获取微信进程句柄
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    # 获取微信模块内存起始地址
    module_name = "wechatwin.dll"
    module_address = find_process_module_address(process_handle, module_name)
    # 从内存中获取微信号
    alias = read_wechat_id(process_handle, module_address + offset_wechat_id)
    # 从内存中获取微信用户名
    wechat_id = read_wechat_id(process_handle, module_address + offset_username)
    # 如果微信号获取不到用wechat_id代替
    alias = alias if alias else wechat_id
    wechat_id = wechat_id if wechat_id else alias
    # 获取昵称
    nickname = read_wechat_id(
        process_handle,
        module_address + offset_nickname,
        False,
    )
    # 获得数据库路径，如果以用户名的方式找不到文件夹，则换成微信号的方式找
    db_folder = (
        find_database_folder(alias)
        if not path.isdir(find_database_folder(wechat_id))
        else find_database_folder(wechat_id)
    )
    # 从内存中获取数据库密钥
    raw_key = read_database_raw_key(
        process_handle,
        module_address + offset_db_key_pointer,
        validation=False,
    )
    # 从内存中获取微信头像
    avatar = (
        read_database_raw_key(process_handle, module_address + offset_avatar, 200) or ""
    )
    if avatar:
        try:
            avatar = avatar.split(b"\0", 1)[0].decode()
        except UnicodeDecodeError:
            avatar = ""
    return {
        "alias": alias,
        "wechat_id": wechat_id,
        "nickname": nickname,
        "db_folder": db_folder,
        "raw_key": raw_key,
        "avatar": avatar,
    }
