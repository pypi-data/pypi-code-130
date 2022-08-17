from dataclasses import dataclass
from pih.collection import FullName, LoginPasswordPair

from pih.const import CONST
from pih.rpc import RPC
from pih.tools import DataTools


@dataclass
class rpcCommand:
    host: str
    port: int
    name: str


class RPC_COMMANDS:

    class MARK:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(CONST.HOST.ORION.NAME(), CONST.RPC.PORT(), command_name)

        @staticmethod
        def ping() -> str:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command(CONST.RPC.PING_COMMAND))

        @staticmethod
        def get_free_marks() -> str:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("get_free_marks"))

        @staticmethod
        def get_mark_by_tab_number(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("get_mark_by_tab_number"), value)

        @staticmethod
        def get_mark_by_person_name(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("get_mark_by_person_name"), value)

        @staticmethod
        def get_free_marks_group_statistics() -> str:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("get_free_marks_group_statistics"))

        @staticmethod
        def get_free_marks_by_group(group: dict) -> str:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("get_free_marks_by_group"), group)

        @staticmethod
        def set_full_name_by_tab_number(value: FullName, tab_number: str) -> bool:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("set_full_name_by_tab_number"), (value, tab_number))


        @staticmethod
        def create(full_name: FullName, tab_number: str, telephone: str = None) -> bool:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("create"), (full_name, tab_number, telephone))

        @staticmethod
        def set_telephone_by_tab_number(value: str, tab_number: str) -> bool:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("set_telephone_by_tab_number"), (value, tab_number))

        @staticmethod
        def make_mark_as_free_by_tab_number(tab_number: str) -> bool:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("make_mark_as_free_by_tab_number"), tab_number)

        @staticmethod
        def get_all_persons() -> bool:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command("get_all_persons"))

    class USER:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(CONST.HOST.AD.NAME(), CONST.RPC.PORT(), command_name)

        @staticmethod
        def ping() -> str:
            return RPC.call(RPC_COMMANDS.USER.create_rpc_command(CONST.RPC.PING_COMMAND))

        @staticmethod
        def user_is_exsits_by_login(value: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.USER.create_rpc_command("user_is_exsits_by_login"), value))

        @staticmethod
        def set_telephone(user_dn: str, telephone: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.USER.create_rpc_command("user_set_telephone"), (user_dn, telephone)))

        @staticmethod
        def get_user_by_full_name(value: FullName) -> dict:
            return RPC.call(RPC_COMMANDS.USER.create_rpc_command("get_user_by_full_name"), value)

        @staticmethod
        def get_user_by_name(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.USER.create_rpc_command("get_user_by_name"), value)

        @staticmethod
        def get_user_by_login(value: str) -> dict:
            return RPC.call(RPC_COMMANDS.USER.create_rpc_command("get_user_by_login"), value)

        @staticmethod
        def get_template_list() -> dict:
            return RPC.call(RPC_COMMANDS.USER.create_rpc_command("get_template_list"))

        def get_containers() -> dict:
            return RPC.call(RPC_COMMANDS.USER.create_rpc_command("get_containers"))

        @staticmethod
        def create_from_template(templated_user_dn: str, full_name: FullName, login: str, password: str, description: str, telephone: str, email: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.USER.create_rpc_command("create_user_from_template"), (templated_user_dn, full_name, login, password, description, telephone, email)))

        @staticmethod
        def create_in_container(container_dn: str, full_name: FullName, login: str, password: str, description: str, telephone: str, email: str) -> bool:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.USER.create_rpc_command("create_user_in_container"), (container_dn, full_name, login, password, description, telephone, email)))

    class TEMPLATE:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(CONST.HOST.TEMPLATE.NAME(), CONST.RPC.PORT(1), command_name)


        @staticmethod
        def ping() -> str:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command(CONST.RPC.PING_COMMAND))

        @staticmethod
        def create_user_documents(path: str, date_now_string: str, web_site_name: str, web_site: str, email_address: str, full_name: FullName, tab_number: str, pc: LoginPasswordPair, polibase: LoginPasswordPair, email: LoginPasswordPair) -> rpcCommand:
            return DataTools.rpc_unrepresent(RPC.call(RPC_COMMANDS.TEMPLATE.create_rpc_command("create_user_documents"), (path, date_now_string, web_site_name, web_site, email_address, full_name, tab_number, pc, polibase, email)))

    
    class BACKUP_WORKER:
    
        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(CONST.HOST.TEMPLATE.NAME(), CONST.RPC.PORT(1), command_name)
            

        @staticmethod
        def ping() -> str:
            return RPC.call(RPC_COMMANDS.MARK.create_rpc_command(CONST.RPC.PING_COMMAND))

