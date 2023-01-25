import json

import regex as re
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from unidecode import unidecode


class Scraper:
    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = selenium.webdriver.Chrome(options=chrome_options)
    url = 'https://www.womenshealth.gov/a-z-topics'
    driver.get(url=url)

    def get_categories(self):
        categories = self.driver.find_elements(By.CSS_SELECTOR, '.AtoZ-list li a')
        categories_list = [c.get_attribute('href') for c in categories]
        for k in categories_list:
            if 'gateway' in k:
                categories_list.remove(k)
        return categories_list

    def get_info(self, categegory):
        to_exclude = ['Sources', 'Did we answer your question',
                      'More information on', 'Selected References']
        self.driver.get(categegory)
        categ_name = self.driver.find_element(By.CSS_SELECTOR, 'h1').get_attribute('outerHTML')
        categ_name = BeautifulSoup(categ_name, 'html.parser').get_text().strip()
        questions = self.driver.find_elements(By.CSS_SELECTOR, 'h2')
        responses = self.driver.find_elements(By.CSS_SELECTOR, '.answer')
        description = self.driver.find_element(By.CSS_SELECTOR, '.heading-description p').get_attribute('innerText')
        rs = []
        qs = []
        for r in responses:
            res = r.get_attribute('outerHTML')
            text = BeautifulSoup(res, 'html.parser').get_text().strip()
            rs.append(text)
        for q in questions:
            res = q.get_attribute('outerHTML')
            text = BeautifulSoup(res, 'html.parser').get_text().strip()
            qs.append(text)
        list_of_questions_answers = []
        qs.remove('Breadcrumb')
        for i in range(len(rs)):
            resp = unidecode(rs[i])
            resp = re.sub('\n', '', resp)
            dc = {'question': qs[i], 'response': resp, 'url': categegory}
            if not any(ele in qs[i] for ele in to_exclude):
                list_of_questions_answers.append(dc)
        dc = {'category': categ_name, 'url': categegory , 'description':unidecode(description) ,'questions': list_of_questions_answers }
        return dc


if __name__ == '__main__':
    final_result = []
    scraper = Scraper()
    categs = scraper.get_categories()
    """ for categ in categs:
        info = scraper.get_info(categ)
        final_result.append(info) """
    info = scraper.get_info(categs[2])
    final_result.append(info)
    with open("sample.json", "w") as outfile:
        json.dump(final_result, outfile)
