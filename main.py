import selenium
from selenium.webdriver.common.keys import Keys
import schedule
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re

class comment_poster:
    latest_post_id = None
    latest_post_reply_button = None
    def __init__(self,username, password, webdriver, interval_check,target_account, comment):

        self.driver = webdriver
        self.login_url = "https://truthsocial.com/login"

        self.target_url = "https://truthsocial.com/" + target_account
        self.comment = comment
        self.interval = interval_check

        self.driver.get(self.login_url)
        self.login(username,password)

        #self.post_comment() #TEST

        schedule.every(self.interval).seconds.do(self.new_post_check)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def login(self, username, password):
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.send_keys(username)
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(password)
        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/div[1]/div/div/div/div/div[2]/form/div[3]/button"))
        )
        login_button.click()
        print("Going to url:", self.target_url)
        time.sleep(3)
        self.driver.get(self.target_url)
        time.sleep(1.5)
        self.scroll_down(900)
        time.sleep(3)


    def new_post_check(self):
        self.driver.get(self.target_url)
        time.sleep(3)
        self.scroll_down(900)
        time.sleep(3)
        try:
            latest_post_id, latest_post = self.get_latest_post_id()
            if(latest_post_id != self.latest_post_id and latest_post is not None):
                self.latest_post_id = latest_post_id
                print("New post found, posting comment")
                self.post_comment(latest_post_id,latest_post)
        except Exception as e:
            print(e)

    def get_latest_post_id(self):
        #Fetches the latest post id and post (so you can easily find the button on the post)

        all_posts = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,'div[data-index]'))#'div[class="py-4 status__wrapper space-y-4 status-public"]'))
        )
        if(len(all_posts) == 1):
            post_element = all_posts[0]
            latest_post = all_posts[0].get_attribute("outerHTML") #Gets the data form the post
            latest_post_index = re.findall(r'\d+', latest_post)[0] #Finds the "data-index" from the post
            if(latest_post_index == 1): #If it's the last post
                latest_post_id = re.findall(r'\d+',latest_post)[0]
                return latest_post_id,post_element
        else:
            data_indexes = [re.findall(r'\d+', x.get_attribute("outerHTML")) for x in all_posts]
            for i, index in enumerate(data_indexes):
                index = int(index[0])
                if(index == 1):
                    post_element = all_posts[i]
                    latest_post = all_posts[i].get_attribute("outerHTML")
                    latest_post_id = [x for x in re.findall(r'\d+', latest_post) if(len(x)==18)][0]
                    return latest_post_id,post_element
        #print("none check",type(latest_post),type(post_element))
        post_element = all_posts[i]
        latest_post = all_posts[i].get_attribute("outerHTML")
        latest_post_id = [x for x in re.findall(r'\d+', latest_post) if (len(x) == 18)][0]
        return latest_post_id, post_element

    def post_comment(self,data_id,post):
        self.latest_post_reply_button = WebDriverWait(post, 10).until(
            EC.presence_of_element_located((By.TAG_NAME,
                                            "button"))#f"[data-id='{data_id}']"))
        )
        reply_button = self.latest_post_reply_button
        reply_button.click()
        text_area = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID,
                                            "compose-textarea"))
        )
        text_area.send_keys(self.comment)
        submit = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'button[type="submit"]'))
                                            #"/html/body/div[1]/div[2]/div[2]/div/div/div/div[2]/form/div[3]/div[2]/button"))
        )
        submit.click()
        #self.driver.close()

    def scroll_down(self,scroll_distance):
        self.driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_distance)




if __name__ == '__main__':
    #Za chrome koristi selenium.webdriver.Firefox()
    cp = comment_poster("acc_name",
                        "password",
        selenium.webdriver.Firefox(),
                        15,
                        "target_acc",
                        "Test comment")
