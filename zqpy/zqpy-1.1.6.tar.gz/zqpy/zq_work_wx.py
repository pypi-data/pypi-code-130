import os, requests, json, time
import zq_file, zq_const, zq_log

class work_wx_class():
    def __init__(self,
        corpid = 'wwb6ec4438ccc388c3',
        secret = '_surPYo0SLVcxPKzAnHdWBwpGl2woxWKWpSTMvbZvnw',
        agentid = '1000002'
    ):
        self.corpid = corpid            # Corpid是企业号的标识
        self.secret = secret            # Secret是管理组凭证密钥
        self.agentid = agentid          # 应用ID
        self.bot = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c2ae20ef-9a26-4791-abb5-962e07f97144'

    #https://www.runoob.com/markdown/md-block.html
    def work_wx_send_desc(self, desc='', userId=None):
        data={'msgtype':'text', 'text':{'content':desc}}
        if userId:
            data['touser'] = userId
        self.work_wx_send(data)
    
    def work_wx_get_token_from_server(self, corpid, secret, token_path):
        ''' 获取 token '''
        token = False
        try:
            if os.path.exists(token_path):
                file = open(token_path, 'r')
                jsonFileData = json.load(file)
                token = jsonFileData['access_token']
                expires_in = jsonFileData['expires_in']
                file.close()
                
                modifyTime = os.path.getmtime(token_path)
                offtime = time.time() - modifyTime - expires_in
                if offtime > 0:
                    token = False
                    raise Exception('%s 校验文件已过期,需要重新获取校验信息'%token_path)
            else:
                zq_file.dir_auto_create_dir_by_file(token_path)
                raise Exception('%s 校验文件不存在需要创建'%token_path)
        except Exception as e:
            zq_log.log_debug('Error: %s'%e)
            url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
            data = {
                'corpid': corpid,
                'corpsecret': secret
            }
            r = requests.post(url=url, params=data, verify=False)
            zq_log.log_debug('企业微信Token: %s'%r.json())
            if r.json()['errcode'] != 0:
                token = False
            else:
                token = r.json()['access_token']
                file = open(token_path, 'w')
                file.write(r.text)
                file.close()
                zq_log.log_debug('%s 校验文件已更新'%token_path)
        return token

    def work_wx_send(self, data, corpid=None, secret=None, errorNum=3):
        ''' 
        发送消息到企业微信
        API文档： https://work.weixin.qq.com/api/doc/90000/90135/90236
        '''
        if not corpid or not secret:
            corpid = self.corpid
            secret = self.secret
        token_path = zq_const.const_merage_caches_dir('./work_wx/%s_wechat_config.json'%(corpid))
        # 获取token信息
        token = self.work_wx_get_token_from_server(corpid, secret, token_path)
        # 发送消息
        if not 'agentid' in data:
            data['agentid'] = self.agentid
        if not 'touser' in data:
            data['touser'] = '@all'
        if not 'toparty' in data:
            data['toparty'] = '1'
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % token
        result = requests.post(url=url, data=json.dumps(data), verify=False)
        zq_log.log_debug('企业微信应用消息： 发送：%s  接收：%s'%(json.dumps(data), result.json()))
        # 如果发送失败，将重试多次if
        if result.json()['errcode'] != 0 and errorNum and errorNum > 0:
            if result.json()['errcode'] == 42001:
                os.remove(token_path)
                token = self.work_wx_get_token_from_server(corpid, secret, token_path)
            return self.work_wx_send(data, corpid, secret, errorNum-1)
        else:
            return result.json()
    
    def work_wx_send_bot(self, data, url=None):
        '''
        发送企业微信消息，机器人群
        API文档： https://work.weixin.qq.com/api/doc/90000/90136/91770
        '''
        url = url or self.bot
        if not 'mentioned_list' in data['text']:
            data['text']['mentioned_list'] = ['@all']
        if not 'mentioned_mobile_list' in data['text']:
            data['text']['mentioned_mobile_list'] = ['@all']
        zq_log.log_debug(json.dumps(data))
        result = requests.post(url=url, data=json.dumps(data), verify=False)
        zq_log.log_debug('企业微信应用消息： %s'%result.json())

if __name__ == "__main__":
    print(work_wx_class().work_wx_send_desc('99999'))