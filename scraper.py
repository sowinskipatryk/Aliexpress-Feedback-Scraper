from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd


driver_path = r'C:\Program Files (x86)\chromedriver.exe'
url = 'https://pl.aliexpress.com/item/4000155832668.html'


def scrape_page():

    option = Options()

    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    driver = webdriver.Chrome(driver_path, options=option)  # Options added to prevent windows from popping up
    driver.maximize_window()
    sleep(2)
    driver.get(url)

    # Product's ID
    product_id = url.replace('https://pl.aliexpress.com/item/', '').replace('.html', '')

    # Seller's ID
    start = driver.page_source.find('sellerAdminSeq') + 16  # Getting rid of text prior to the ID
    stop = start + driver.page_source[start:].index(',')  # Summing up the positions where the ID begins and ends
    seller_id = driver.page_source[start:stop]

    # Company's ID
    start = driver.page_source.find('companyId') + 11
    stop = start + driver.page_source[start:].index(',')
    company_id = driver.page_source[start:stop]

    # Creating feedback URL
    feedback_url = f'https://feedback.aliexpress.com/display/productEvaluation.htm?v=2&productId={product_id}' \
                   f'&ownerMemberId={seller_id}&companyId={company_id}&memberType=seller&startValidDate=&i18n=true'

    driver.get(feedback_url)

    data = []  # Empty list to gather the data

    is_next_page = True
    while is_next_page:

        # Searching for the data in page source
        reviews = driver.find_elements_by_class_name('feedback-item.clearfix')
        for review in reviews:
            username = review.find_element_by_class_name('user-name').text
            country = review.find_element_by_class_name('user-country').text
            stars_bar = review.find_element_by_class_name('star-view')
            stars_perc = stars_bar.find_elements_by_tag_name('span')[0].get_attribute('style')
            stars = int(stars_perc[7:-2]) // 20
            contents_and_dates = review.find_elements_by_class_name('buyer-feedback')
            for content_and_date in contents_and_dates:
                content = content_and_date.find_elements_by_tag_name('span')[0].text
                date = content_and_date.find_elements_by_tag_name('span')[1].text
            images = review.find_elements_by_class_name('pic-view-item')
            links = []
            for image in images:
                links.append(image.get_attribute('data-src'))
            is_useful = review.find_elements_by_class_name('thf-digg-num')
            useful = is_useful[0].text
            useless = is_useful[1].text

            links = ", ".join(links)

            data.append([username, country, stars, content, date, useful, useless, links])

        # Checking if there's a next page of reviews
        # Try/except block used to avoid NoSuchElementException
        try:
            driver.find_element(By.CLASS_NAME, "ui-pagination-next.ui-goto-page")
            next = driver.find_elements(By.TAG_NAME, 'a')
            driver.execute_script("arguments[0].click();", next[-1])
        except:
            is_next_page = False

    # Building the DataFrame and saving the data in .csv format
    df = pd.DataFrame(data, columns=['Username', 'Country', 'Score', 'Content', 'Date', 'Useful', 'Useless', 'Links'])
    df.to_csv(f'feedback_{product_id}.csv', index=False)


scrape_page()
