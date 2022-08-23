from six import  wraps
import time,os
from util.log_util import logger

def get_screen(func):
    '''
    测试用例运行完成或者发生错误的时候进行截图
    :param func:
    :return:
    '''
    @wraps(func)
    def f1(obj,*args,**kwargs):
        try:
            func(obj,*args,**kwargs)
            time.sleep(1)
        except:
            current_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+"\\screenshot"
            obj.image_name = obj.image_name if obj.image_name is not None else "auto_test"
            image_path = os.path.join(current_path,obj.image_name+".png")
            # logger.info("异常截图存储位置为：",image_path)
            obj.driver.get_screenshot_as_file(image_path)
            time.sleep(1)
            # 发送异常截图日志至reportportal
            with open("D:\\UIAutotestFramework\\screenshot\\" + obj.image_name + ".png", "rb") as image_file:
                file_data = image_file.read()
                logger.info(msg=obj.image_name+"-异常截图", attachment={"name": obj.image_name+".png", "data": file_data, "mime": "image/png"})
            raise
    return f1




