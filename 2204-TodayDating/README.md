# Today Dating 데이트 장소 검색 카카오 챗봇 만들기
## Blog
[Blog link](https://github.com/robert-min/dev-blog/issues?q=is%3Aissue+is%3Aclosed+label%3ATodayDating)


## Preview
![image](https://user-images.githubusercontent.com/91866763/229274859-c3f0e8a5-1d40-442a-8cc1-447ecc8b21db.png) | ![image](https://user-images.githubusercontent.com/91866763/229274941-6916b4e8-989b-455a-9a8c-6d73a6f90861.png)
--- | --- | 

## Today Dating : 데이트 장소 카카오 챗봇

### Intro

개인프로젝트로 데이터를 활용한 서비스를 구상 중 커플 대상으로한 데이트 장소 검색 및 추천 서비스를 구상하게 되었습니다. 해당 서비스를 구상 후 빠르게 구상 후 테스트를 진행하기 위해 카카오 챗봇을 활용해 서비스를 제작했습니다.

해당 프로젝트는 아래의 단계로 개발 진행되었습니다.

1. 네이버 검색 API를 활용한 데이터 수집
2. 카프카를 활용해 수집한 데이터 DB 저장 자동화
3. 카카오 채팅 봇 스킬 구현을 위한 Flask 서버 구축
4. 서비스 배포를 위한 AWS EC2, RDS 활용
5. 결과 확인 및 프로젝트 회고
A. 코드 개선

### 네이버 검색 API를 활용한 데이터 수집

[https://developers.naver.com/products/service-api/search/search.md](https://developers.naver.com/products/service-api/search/search.md)

네이버는 블로그, 뉴스 등 개발자가 원하는 키워드로 데이터를 검색하는 검색 API product를 제공합니다. 이 중 블로그 검색 API를 활용하여 OO + 데이트로 작성된 블로그 글을 모으는 코드를 구현했습니다.

*참고!! 해당 리뷰는 코드를 중점으로 작성되어 있기 때문에 네이버 개발자 등록 과정 등은 생략하고 진행합니다.*

네이버 검색 API를 통한 블로그 정보 수집은 2가지 과정으로 진행되었습니다.

1. 네이버 검색 시 해당 키워드로 블로그 글이 몇개 있는지 확인합니다.
    
    1,000개 이상의 데이터는 정확도가 낮다고 판단하여 최대 블로그 개수를 1000개로 지정했습니다.
    

```python
# naver_blog.py
# 네이버 API(git 업로드시 삭제)
client_id = naver_secret.id
client_secret = naver_secret.secret

def get_blog_count(query, display):
    # OO 데이트로 기본 검색
    encode_query = urllib.parse.quote(query + '데이트')
    search_url = "https://openapi.naver.com/v1/search/blog?query=" + encode_query
    request = urllib.request.Request(search_url)

    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

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
```

1. 블로그 글 수 확인 후 각 블로그 정보 중 필요한 정보를 전처리합니다.
    
    이 단계에서 한가지 문제점이 있었습니다!!
    데이터를 수집하는 단계에서 Today dating 서비스가 모바일 앱을 통해 지도 형태로 정보 전달할 계획이었습니다. 하지만 네이버 검색 API에서는 블로그명, 블로그 주소 정보만을 제공하고 있지만 저는 블로그에서 소개하고 있는 장소 이름과 위치(위도, 경도)의 정보까지 필요했습니다.
    
    위의 문제를 해결하기 위해 저는 블로그 링크를 활용하여 bs4를 활용해 위치 정보를 추출했습니다. 물론 실제 서비스의 경우 크롤링 또는 스크래핑을 활용해 데이터를 수집하여 상용화 서비스를 제공하는 것은 문제의 소지가 있습니다. 하지만 해당 프로젝트는 저의 개인프로젝트로 학업의 목적이었기 때문에 bs4를 사용해 프로젝트를 진행했습니다.
    

```python
# naver_blog.py
def get_blog_post(query, display, start_index):

    # OO 데이트로 기본 검색
    encode_query = urllib.parse.quote(query + ' 데이트')
    search_url = "https://openapi.naver.com/v1/search/blog?query=" + encode_query + \
                 "&start=" + str(start_index) + "&display=" + str(display)
    print(search_url)
    request = urllib.request.Request(search_url)

    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()

    if (response_code == 200):
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode("utf-8"))

        for item_index in range(0, len(response_body_dict["items"])):
            remove_tag = re.compile("<.*?>")
            keyword = str(query)
            title = re.sub(remove_tag, "", response_body_dict["items"][item_index]["title"])
            link = response_body_dict["items"][item_index]["link"]
            ori_link = link.replace("?Redirect=Log&logNo=", "/")

            post_code = urllib.request.urlopen(ori_link).read()
            post_soup = BeautifulSoup(post_code, "lxml")

            for mainFrame in post_soup.select("iframe#mainFrame"):
                blog_post_url = "http://blog.naver.com" + mainFrame.get("src")
                blog_post_code = urllib.request.urlopen(blog_post_url).read()
                blog_post_soup = BeautifulSoup(blog_post_code, "lxml")

                try:
                    map_soup = blog_post_soup.find("div", attrs={"class" : "se-module se-module-map-text"})
                    place_text = map_soup.find("a")["data-linkdata"]
                    place_dict = json.loads(place_text)
                    blog_dict = {"keyword": keyword, "title": title, "link": ori_link,
                                 "placeId": int(place_dict["placeId"])}
                    place = json.dumps(place_dict).encode("utf-8")
                    blog = json.dumps(blog_dict).encode("utf-8")
                    producer.send("place_db", place)
                    producer.send("blog_db", blog)
                    print(place)
                except:
                    pass

            item_index += 1
            time.sleep(0.1)
```

### 카프카를 활용해 수집한 데이터 DB 저장 자동화

해당 프로젝트만을 진행할 예정인 경우 Kafka를 사용하지 않고 수집한 데이터를 DB에 저장하는 코드로 작성할 수 있습니다. 하지만 데이터를 수집하는 과정에서 정상적인 데이터가 들어왔는지 확인이 필요하고 또한 해당 데이터를 blog 와 place 별도의 테이블에 저장하기위해 Kafka를 통한분산데이터 처리하였습니다. 또한, 저는 해당 프로젝트를 앞으로 개선을 통해 데이터를 수집하는 과정 및 저장을 자동화할 계획이고 이 과정을 위해서 사전에 Kafka를 통해 코드를 구현하였습니다.

```python
# naver_blog.py
# kafka producer
brokers = ["localhost:9091", "localhost:9092", "localhost:9093"]
producer = KafkaProducer(bootstrap_servers=brokers)
```

```python
# place_db.py
from kafka import KafkaConsumer
import json
import pymysql

brokers = ["localhost:9091", "localhost:9092", "localhost:9093"]
consumer = KafkaConsumer("place_db", bootstrap_servers=brokers)

for message in consumer:
    db = pymysql.connect(host="localhost", port=3306, user="root", password="aksen5466!", db="todayDating",
                         charset="utf8")
    try:
        msg = json.loads(message.value.decode())

        cursor = db.cursor()
        sql = """
        INSERT IGNORE INTO place (placeId, name, address, latitude, longitude, tel) VALUES ({0}, '{1}', '{2}', {3}, {4}, '{5}');
        """.format(
            int(msg["placeId"]),
            msg["name"],
            msg["address"],
            float(msg["latitude"]),
            float(msg["longitude"]),
            msg["tel"]
        )
        print(sql)
        cursor.execute(sql)
        db.commit()
    except:
        print("Error")

    finally:
        db.close()
```

테스트를 위해 서울 지하철 2호선 내선순환 역명을 키워드로 선정하여 데이터를 수집후 DB에 저장했습니다.
![image](https://user-images.githubusercontent.com/91866763/229275125-4e6c4f22-4154-4570-a866-ab87412683c3.png)

### 카카오 채팅 봇 스킬 구현을 위한 Flask 서버 구축

*참고!! 해당 리뷰는 코드를 중점으로 작성되어 있기 때문에 카카오 채팅봇 등록 과정 등은 생략하고 진행합니다.*

카카오 챗봇을 통해 데이트 장소 정보등을 제공하기 위해서는 카카오에서 제공하는 스킬을 활용해야합니다. 해당 스킬은 JSON 데이터를 POST 방식으로 사용하며 이를 주고 받기 위해서는 서버를 구축해야합니다. 1차적인 테스트 단계에서 빠르게 작업을 진행하기 위해 구름 IDE를 통한 Flask 서버를 구축했습니다.

```python
# 구름IDE 
from flask import Flask, request, jsonify
import sys
app = Flask(__name__)

@app.route('/test', methods=["POST"])
def test():
    if request.method == "POST":
        req = request.get_json()
        print(req)
        keyword = req["action"]["params"]["Subway"]
        print(keyword)
        output = list_card(keyword)
    return jsonify(output)
```
구름 IDE를 통해 챗봇 사용을 충분히 테스트한 후 AWS 서버 구축을 진행했습니다.

### 서비스 배포를 위한 AWS EC2, RDS 활용

단순한 테스트를 위해서는 충분히 구름IDE에서 제공하는 환경으로 진행이 가능합니다. 하지만 해당 프로젝트를 개선할 단계에서 사용자 데이터와 데이트 장소 데이터를 모을 데이터 웨어하우스 구축과 실시간 데이터 처리 등을 적용해보기 위해 AWS환경에서 구현을 진행했습니다.

우선 EC2에 서버를 구축하기 위해 코드 작성 후 github를 통해 git clone을 진행했습니다.

```python
# test.py
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import search

app = Flask(__name__)

@app.route('/test', methods=["POST"])
def test():
    if request.method == "POST":
        req = request.get_json()
        keyword = req["action"]["params"]["Subway"]
        temp = search.rds(keyword)
        output = temp.find_data()
    return jsonify(output)

if __name__ == "__main__":
    app.run(host='0.0.0.0') # Flask 기본포트 5000번
```

아래 코드는 RDS에 저장되어 있는 데이터를 랜덤으로 5개 선택 후 json 형태로 챗봇에 전달하는 코드 입니다.

(문제점!!) 현재 코드는 하나의 find_data 함수에 여러 기능을 결합해 작성하여 보기에 상당히 불편한 코드입니다. 이후 마지막 장에 코드 개선을 통해 코드를 수정할 계획입니다.

```python
# search.py
# -*- coding: utf-8 -*-

import pymysql

class rds:
    def __init__(self, keyword):
        self.keyword = keyword

    def find_data(self):
        self.head = self.keyword
        db = pymysql.connect(host="",
                             port=3306,
                             user="admin",
                             password="",
                             db="todayDating",
                             charset="utf8")

        cursor = db.cursor()

        sql = "SELECT * FROM blog WHERE keyword = '{}' ORDER BY RAND() LIMIT 5;".format(self.head)

        cursor.execute(sql)
        result = cursor.fetchall()
        all_card = []
        for data in result:
            context = data[2]
            link = data[3]
            place_id = data[4]

            sql2 = "SELECT * FROM place WHERE placeId = '{}';".format(place_id)
            cursor.execute(sql2)
            temp = cursor.fetchone()
            store_name = temp[1]
            all_card.append([store_name, context, link])
        output = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": "{} 데이트 장소 입니다.".format(self.keyword)
                            },
                            "items": [
                                {
                                    "title": all_card[0][0],
                                    "description": all_card[0][1],
                                    "link": {
                                        "web": all_card[0][2]
                                    }
                                },
                                {
                                    "title": all_card[1][0],
                                    "description": all_card[1][1],
                                    "link": {
                                        "web": all_card[1][2]
                                    }
                                },
                                {
                                    "title": all_card[2][0],
                                    "description": all_card[2][1],
                                    "link": {
                                        "web": all_card[2][2]
                                    }
                                },
                                {
                                    "title": all_card[3][0],
                                    "description": all_card[3][1],
                                    "link": {
                                        "web": all_card[3][2]
                                    }
                                },
                                {
                                    "title": all_card[4][0],
                                    "description": all_card[4][1],
                                    "link": {
                                        "web": all_card[4][2]
                                    }
                                },
                            ]
                        }
                    },
                    {"simpleText": {
                        "text": "추가 검색을 원하실 경우\n키워드를 입력해주세요."}}
                ]
            }
        }
        db.close()
        return output

t = rds("왕십리")
k = t.find_data()
print(k)
```

### 결과 확인 및 프로젝트 회고
지금까지 공부한 프로그래밍을 활용하여 처음 목표했던 Today Dating 챗봇 작업을 완료했습니다. 만드는 과정에서 중간중간에 어려운 점이 몇가지 있었지만 침착하게 하나하나 원인을 찾고 문제를 해결해나가는 경험을 할 수 있었습니다. 또, 해당 프로젝트는 4월~5월 중에 사용자 데이터 실시간 처리, 데이터 웨어하우스 구축 등 추가 프로젝트를 진행할 계획이라 이 과정에서도 많은 경험을 할 수 있을 것으로 생각합니다.

이 프로젝트에서 개인적으로 반성할 점은 내가 작성한 코드지만 나도 알아보기 어려울 정도로 읽기 싫은 코드였다는 점이였습니다. 아무래도 코드를 작성한 경험이 부족하다보니 나온 문제점이라 생각하는데 이 부분에 대한 공부를 진행하여 다음 프로젝트를 진행할 때는 좀 더 보기 좋은 코드를 작성해나갈 계획입니다.

### 코드 개선

기존의 코드 작업 중 몇가지 문제점을 파악하고 이를 반영한 코드 개선을 진행했습니다.

- 파이썬 클래스 내에 클래스 메소드가 아닌 해당객체의 변수 또는 인스턴스 메소드를 만들 경우 self를 앞에 명시해야합니다. → 이 부분을 반영하여 코드를 수정했습니다.
- 일반적으로 함수에서 클린한 코드를 작성하기 위해서는 하나의 함수는 하나의 일만하는 것이 좋습니다. → 이전에 find_data 함수에서 데이터도 찾고 outdata까지 만들어서 return하였는데 이부분을 분리했습니다.
- find_data에서 분리한 함수 output_data로 작성했는데 여기서 output_data도 output 자체에도 data의 의미가 있어 중복되는 것 같고 data란 단어도 좀 더 명시적인 명칭을 사용하는게 좋을거 같다는 생각을 했습니다. → 이 부분은 아직 네이밍에 대한 경험이 부족하여 조금 더 공부한 후 수정할 계획입니다.

```python
# -*- coding: utf-8 -*-
import pymysql

class rds:
    def __init__(self, keyword):
        self.all_card = list()
        self.keyword = keyword

    def find_data(self):
        db = pymysql.connect(host="",
                             port=3306,
                             user="admin",
                             password="",
                             db="todayDating",
                             charset="utf8")

        cursor = db.cursor()

        sql = "SELECT * FROM blog WHERE keyword = '{}' ORDER BY RAND() LIMIT 5;".format(self.keyword)

        cursor.execute(sql)
        result = cursor.fetchall()
        all_card = []
        for data in result:
            context = data[2]
            link = data[3]
            place_id = data[4]

            sql2 = "SELECT * FROM place WHERE placeId = '{}';".format(place_id)
            cursor.execute(sql2)
            temp = cursor.fetchone()
            store_name = temp[1]
            all_card.append([store_name, context, link])

        db.close()
        return all_card

    def output_data(self):
        self.all_card = self.find_data()
        output = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": "{} 데이트 장소 입니다.".format(self.keyword)
                            },
                            "items": [
                                {
                                    "title": self.all_card[0][0],
                                    "description": self.all_card[0][1],
                                    "link": {
                                        "web": self.all_card[0][2]
                                    }
                                },
                                {
                                    "title": self.all_card[1][0],
                                    "description": self.all_card[1][1],
                                    "link": {
                                        "web": self.all_card[1][2]
                                    }
                                },
                                {
                                    "title": self.all_card[2][0],
                                    "description": self.all_card[2][1],
                                    "link": {
                                        "web": self.all_card[2][2]
                                    }
                                },
                                {
                                    "title": self.all_card[3][0],
                                    "description": self.all_card[3][1],
                                    "link": {
                                        "web": self.all_card[3][2]
                                    }
                                },
                                {
                                    "title": self.all_card[4][0],
                                    "description": self.all_card[4][1],
                                    "link": {
                                        "web": self.all_card[4][2]
                                    }
                                },
                            ]
                        }
                    },
                    {"simpleText": {
                        "text": "추가 검색을 원하실 경우\n키워드를 입력해주세요."}}
                ]
            }
        }

        return output
```
