from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import re 

class Scorer():
    def __init__(self, ):
        self.driver = webdriver.Chrome()
        print('webdriver initlized!')
        
    def rule(self, answer, update_time):
        if len(answer)>35:
                score = 100.00
        if len(answer)<=35 and len(answer)>25:
            score = 80.00
        if len(answer)<=25:
            score = 60.00
        return str(score)  

    def access(self, kadai_url, username_input, password_input, mode): 
        self.driver.get('https://moodle.s.kyushu-u.ac.jp/login/index.php')
        self.driver.maximize_window()
        username = self.driver.find_element_by_name('username')
        username.clear()
        username.send_keys(username_input)

        password = self.driver.find_element_by_name('password')
        password.clear()
        password.send_keys(password_input)
        password.send_keys(Keys.RETURN)
        
        if mode=='lu':
            moodle_url = 'https://moodle.s.kyushu-u.ac.jp/course/view.php?id=20717'
            self.driver.get(moodle_url)
            self.driver.find_elements_by_class_name("instancename")[1].click()
            windows = self.driver.window_handles
            self.driver.switch_to.window(windows[-1])
        
        self.driver.get(kadai_url)
       
        html = self.driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        pages = soup.select('li[class="page-item"]')
        self.num_page = len(pages)//2
        
    def score(self): 
        html = self.driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        tbody = soup.find('tbody')
        students = tbody.find_all('tr', {'id':re.compile(r'mod_assign_grading_r\d+')})
        
        i = 0
        for student in students:
            score = '0.00'
            try:
                name = student.find('td', {'class':'cell c2'}).get_text()
                
                if name=='':
                    break
                score_input = self.driver.find_element_by_xpath('//tr[@id="mod_assign_grading_r{0}"]/td[@class="cell c7"]/input'.format(i))
                answer = student.find('td', {'class':'cell c10'}).find('div').get_text()
                update_time = student.find('td', {'class':'cell c9'}).get_text()
            except Exception:
                score_input.clear()
                score_input.send_keys(score)
                update_time = 'NAN'
            else:
                score = self.rule(answer, update_time)
                score_input.clear()
                score_input.send_keys(score)
            print('student:{0},name:{1},submit_time:{2},score:{3} done!'.format(i, name, update_time, score))
            i += 1
        save = self.driver.find_element_by_id('id_savequickgrades')
        save.click()
        print('successfully saved!!!')
        
    def auto_score(self, kadai_url, username_input, password_input, mode='konomi'):
        self.access(kadai_url, username_input, password_input, mode)
        self.score()
        # continue
        self.driver.find_element_by_xpath('//div[@role="main"]/div[@class="continuebutton"]/form/button').click()
        print('page 0 done!!')
        if self.num_page>1:
            for page in range(1, self.num_page):
                # next page
                home = self.driver.current_url
                self.driver.get(home+r'&page={}'.format(page))
                self.score()
                self.driver.find_element_by_xpath('//div[@class="continuebutton"]/form/button').click()
                print('page {} done!!'.format(page))