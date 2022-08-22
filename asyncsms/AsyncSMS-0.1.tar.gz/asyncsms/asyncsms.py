from smsactivate.api import SMSActivateAPI
import asyncio

class AsyncSMS(SMSActivateAPI):

    def __init__(self, api_key):
        super().__init__(api_key)
    
    async def get_balance(self):
        """得到余额
        """
        return self.getBalance()
    
    async def get_active_activations(self):
        """得到激活列表"""
        return self.getActiveActivations()
    
    async def get_number(self, service:str='tg', country:int=None):
        """得到号码
        """
        if country is None:
            top_countries = self.getTopCountriesByService(service)
            country = top_countries.iloc[0, 0]
        return self.getNumberV2(service=service, country=country)
    
    async def get_code(self, activation_id:str, retries:int=60):
        """得到code
        """
        code = None
        for i in range(retries):
            r = self.getStatus(activation_id)
            if isinstance(r, dict) or r == 'STATUS_WAIT_CODE':
                await asyncio.sleep(1)
            elif isinstance(r, str):
                r_list = r.split(':')
                code = r_list[1]
                break
        return code
    
    async def set_status(self, activation_id:str, status:int):
        """设置激活状态
        """
        return self.setStatus(id=activation_id, status=status)