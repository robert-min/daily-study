# -*- coding: utf-8 -*-
import pymysql
import secret

class rds:
    def __init__(self, keyword):
        self.all_card = list()
        self.keyword = keyword

    def find_data(self):
        db = pymysql.connect(host=secret.mysql_host,
                             port=3306,
                             user="admin",
                             password=secret.mysql_pw,
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

# testcode
# t = rds("왕십리")
# k = t.output_data()
# print(k)