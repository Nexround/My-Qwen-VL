import json
import os
import requests
import random
import json
from hashlib import md5
import time
import argparse

# Set your own appid/appkey.
appid = '20210114000671373'
appkey = 'HUyo4g1HG5ejhwx8NEX8'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path
# Create an argument parser


def parse_args():
    parser = argparse.ArgumentParser(
        description='Translate images and generate result JSON file.')

    parser.add_argument('--from_lang', type=str, default='zh',
                        help='translate from what language')
    parser.add_argument('--to_lang', type=str, default='en',
                        help='translate to what language')
    parser.add_argument('--appid', type=str)
    parser.add_argument('--appkey', type=str)
    parser.add_argument('--save_json_path', type=str)
    parser.add_argument('--source_json_path', type=str)

    args = parser.parse_args()
    return args


args = parse_args()


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def fanyi(query, args):
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': args.from_lang,
               'to': args.to_lang, 'salt': salt, 'sign': sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    translated_text = result['trans_result'][0]['dst']
    return translated_text
# print(fanyi('你好世界', args))


data = json.load(open('data.json'))
# {
#     "image_name": "",
#     "question": "",
#     "answer": ""
# },
template = {"image_name": '', "question": '', "answer": ''}
result = list()
save_file_path = 'result.json'
for index, i in enumerate(data):
    if (index % 10 == 0 and index != 0):
        print(result)
        time.sleep(1.11)  # API的QPS=10
    name_with_extension = i['data']['image']
    file_name_without_extension = os.path.splitext(
        os.path.basename(name_with_extension))[0]
    first_sentence = i["annotations"][0]["result"][0]["value"]["text"][0]
    second_sentence = i["annotations"][0]["result"][1]["value"]["text"][0]
    answer = first_sentence + second_sentence
    translated_answer = fanyi(answer, args)
    this_object = dict(template)
    this_object["image_name"] = file_name_without_extension
    this_object["answer"] = translated_answer
    this_object["question"] = 'Is there any violation of operating standards in this picture'
    result.append(this_object)
    # print("Annotated Text:", answer)
with open(save_file_path, 'w') as json_file:
    json.dump(result, json_file, indent=4)
