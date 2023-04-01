# -*- coding: utf-8 -*-

import json
import boto3
import secret
from time import time, gmtime, strftime
import pymysql
import re

s3r = boto3.resource("s3", aws_access_key_id=secret.aws_access_id, aws_secret_access_key=secret.aws_access_secret)
bucket = s3r.Bucket("today-dating")


# 한시간 전 파일
tm = gmtime(time()) #  - 6600
date = strftime("%Y-%m-%d", tm)
file_name = strftime("%H", tm)

print(file_name)

# folder download
path = date + "/" + file_name

for object in bucket.objects.filter(Prefix=path):
    key = object.key
    print(key)
    body = object.get()["Body"]
    dataset = json.load(body)

    # db 저장
    db = pymysql.connect(host=secret.mysql_host, port=3306, user="admin", password=secret.mysql_pw, db="todayDating",
                         charset="utf8")

    cursor = db.cursor()

    remove_tag = re.compile("<.*?>")
    for i in range(len(dataset.keys()) - 1):
        title = re.sub(remove_tag, "", dataset[str(i)]["blog"]["title"])
        title = title.replace("'", "")
        title = title.replace('"', '')

        try:
            sql = "INSERT IGNORE INTO blog (keyword, title, link, placeId) VALUES ('{0}', '{1}', '{2}', {3});".format(
                dataset["keyword"],
                title,
                dataset[str(i)]["blog"]["link"],
                int(dataset[str(i)]["place"]["placeId"])
            )
        except:
            sql = "INSERT IGNORE INTO blog (keyword, title, link) VALUES ('{0}', '{1}', '{2}');".format(
                dataset["keyword"],
                title,
                dataset[str(i)]["blog"]["link"]
            )
        cursor.execute(sql)
        try:
            sql = """
            INSERT IGNORE INTO place (placeId, name, address, latitude, longitude, tel) VALUES ({0}, '{1}', '{2}', {3}, {4}, '{5}');
            """.format(
                int(dataset[str(i)]["place"]["placeId"]),
                dataset[str(i)]["place"]["name"],
                dataset[str(i)]["place"]["address"],
                float(dataset[str(i)]["place"]["latitude"]),
                float(dataset[str(i)]["place"]["longitude"]),
                dataset[str(i)]["place"]["tel"]
        )
        except:
            pass
        cursor.execute(sql)

    db.commit()

    db.close()