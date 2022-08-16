def login_account(self,autologin=True):
        img_login=0
        try:
            self.driver.delete_all_cookies()
        except Exception as r:
            logger.warning('清除cookie发生错误，错误信息: %s' %(r))   

        logger.info('正在尝试使用账号密码登录站点...')

        if not ('username' in dir(self.site) and self.site.username!=None and 'password' in  dir(self.site) and self.site.password!=None): 
            logger.warning('登录失败，失败原因:站点'+self.site.sitename+'用户名密码信息不全，请检查配置文件au.yaml')
            return -1

        try:
            self.driver.get(self.site.loginurl)
        except Exception as r:
            logger.warning('打开登录页面发生错误，错误信息: %s' %(r))

        if len(self.driver.find_elements_by_name('username'))<=0:
            self.driver.execute_script("window.scrollBy(0,300)")

        if not self.wait_page():
            logger.warning('登录页面加载失败')
            return -1

        try:
            self.driver.find_elements_by_name('username')[0].send_keys(self.site.username)
            self.driver.find_elements_by_name('password')[0].send_keys(self.site.password)
        except Exception as r:
            logger.warning('输入用户名密码发生错误，错误信息: %s' %(r))
            return -1

        if self.site.sitename=='ssd':
            imgs=self.driver.find_elements_by_xpath('/html/body/section/main/div/form/div[3]/span[1]/img')
        else:
            imgs=self.driver.find_elements_by_xpath('/html/body/table[2]/tbody/tr/td/form[2]/table/tbody/tr[4]/td[2]/img')

        if len(imgs)>0:
            logger.info('遇到验证码，请稍等...')
            if self.headless==True:
                logger.warning('检测到目前正在后台运行，无法识别验证码，正常尝试重新登录,请稍等')
                return -1
            img_login=1
            #image_code_name=os.path.join(self.basic['screenshot_address'],'code.png')
            image_code_name=os.path.join(os.getcwd(),'code.png')
            if os.path.exists(image_code_name):
                logger.info('已存在验证码图片，正在删除'+image_code_name)
                try:
                    os.remove(image_code_name)
                except Exception as r:
                    logger.warning('删除图片发生错误: %s' %(r))
            try:
                self.driver.save_screenshot(image_code_name)
            except Exception as r:
                logger.info('保存图片发生错误，错误信息: %s' %(r))
            img_element = imgs[0]
            left = img_element.location['x']
            top = img_element.location['y']
            right = (img_element.location['x'] + img_element.size['width']) 
            bottom = (img_element.location['y'] + img_element.size['height']) 
            if platform.system()=='Darwin':
                left=left*2
                top=top*2
                right=right*2
                bottom=bottom*2
            logger.info('已获取位置')
            im = Image.open(image_code_name)
            im = im.crop((left, top, right, bottom))
            im.save(image_code_name)
            with open(image_code_name, 'rb') as f:
                image = f.read()  
            if autologin==Flase:
                autologin=int(input('是否使用OCR识别验证码,0否1是:'))
            if autologin==1:
                ocr = ddddocr.DdddOcr(show_ad=False,old=True)
                data_ocr = ocr.classification(image)
            else:
                showpic(image_code_name)
                data_ocr=input('请输入文件所示验证码:') 
            try:
                os.remove(image_code_name)
            except:
                a=None
            try:
                self.driver.find_elements_by_name('imagestring')[0].send_keys(data_ocr)
            except Exception as r:
                logger.info('输入验证码发生错误: %s' %(r)) 
                #return -1      

        logger.info('正在点击登录...')

        submitxpath='/html/body/table[2]/tbody/tr/td/form[2]/table/tbody/tr[10]/td/input[1]'
        if self.site.sitename=='hdyu':
            submitxpath='/html/body/table[2]/tbody/tr/td/form[2]/table/tbody/tr[7]/td/input[1]'
        elif self.site.sitename=='pter':
            time.sleep(3)
        elif self.site.sitename=='tjupt':
            submitxpath='/html/body/table[2]/tbody/tr/td/form/table/tbody/tr[5]/td/input[1]'

        try:
            if len(self.driver.find_elements_by_xpath(submitxpath))>0:
                logger.info('找到登录按键')
                self.driver.find_element_by_xpath(submitxpath).click()
        except Exception as r:
            logger.info('点击登录发生错误: %s' %(r)) 
        
        try:
            self.driver.get(self.site.uploadurl)
        except Exception as r:
            logger.warning('打开登录页面发生错误，错误信息: %s' %(r))
            return -1

        if not self.wait_page():
            logger.warning('登录页面加载失败')
            return -1

        try:
            fileitem=self.driver.find_elements_by_class_name('file')
        except Exception as r:
            logger.info('打开发布页面发生错误，错误信息: %s' %(r))

        if len(fileitem)>0:
            logger.info('登录站点成功！')
            self.login_done=1
            return 1
        else:
            if autologin==False or img_login==0:
                logger.warning('站点登录失败')
                return -1
            logger.info('自动识别验证码登陆失败,请手动输入验证码重试...')
            return self.login_account(autologin=False)
        return -1