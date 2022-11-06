#SeleniumBase.py

import time
import calendar
import functools
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def failure_screenshot(func):
    def inner_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            selenium = args[0]
            ts = calendar.timegm(time.gmtime())
            screenshotName = 'Screenshot' + str(ts)
            screenshot = selenium.SCREENSHOT_PATH + screenshotName + selenium.SCREENSHOT_EXT
            selenium.driver.save_screenshot(screenshot)
            logging.error('Screenshot saved in '+ screenshot)
            raise
    return inner_func

class SeleniumBase():

    FINDING_TIMEOUT = 3
    CHROME_BIN = '/usr/bin/google-chrome'
    CHROME_DRV = '/usr/bin/chromedriver'
    SCREENSHOT_PATH = './screenshots/'
    SCREENSHOT_EXT = '.png'

    findMethods = {
        'id'            : By.ID,
        'xpath'         : By.XPATH,
        'name'          : By.NAME,
        'tag'           : By.TAG_NAME,
        'class'         : By.CLASS_NAME,
        'css'           : By.CSS_SELECTOR,
        'partial-text'  : By.PARTIAL_LINK_TEXT,
        'text'          : By.LINK_TEXT

    }

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.binary_location = self.CHROME_BIN
        options.add_argument('--incognito')

#        driver = webdriver.Chrome(executable_path=self.CHROME_DRV, options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.maximize_window()
        self.driver = driver


    def open(self, url):
        self.driver.get(url)

    
    @failure_screenshot
    def getElementBy(self, method, value, multipleElements = False):
        byMethod = self.findMethods[method]
        wait = WebDriverWait(self.driver, self.FINDING_TIMEOUT)
        if multipleElements:
            output = wait.until(lambda d: d.find_elements(byMethod, value))
        else:
            output = wait.until(lambda d: d.find_element(byMethod, value))
        return output


    @failure_screenshot
    def getElementsBy(self, method, value, multipleElements = True):
            elements = self.getElementBy(method, value, multipleElements)
            return elements


    @failure_screenshot
    def getSubElementBy(self, parentElement, method, value, multipleElements = False):
        byMethod = self.findMethods[method]
        if multipleElements:
            output = parentElement.find_elements(byMethod, value)    
        else:
            output = parentElement.find_element(byMethod, value)    
        return output


    @failure_screenshot
    def getSubElementsBy(self, parentElement, method, value, multipleElements = True):
        subelements = self.getSubElementBy(parentElement, method, value, multipleElements)
        return subelements


    def close(self):
        self.driver.quit()


    def openNewTab(self, url, tabName):
        if not hasattr(self, 'mainWindowHandle'):
            self.mainWindowHandle = self.driver.window_handles[0]

        self.driver.execute_script("window.open('"+ url +"', '" + tabName + "')")
        self.driver.switch_to_window(tabName)

    def switchToTab(self, tabName):
        self.driver.switch_to_window(tabName)

    def switchToMainTab(self):
        self.driver.switch_to_window(self.mainWindowHandle)

    @failure_screenshot
    def waitForText(self, text):
        wait = WebDriverWait(self.driver, self.FINDING_TIMEOUT)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text))

    @failure_screenshot
    def isText(self, text, failIfNotFound = False):
        if failIfNotFound:
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text)
        else:
            try:
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text)
                return True
            except:
                return False

    @failure_screenshot
    def typeEnter(self, field, value):
        field.send_keys(value)
        field.send_keys(Keys.ENTER)

    @failure_screenshot
    def type(self, field, value):
        field.send_keys(value)

    def getAttribute(self, element, attribute):
        value = element.get_attribute(attribute)
        return value

    @failure_screenshot
    def scrollUntilClickable(self, element, retries = 0, maxRetries = 50):
        try:
            element.click()
        except:
            if (retries < maxRetries):
                html = self.getElementBy('tag', 'html')
                html.click()
                html.send_keys(Keys.PAGE_DOWN)
                retries += 1
                self.scrollUntilClickable(element, retries)
            else:
                raise
    @failure_screenshot
    def executeScript(self, script):
        return self.driver.execute_script(script)

    def getPageSource(self):
        return self.driver.page_source

    def closeCurrentTab(self):
        self.driver.execute_script("window.close()")
        self.switchToMainTab()
        

    def waitUntilNotPresent(self, method, xpath):
        element = WebDriverWait(self.driver, self.FINDING_TIMEOUT).until(EC.invisibility_of_element_located((self.findMethods[method], xpath)))
    
    def checkElements(self, method, xpath):
        try:
            elements = self.selenium.driver.find_elements(self.findMethods[method], xpath)
            ret = elements
        except:
            ret = []
        return ret



