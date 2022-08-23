import ctypes
import os
import time
from subprocess import Popen, PIPE

from comtypes.client import CreateObject


class RegDm:

    @classmethod
    def reg(cls):
        path = os.path.dirname(__file__)
        reg_dm = ctypes.windll.LoadLibrary(path + r'\DmReg.dll')
        reg_dm.SetDllPathW(path + r'\dm.dll', 0)
        return CreateObject(r'dm.dmsoft')

    @classmethod
    def create_dm(cls):
        return CreateObject(r'dm.dmsoft')


class LDCmd:
    def __init__(self, path: str):
        os.putenv('Path', path)

    @staticmethod
    def read_message(cmd):
        res = Popen(cmd, stdout=PIPE, shell=True)
        res = res.stdout.read().decode(encoding='GBK')
        return res

    def lunch(self, order: str):
        self.read_message('ldconsole.exe launch --index ' + order)

    def quit(self, order: str):
        self.read_message(cmd='ldconsole.exe quit --index ' + order)

    def get_message(self):
        return self.read_message('ldconsole.exe  list2')
        # 索引，标题，顶层窗口句柄，绑定窗口句柄，是否进入android，进程PID，VBox进程PID

    def add(self, name: str):
        self.read_message('ldconsole.exe add --name ' + name)

    def remove(self, order: str):
        self.read_message('ldconsole.exe remove --index ' + order)

    def copy(self, name: str, order: str):
        self.read_message('ldconsole.exe copy --name ' + name + ' --from ' + order)

    def start_app(self, order: str, packagename: str):
        self.read_message('ldconsole.exe runapp --index ' + order + ' --packagename ' + packagename)

    def close_app(self, order: str, packagename: str):
        self.read_message('ldconsole.exe killapp --index ' + order + ' --packagename ' + packagename)

    def get_list_package(self, order: str):
        return self.read_message(cmd='ld.exe -s ' + order + '  pm list packages')

    def install_app(self, order: str, path: str):
        self.read_message('ldconsole.exe  installapp --index ' + order + ' --filename ' + path)

    def sort_wnd(self):
        self.read_message('ldconsole.exe sortWnd')

    def reboot(self, order: str):
        self.read_message('ldconsole.exe reboot --index ' + order)

    def get_appoint_game_hwd(self, order: str):
        my_list = self.get_message()
        items = my_list.splitlines()
        return items[int(order)].split(',')[3]


class Memory:
    def __init__(self, dx, hwd):
        self.__dx = dx
        self.hwd = hwd

    def get_call_address(self, s, model, off):
        # 返回16进制字符串地址
        module_size = self.__dx.GetModuleSize(self.hwd, model)
        base_address = self.__dx.GetModuleBaseAddr(self.hwd, model)
        end_address = module_size + base_address
        call_address = self.__dx.FindData(self.hwd, hex(base_address)[2:] + '-' + hex(end_address)[2:], s)
        return hex(int(call_address, 16) + int(off, 16))[2:]

    def x64_get_base_address(self, s, model, off):
        address = self.get_call_address(s, model, off)
        address = self.__dx.readint(self.hwd, address, 4)
        return hex(int(address, 16) + int(address) + 4)[2:]

    def x32_get_base_address(self, s, model, off):
        address = self.get_call_address(s, model, off)
        address = self.__dx.readint(self.hwd, address, 4)
        return hex(address)[2:]


class Mouse:
    """
    模块为dm鼠标类模块。
    例子：mouse = Mouse(dm)
    mouse.大漠移动(100,200)
    """

    def __init__(self, dx):
        self.__dx = dx

    def move_to(self, x: int, y: int):
        self.__dx.MoveTo(x, y)

    def left_click(self):
        self.__dx.LeftClick()

    def left_double_click(self):
        self.__dx.LeftDoubleClick()

    def left_down(self):
        self.__dx.LeftDown()

    def left_up(self):
        self.__dx.LeftUp()

    def move_left_click(self, x: int, y: int):
        self.move_to(x, y)
        self.left_click()

    def move_left_double_click(self, x: int, y: int):
        self.move_to(x, y)
        self.left_double_click()

    def left_drag(self, x1: int, y1: int, x2: int, y2: int):
        self.move_to(x1, y1)
        self.left_down()
        self.move_to(x2, y2)
        self.left_up()


