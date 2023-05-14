import os
import time
import argparse

from functools import wraps
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initiate_selenium_driver(*args):
    options = webdriver.ChromeOptions()
    for arg in args:
        options.add_argument(arg)
    return webdriver.Chrome(options=options)


def wait(browser, wait_object, wait_time):
    WebDriverWait(browser, wait_time).until(
        EC.visibility_of_element_located(wait_object)
    )


def access(browser, url, wait_object, wait_time=10):
    browser.get(url)
    wait(browser, wait_object, wait_time)


def click_first_article(browser, wait_time):
    titles = browser.find_elements(By.CLASS_NAME, "s_tit")
    first_article = titles[0].find_element(By.TAG_NAME, "a")
    first_article.click()
    wait(browser, (By.ID, 'contentBody'), wait_time)


def get_case_list(browser):
    # list of cases is in the first element of div class="left_list_bx"
    list_box = browser.find_element(By.CSS_SELECTOR, "ul.left_list_bx")
    return list_box.find_elements(By.TAG_NAME, "li")


def do_until_succeed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                result = func(*args, **kwargs)
                return result
            except:
                time.sleep(0.1)
                pass
    return wrapper


@do_until_succeed
def is_first_element_clickable(browser):
    list_case = get_case_list(browser)
    link = list_case[0].find_element(By.TAG_NAME, "a")
    link.click()
    return True


@do_until_succeed
def click(link):
    link.click()


@do_until_succeed
def retrieve_info(browser):
    content_body = browser.find_element(By.ID, "contentBody")

    url = browser.current_url
    case_id = url[url.find("#")+1:]

    title = content_body.find_element(By.TAG_NAME, "h2").text
    subtitle = content_body.find_element(By.CSS_SELECTOR, "div.subtit1").text

    pgroup = content_body.find_element(By.CSS_SELECTOR, "div.pgroup")
    body = "\n".join([element.text for element in pgroup.find_elements("xpath", "./*") if element.text != ""])

    text = title + "\n" + subtitle + "\n" + body

    return {"case_id": case_id,
            "title": title,
            "subtitle": subtitle,
            "text": text}


def save_txt(savedir, info):
    filename = get_filename(info["case_id"])
    path_save = Path(savedir) / filename

    os.makedirs(savedir, exist_ok=True)

    with open(path_save, "w") as f:
        f.write(info["text"])


def get_filename(case_id):
    return "{}.txt".format(case_id)


def save_content(browser, case, savedir):
    link = case.find_element(By.TAG_NAME, "a")
    click(link)

    info = retrieve_info(browser)

    save_txt(savedir, info)


def save_contents_in_page(browser, savedir):
    if is_first_element_clickable(browser):
        for case in get_case_list(browser):
            save_content(browser, case, savedir)


def page2pindex(page, page_interval):
    return (page - 1) % page_interval


def set_page(browser, page, page_interval):
    pindex = page2pindex(page, page_interval)
    if pindex == 0:
        paging = browser.find_element(By.CSS_SELECTOR, "div.paging")
        list_move_button = paging.find_elements(By.TAG_NAME, "a")
        # list_move_button: [start_page, prev_page, next_page, end_page]
        click(list_move_button[-2])
    else:
        ol = browser.find_element(By.TAG_NAME, "ol")
        list_other_pages = ol.find_elements(By.TAG_NAME, "li")
        click(list_other_pages[pindex])


def click_articles_and_save_contents(browser, start_page, end_page, page_interval, savedir):
    for page in range(start_page, end_page+1):
        if page != start_page:
            set_page(browser, page, page_interval)

        save_contents_in_page(browser, savedir)


def run(args):
    browser = initiate_selenium_driver()
    access(browser, args.url_home, wait_object=(By.CSS_SELECTOR, 'div.tbl_wrap'))
    click_first_article(browser, args.wait_time)
    # website structure changes after clicking the first article
    click_articles_and_save_contents(browser, args.start_page, args.end_page, args.page_interval, args.savedir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example script using argparse')
    parser.add_argument('--url_home', type=str, default="http://www.law.go.kr/precSc.do")  # url accessible on 2023/05/13
    parser.add_argument('--savedir', type=str, default="crawled_data")
    parser.add_argument('--start_page', type=int, default=1)  # url accessible on 2023/05/13
    parser.add_argument('--end_page', type=int, default=1712)
    parser.add_argument('--page_interval', type=int, default=5)
    parser.add_argument('--wait_time', type=int, default=10, help="wait time in seconds")
    args = parser.parse_args()

    run(args)
