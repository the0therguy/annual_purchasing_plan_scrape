import datetime
import json

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import time
import random
from bs4 import BeautifulSoup


def scrape():
    url = 'https://comunidad.comprasdominicana.gob.do/Public/App/AnnualPurchasingPlanManagementPublic/Index'
    option = webdriver.FirefoxOptions()
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    # Enable headless mode
    option.add_argument('--headless')
    # Initialize the WebDriver with the configured options
    driver = webdriver.Firefox(options=option)
    driver.get(url)
    front_page_data = []
    time.sleep(random.randint(10, 15))
    # scraping front page
    driver.find_element(By.ID,
                        'tblMainTable_trRowMiddle_tdCell1_tblForm_trGridRow_tdCell1_grdResultList_Paginator_goToPage_MoreItems').click()

    time.sleep(random.randint(10, 15))
    table = driver.find_element(By.ID, 'tblMainTable_trRowMiddle_tdCell1_tblForm_trGridRow_tdCell1_grdResultList_tbl')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    tr = tbody.find_elements(By.TAG_NAME, 'tr')
    initial_date = tr[1].text.split('\n')[-3]
    time.sleep(random.randint(2, 6))
    for i in range(1, len(tr) - 2):
        t = tr[i].text.split('\n')
        time.sleep(7)
        if initial_date == t[5]:
            details_link = tr[i].find_element(By.ID,
                                              'tblMainTable_trRowMiddle_tdCell1_tblForm_trGridRow_tdCell1_grdResultListtd_thEditButton').find_element(
                By.TAG_NAME, 'a').get_attribute('href')
            front_page_data.append({'company_name': t[0], 'version': t[4], 'version_date': t[5], 'publish_date': t[2],
                                    'details': details_link})

        else:
            break

    time.sleep(random.randint(10, 15))
    whole_data = []
    # scraping 2nd page data
    for i in front_page_data:
        print(i.get('company_name'))
        driver.get(i.get('details'))
        time.sleep(random.randint(7, 10))
        # Extract contact information
        contact_info = driver.find_element(By.ID, 'fdsContactInfo_tblContactInfoTable').find_element(By.TAG_NAME,
                                                                                                     'tbody').text.split(
            '\n')
        # Extract global value information
        global_value = driver.find_element(By.ID, 'fdsBudgetInfo').find_element(By.TAG_NAME, 'div').text.split('\n')
        # Extract data table
        data_table = driver.find_element(By.ID, 'tblAcqGrid').find_element(By.TAG_NAME, 'tbody').find_element(By.ID,
                                                                                                              'tblAcqGrid_trrow1').find_element(
            By.ID, 'tblAcqGrid_trrow1_tdcell1').find_element(By.ID, 'grdTempAcqGrid').find_element(By.ID,
                                                                                                   'grdTempAcqGrid_tbl').find_element(
            By.TAG_NAME, 'tbody')
        second_page_data = []
        # looping through the table
        for d in range(1, len(data_table.find_elements(By.TAG_NAME, 'tr')) - 2):
            table = data_table.find_elements(By.TAG_NAME, 'tr')[d].find_elements(By.TAG_NAME, 'td')
            per_page_data = []
            for ta in table:
                row_data = BeautifulSoup(ta.get_attribute('outerHTML'), "html.parser").get_text()
                per_page_data.append(row_data)
            second_page_data.append(per_page_data)

        whole_data.append(
            {'company_name': i.get('company_name'), 'version': i.get('version'), 'version_date': i.get('version_date'),
             'publish_date': i.get('publish_date'), 'name': contact_info[1], 'phone_number': contact_info[3],
             'email': contact_info[5], 'global_value': global_value[1], 'table_data': second_page_data})

        time.sleep(random.randint(7, 12))
    # closing the webdriver after done
    driver.quit()
    return whole_data


if __name__ == '__main__':
    data = scrape()
    with open('data.json', 'w') as file:
        json.dump(data, file)
