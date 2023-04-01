import json
import boto3
import secret
from time import time, localtime, strftime
import pymysql
import re

s3r = boto3.resource("s3", aws_access_key_id=secret.aws_access_id, aws_secret_access_key=secret.aws_access_secret)
bucket = s3r.Bucket("today-dating")


# 어제 날짜에 모인 Json 파일 업로드
tm = localtime(time()) #  - 86400
date = strftime("%Y-%m-%d", tm)



# folder download
path = date + "/" + date

for object in bucket.objects.filter(Prefix=path):
    key = object.key
    print(key)
    body = object.get()["Body"]
    dataset = json.load(body)

    # db 저장
    db = pymysql.connect(host="localhost", port=3306, user="root", password=secret.mysql_pw, db="todayDating",
                         charset="utf8")

    cursor = db.cursor()

    remove_tag = re.compile("<.*?>&")
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
        print(sql)
        cursor.execute(sql)
    db.commit()

    db.close()