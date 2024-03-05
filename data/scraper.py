from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

class LawScraper:
    def __init__(self, headless: bool = True, driverPath : str = '/snap/bin/geckodriver') -> None:
        self.base_url = "https://caselaw.findlaw.com/search.html?search_type=party&court=us-supreme-court&text="
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        if headless: self.options.add_argument("--headless")
        self.driverService = Service(driverPath)
    
    def get_cases(self, start: datetime, end: datetime, pageStart: int = 1, pageLimit: int = 20000) -> list[dict]:
        caseList = []
        self.driver = webdriver.Firefox(service=self.driverService, options=self.options)
        self.driver.get(self.base_url + f"&date_start={start.strftime("%Y%m%d")}&date_end={end.strftime("%Y%m%d")}")
        span = self.driver.find_element(By.CLASS_NAME, 'pagecount')
        count = span.find_elements(By.TAG_NAME, 'strong')[1]
        pageCount = min(int(count.get_attribute("innerText")), pageLimit)
        self.driver.quit()
        print(pageCount)
        for p in range(pageStart, pageCount+1):
            if p % 1000 == pageStart:
                print('On Page:', p)
            urls = self.get_page_urls(start, end, p)
            print(urls)
            for url in urls:
                caseList.append(self.get_case_content(url))
        return caseList

    def get_page_urls(self, start: datetime, end: datetime, pageNum : int) -> list[str]:
        self.driver = webdriver.Firefox(service=self.driverService, options=self.options)
        self.driver.get(self.base_url + f"&date_start={start.strftime("%Y%m%d")}&date_end={end.strftime("%Y%m%d")}&page={pageNum}")
        table = self.driver.find_element(By.CLASS_NAME, 'responsive-card-table')
        linkTagList = table.find_elements(By.TAG_NAME, 'a')
        urlList = [a.get_attribute("href") for a in linkTagList]
        self.driver.quit()
        return urlList
    
    def get_case_content(self, url: str) -> dict:
        caseContent = {}
        self.driver = webdriver.Firefox(service=self.driverService, options=self.options)
        self.driver.get(url)
        info = self.driver.find_element(By.CLASS_NAME, 'case-information')
        title = info.find_element(By.TAG_NAME, 'h2').get_attribute("innerText")
        caseContent['name'] = ', '.join(title.split(', ')[:-1]).split('(')[0].rstrip()

        paragraphs = info.find_elements(By.TAG_NAME, 'p')
        for paragraph in paragraphs:
            paragraphText = paragraph.get_attribute("innerText").split(':')
            caseContent[paragraphText[0]] = paragraphText[1]
            
        content = self.driver.find_element(By.ID, 'caselaw-content')
        caseContent['content'] = content.get_attribute("innerText")
        self.driver.quit()
        caseContent['url'] = url
        return caseContent
