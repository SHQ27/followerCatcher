from selenium_base import selenium_base
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from pprint import pprint
import time
import json

class FollowerCatcher():
    def __init__(self, loginData, targetAccount):
        self.basePath = 'http://twitter.com/' + targetAccount
        self.loginData = loginData
        self.targetAccount = targetAccount

    def start(self): 
        self.selenium = selenium_base.SeleniumBase()
        self.__login()

    def end(self):
        self.selenium.close()

    def catchFollowing(self):
        self.__catch('following')

    def catchFollowers(self):
        self.__catch('followers')

    #Private
    def __login(self):
        self.selenium.open('http://twitter.com/login')
        userInput = self.selenium.getElementBy('name', 'text')
        self.selenium.type(userInput, self.loginData['username'])
        nextButtonSpan = self.selenium.getElementBy('xpath', "//span[contains(text(), 'Next')]")
        nextButtonSpan.click()
        passwordInput = self.selenium.getElementBy('name', 'password')
        self.selenium.type(passwordInput, self.loginData['password'])
        logInButtonSpan = self.selenium.getElementBy('xpath', "//span[contains(text(), 'Log in')]")
        logInButtonSpan.click()
        self.selenium.waitForText(self.loginData['username'])

    def __catch(self, path):
        url = self.basePath + '/' + path 
        self.selenium.open(url)
        time.sleep(1.5)
        accounts = self.__getAccountsByEndlessScroll()
        pprint('Accounts to be parsed: ' +  str(len(accounts)))
        ret = []
        self.__writeJSON(targetAccount + '-' + path + '.json', '[', False)
        for account in accounts:
            info = self.__getAccountInfo(account)
            self.__writeJSON(targetAccount + '-' + path + '.json', info)
        self.__writeJSON(targetAccount + '-' + path + '.json', ']', False)

    def __getAccountsByEndlessScroll(self):
        accounts = []
        height = self.selenium.executeScript("return document.body.scrollHeight")
        while True:
            anchors = self.selenium.getElementsBy('xpath', '//div[@data-testid="primaryColumn"]//section[1]//div[@data-testid="cellInnerDiv"]//div[@data-testid="UserCell"]//a[1]')
            for anchor in anchors:
                href = anchor.get_attribute('href')
                if not href in accounts:
                    if not '?' in href and 'twitter' in href:
                        accounts.append(href)
            self.selenium.executeScript("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            current_height = self.selenium.executeScript("return document.body.scrollHeight")
            if current_height == height:
                break
            height = current_height
        return accounts

    def __getAccountInfo(self, account):
        self.selenium.open(account)
        url = account
        self.__checkIfRetry()

        username = '@' + url.removeprefix('https://twitter.com/')
        name = self.__tryInnerText('//div[@data-testid="UserName"]//span[1]/span[1]')
        bio = self.__tryInnerText('//div[@data-testid="UserDescription"]')
        joined = self.__tryInnerText('//span[@data-testid="UserJoinDate"]')
        followers = self.__tryInnerText("//span[contains(text(), 'Followers')]/parent::span/preceding-sibling::span")
        following = self.__tryInnerText("//span[contains(text(), 'Following')]/parent::span/preceding-sibling::span")
        info = {}
        info['username'] = username
        info['name'] = name
        info['followers'] = followers
        info['following'] = following
        info['joined'] = joined
        info['bio'] = bio
        return info

    def __tryInnerText(self, xpath):
        try: 
            value = self.selenium.getElementBy('xpath', xpath).get_attribute('innerText')
        except (NoSuchElementException, TimeoutException):
            value = ''
        return value

    def __writeJSON(self, filename, data, json = True):
        if json: 
            data = json.dumps(data)
        with open(filename, "a") as outfile:
            outfile.write(data + "\n")
            outfile.close()

    def __checkIfRetry(self):
        elements = self.selenium.checkElements('xpath', "//span[contains(text(), 'Retry')]")
        if elements:
            for element in elements:
                element.click()

#Execution

loginData = {
    'username' : 'recklessMFO',
    'password' : 'i92wSdc123'
}

targetAccount = 'Cointelegraph'

catcher = FollowerCatcher(loginData, targetAccount)
catcher.start()
catcher.catchFollowing()
catcher.end()
