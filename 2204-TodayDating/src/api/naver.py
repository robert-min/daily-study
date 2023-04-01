# -*- coding: utf-8 -*-

class NaverApi:
    def __init__(self, keyword):
        import secret

        self.keyword = keyword
        self.client_id = secret.naver_id
        self.client_secret = secret.naver_secret

    def get_blog_count(self, display):
        import urllib.request
        import urllib.parse
        import json
        import math

        # OO 데이트로 기본 검색
        encode_query = urllib.parse.quote(self.keyword + '데이트')
        search_url = "https://openapi.naver.com/v1/search/blog?query=" + encode_query
        request = urllib.request.Request(search_url)

        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)

        response = urllib.request.urlopen(request)
        response_code = response.getcode()

        if (response_code == 200):
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode("utf-8"))

            print("Last blog build date : " + str(response_body_dict["lastBuildDate"]))

            if response_body_dict["total"] == 0:
                blog_count = 0
            else:
                blog_total = math.ceil(response_body_dict["total"] / int(display))

                if blog_total >= 1000:
                    blog_count = 1000
                else:
                    blog_count = blog_total

                print("Blog total : " + str(blog_total))
                print("Blog count : " + str(blog_count))

        return blog_count

    def get_blog_post(self, display, start_index):
        import urllib.request
        import urllib.parse
        import json
        from bs4 import BeautifulSoup
        import time
        from collections import defaultdict

        # OO 데이트로 기본 검색
        encode_query = urllib.parse.quote(self.keyword + ' 데이트')
        search_url = "https://openapi.naver.com/v1/search/blog?query=" + encode_query + \
                     "&start=" + str(start_index) + "&display=" + str(display)
        request = urllib.request.Request(search_url)

        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)

        response = urllib.request.urlopen(request)
        response_code = response.getcode()

        all_contents = defaultdict(dict)
        all_contents["keyword"] = self.keyword

        if (response_code == 200):
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode("utf-8"))
            contents = response_body_dict["items"]

            for item_index, content in enumerate(contents):
                all_contents[item_index]["blog"] = content
                link = content["link"]
                ori_link = link.replace("?Redirect=Log&logNo=", "/")
                post_code = urllib.request.urlopen(ori_link).read()
                post_soup = BeautifulSoup(post_code, "lxml")

                for mainFrame in post_soup.select("iframe#mainFrame"):
                    blog_post_url = "http://blog.naver.com" + mainFrame.get("src")
                    blog_post_code = urllib.request.urlopen(blog_post_url).read()
                    blog_post_soup = BeautifulSoup(blog_post_code, "lxml")

                    try:
                        map_soup = blog_post_soup.find("div", attrs={"class": "se-module se-module-map-text"})
                        place_text = map_soup.find("a")["data-linkdata"]
                        place_dict = json.loads(place_text)
                        all_contents[item_index]["place"] = place_dict
                    except:
                        pass
                item_index += 1
                time.sleep(0.001)

        return all_contents

    def save_json(self, tm):
        display = 100
        self.blog_count = self.get_blog_count(display)
        print(self.keyword, ":", self.blog_count)
        contents = list()
        for start_index in range(1, self.blog_count + 1, display):
            print(start_index)
            temp = self.get_blog_post(display, start_index)
            contents.append(temp)

        import json
        import os
        from time import strftime

        path = "./date_data/" + strftime("%Y-%m-%d", tm)

        try:
            if not os.path.isdir(path):
                os.mkdir(path)
        except OSError as e:
            if e.errno != e.errno.EEXIST:
                print("Failed to create")
                raise

        for index, content in enumerate(contents):
            with open(path + "/{}-{}.json".format(strftime("%H-%M-%S", tm), index), "w") as f:
                json.dump(content, f, indent=4, ensure_ascii=False)

    def save_list(self, tm):
        from time import strftime

        path = "./date_data/" + strftime("%Y-%m-%d", tm)

        with open(path + "/{}.txt".format(strftime("%Y-%m-%d", tm)), "a+") as f:
            f.write(strftime("%H-%M-%S", tm) + ".json, " + self.keyword + "\n")

        print("{} : 수집완료".format(self.keyword))



