import boto3
import secret
import os
from time import time, localtime, strftime


def upload_file_s3(bucket_name, path, date):
    # aws
    ACCESS_KEY = secret.aws_access_id
    SECRET_KEY = secret.aws_access_secret

    s3 = boto3.client("s3", aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)

    file_list = os.listdir(path)
    file_list_json = [file for file in file_list if file.endswith((".json", ".txt"))]

    for index, file in enumerate(file_list_json):
        try:
            with open(path + "/" + file, "rb") as data:
                s3.put_object(Bucket=bucket_name,
                              Body=data,
                              Key=date + "/" + file)
        except:
            return print("error")



if __name__ == '__main__':

    # 어제 날짜에 모인 Json 파일 업로드
    tm = localtime(time())  #  - 86400
    date = strftime("%Y-%m-%d", tm)

    path = "./date_data/" + date
    bucket = "today-dating"
    upload_file_s3(bucket, path, date)

