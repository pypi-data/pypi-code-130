from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pandas as pd

def tuples(*args):
	data_tuple = []
	lists = []
	for x in range(0, len(args[0])):
		lists.append([item[x] for item in args])
	data_tuples = [tuple(list) for list in lists]
	return data_tuples

def toDataFrame(*args):
	columnNames = args[0:int(len(args) / 2)]
	dataList = args[int(len(args) / 2):len(args)]
	data_tuples = tuples(*dataList)
	return pd.DataFrame(data_tuples, columns=columnNames)


class scrape:
	def __init__(self, path, hidden):
		options = Options()
		options.headless=hidden
		options.add_experimental_option("excludeSwitches", ["enable-logging"])
		self.element = webdriver.Chrome(options=options, executable_path=path)
	def get(self, url):
		self.element.get(url)
	def find(self, by, selector):
		if by == ("css"):
			self.by = By.CSS_SELECTOR
		elif by == ("xpath"):
			self.by = By.XPATH
		elif by == ("id"):
			self.by = By.ID
		elif by == ("name"):
			self.by = By.NAME
		else:
			self.by = by
		if ("/") in selector:
			if len(selector.split("/")) == 2:
				self.selector = (selector.split("/")[0] + "[" + selector.split("/")[-1] + "]")
			elif len(selector.split("/")) == 3:
				self.selector = (selector.split("/")[0] + "[" + selector.split("/")[1] + "='" + selector.split("/")[-1] + "']")
		else:
			self.selector = selector
	def wait(self, by, selector):
		self.find(by, selector)
		WebDriverWait(self.element, 10).until(EC.presence_of_element_located((self.by, self.selector)))
	def get_wait(self, url, by, selector):
		self.get(url)
		self.wait(by, selector)
	def text(self):
		return self.element.find_element(self.by, self.selector).text
	def find_text(self, by, selector):
		self.find(by, selector)
		return self.text()
	def attr(self, attribute):
		return self.element.find_element(self.by, self.selector).get_attribute(attribute)
	def click(self):
		self.element.find_element(self.by, self.selector).click()
	def find_click(self, by, selector):
		self.find(by, selector)
		self.click()
	def url(self):
		return self.element.current_url
	def source(self):
		return self.element.page_source
	def close(self):
		self.element.close()