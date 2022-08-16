from nonebot.rule import ArgumentParser
from .model import PARSER_DESC

ncov_parser = ArgumentParser("ncov", description=PARSER_DESC)
ncov_sub_parser = ncov_parser.add_subparsers(dest="cmd")

add_parser = ncov_sub_parser.add_parser('add', help="添加新的用户")
add_parser.add_argument('user', type=str, action='store', help="用户名字 (通常为学号) ")
add_parser.add_argument('password', type=str, action='store', help="用户密码")
# add_parser.add_argument('-c', '--cookie', type=str, action='store', help="用户 auth.bupt.edu.cn 的 cookie (需标准形式)")
add_parser.add_argument('-t', '--time', type=str, action='store', help="签到时间 (默认为 00:01 )", default="00:01")

remove_parser = ncov_sub_parser.add_parser('remove', help="删除用户")

modify_parser = ncov_sub_parser.add_parser('modify', help="修改用户数据")
modify_parser.add_argument('-u', '--user', type=str, action='store', help="用户名字 (通常为学号) ")
modify_parser.add_argument('-p', '--password', type=str, action='store', help="用户密码")
# add_parser.add_argument('-c', '--cookie', type=str, action='store', help="用户 auth.bupt.edu.cn 的 cookie (需标准形式)")
modify_parser.add_argument('-t', '--time', type=str, action='store', help="签到时间 (默认为 00:01 )")
modify_parser.add_argument('-s', '--status', help="签到状态, ( enable / disable )")

list_parser = ncov_sub_parser.add_parser('list', help="查看用户状态")
