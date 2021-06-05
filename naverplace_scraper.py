import pickle
from selenium import webdriver
import time
import tqdm
import pandas as pd
import numpy as np


class Mydriver:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=options)

    @staticmethod
    def load_cafe_list():
        """
        미리 만들어둔 카페 리스트를 가져옵니다.
        """
        with open("cafelist.pickle", "rb") as f:
            cafels = pickle.load(f)
        return cafels

    def scroll_down_all(self):
        """
        스크롤을 끝까지 내리도록 자바스크립트 함수를 실행합니다.
        """
        SCROLL_PAUSE_TIME = 1
        while True:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                else:
                    last_height = new_height
                    continue

    def close(self):
        self.driver.close()

    def get_data(self):
        """
        셀레니움 브라우져 안에서 유저이름,리뷰를남긴 시점, rating점수, 리뷰를 데이터프레임화 합니다.
        """

        username_ls = []
        date_ls = []
        rating_ls = []
        review_ls = []

        withoutpic = self.driver.find_elements_by_class_name("_2Cv-r ")
        for user in withoutpic:
            username = user.find_element_by_class_name("hbo4A")
            username_ls.append(username.text)

            date = user.find_element_by_class_name("ZvQ8X")
            date_ls.append(date.text[:10])

            rating = user.find_element_by_class_name("_2tObC")
            rating_ls.append(rating.text)
            try:
                review = user.find_element_by_class_name("WoYOw")
                review_ls.append(review.text)
            except:
                review_ls.append(np.nan)

        data = {"username": username_ls, "date": date_ls, "rating": rating_ls, "review": review_ls}
        columns = ["username", "date", "rating", "review"]
        df = pd.DataFrame(data, columns=columns)
        return df

    def cafe_scraper(self, cafename):
        """
        카페 이름을 가져와 셀레니움을 이용해 데이터를 수집하여 DataFrame으로 변환 및 pickle로 저장합니다.
        cafename: (str)
        """
        url = f"https://m.map.naver.com/search2/search.naver?query={cafename}&siteLocation=&queryRank=&type="

        self.driver.get(url)
        btn1 = self.driver.find_element_by_css_selector(
            """#ct > div.search_listview._content._ctList > ul > li:nth-child(1) > div.item_info > a.a_item.a_item_distance._linkSiteview > div"""
        )
        btn1.click()

        time.sleep(1)

        currenturl = self.driver.current_url
        reviewurl = currenturl.replace("home", "review")
        self.driver.get(reviewurl)  # get to review section
        time.sleep(1)

        Mydriver()

        time.sleep(1)

        numofreview = self.driver.find_element_by_class_name("place_section_count").text
        print("리뷰수:", numofreview)
        btnclick = round(int(numofreview) / 10)  # calc how many times to click

        for i in range(btnclick - 38):  # -38 is for short test, remove when you want to run all
            try:
                morebtn = self.driver.find_element_by_class_name("_3iTUo")
                morebtn.click()
                time.sleep(1)
                Mydriver()
                time.sleep(2)
            except:
                pass

        time.sleep(1)

        df = Mydriver.get_data()

        df.to_pickle(f"{cafename}.pickle")
        print(f"{cafename}: 저장완료")
        Mydriver.close()


if __name__ == "__main__":
    # test for the first one
    # use for-loop to scrape all cafes and check process using tqdm
    ls = Mydriver.load_cafe_list()
    cafename = ls[0]
    Mydriver = Mydriver()
    Mydriver.cafe_scraper(cafename)
    df = pd.read_pickle("알베르.pickle")
    print(df.head())
