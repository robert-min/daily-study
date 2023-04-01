# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import search
from naver_api import NaverApi
from time import time, gmtime

# (airflow 스케줄링 작업 후 진행) kafka producer
# brokers = ["localhost:9091", "localhost:9092", "localhost:9093"]
# producer = KafkaProducer(bootstrap_servers=brokers)

app = Flask(__name__)

@app.route('/test', methods=["POST"])
def test():
    if request.method == "POST":
        req = request.get_json()
        keyword = req["action"]["params"]["Subway"]
        output = search.rds(keyword).output_data()
    return jsonify(output)

@app.route('/nokeyword', methods=["POST"])
def nokeyword():
    if request.method == "POST":
        req = request.get_json()
        keyword = req["userRequest"]["utterance"]
        # producer.send("keyword", keyword)
        output = nokeyword_output()

        # 현재 코드는 두개 이상의 저장된 키워드 중복될 시 오류 발생
        tm = gmtime(time())
        NaverApi(keyword).save_json(tm)
        NaverApi(keyword).save_list(tm)

    return jsonify(output)


def nokeyword_output():
    output = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "해당 키워드는 아직 저장되지 않았습니다. \n 1시간 후 키워드가 추가됩니다."
                            }
                        }
                    ]
                }
            }

    return output

if __name__ == "__main__":
    app.secret_key = "aksen"
    app.run(host='0.0.0.0') # Flask 기본포트 5000번