class Pic:
    def __init__(self, dx):
        self.__dx = dx

    def find_pic(self, x1: int, y1: int, x2: int, y2: int, name: str):
        """



        :param x1: 找图的左上角纵坐标
        :param y1: 找图的左下角纵坐标
        :param x2: 找图的右上角纵坐标
        :param y2: 找图的右下角纵坐标
        :param name: 图片名字xx.bmp
        :return: 找到返回1，否则返回-1
        """

        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        if dm_ret != '-1|-1|-1':
            return 1
        else:
            return -1

    def wait_pic(self, x1: int, y1: int, x2: int, y2: int, name: str, t2: int):
        """



        :param x1: 找图的左上角纵坐标
        :param y1: 找图的左下角纵坐标
        :param x2: 找图的右上角纵坐标
        :param y2: 找图的右下角纵坐标
        :param name: 图片名字xx.bmp
        :param t2: 检测时间上限单位秒
        :return: 超时返回1，否则返回-1
        """
        t = time.time()
        while self.find_pic(x1, y1, x2, y2, name) == -1:
            t1 = time.time()
            if t - t1 > t2:
                return -1
            time.sleep(1)
        return -1

    def find_pic_left_click(self, x1: int, y1: int, x2: int, y2: int, name: str):
        """


        :param x1: 找图的左上角纵坐标
        :param y1: 找图的左下角纵坐标
        :param x2: 找图的右上角纵坐标
        :param y2: 找图的右下角纵坐标
        :param name: 图片名字xx.bmp
        :return: 点击成功返回1，否则返回-1
        """
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        pos = dm_ret.split('|')
        if pos[0] != '-1':
            Mouse(self.__dx).move_left_click(int(pos[1]), int(pos[2]))
            return 1
        else:

            return -1

    def find_pic_offsite_left_click(self, x1: int, y1: int, x2: int, y2: int, name: str, x3: int, y3: int):
        """


        :param x1: 找图的左上角纵坐标
        :param y1: 找图的左下角纵坐标
        :param x2: 找图的右上角纵坐标
        :param y2: 找图的右下角纵坐标
        :param x3: 相对于目标点的横坐标偏移量
        :param y3: 相对于目标点的纵坐标偏移量
        :param name: 图片名字xx.bmp
        :return: 点击成功返回1，否则返回-1
        """
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        pos = dm_ret.split('|')
        if pos[0] != '-1':
            self.__dx.MoveTo(int(pos[1]) + x3, int(pos[2]) + y3)
            self.__dx.LeftClick()

            return 1
        else:

            return -1

    def find_pic_left_click_disappear(self, x1: int, y1: int, x2: int, y2: int, name: str, t3: int):
        """

        :param x1: 找图的左上角纵坐标
        :param y1: 找图的左下角纵坐标
        :param x2: 找图的右上角纵坐标
        :param y2: 找图的右下角纵坐标
        :param name: 图片名字xx.bmp
        :param t3: 检测时间上限单位秒
        :return: 开始没有找到图返回-1，超时返回1，时间范围内消失返回-2
        """
        dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
        pos = dm_ret.split('|')
        t = time.time()
        if pos[0] != '-1':
            while time.time() - t < t3:
                Mouse(self.__dx).move_left_click(pos[1], pos[2])
                time.sleep(1)
                dm_ret = self.__dx.FindPicE(x1, y1, x2, y2, name, '050505', 0.9, 0)
                pos = dm_ret.split('|')
                if pos[0] != '-1':
                    Mouse(self.__dx).move_left_click(pos[1], pos[2])
                    time.sleep(1)
                else:
                    return -2
            return 1
        else:
            return -1


if __name__ == '__main__':
    dm = RegDm.reg()
    M = Mouse(dm)
    M.move_to(10, 10)
