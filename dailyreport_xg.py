#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021-03-03 18:49
# @Author  : Eustiar
# @File    : dailyreport_xg.py
import requests
import datetime
import schedule
import re

sess = requests.session()
login_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xsHome'
certification_url = 'https://sso.hitsz.edu.cn:7002/cas/login?service=http://xgsm.hitsz.edu.cn/zhxy-xgzs/common/casLogin?params=L3hnX21vYmlsZS94c0hvbWU='
add_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/csh'
ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
log_path = './dailyreport_xg.log'
with open('userdata', 'r') as f:
    data = f.readlines()
    username = data[0].strip()
    password = data[1].strip()

def login():
    res = sess.get(login_url, headers=ua)
    lt = re.findall('\"lt\" value=\"(.+)\"', res.text)[0]
    execution = re.findall('\"execution\" value=\"(.+)\"', res.text)[0]
    login_data = {'username': username, 'password': password, 'lt': lt, 'execution': execution, '_eventId': 'submit',
                  'vc_username': None, 'vc_password': None}
    res = sess.post(certification_url, headers=ua, data=login_data)
    if '头部' in res.text:
        save_log('login success!')
        return True
    save_log('login failed!')
    return False

def save_log(data_log):
    with open(log_path, 'a+') as f:
        f.write('\n' + str(datetime.datetime.now()) + '\n\n' + data_log + '\n')

def work_once():
    if not login():
        print('Login failed')
        exit()
    res = sess.post(add_url, headers=ua)
    # print(res.text)
    module = res.json()['module']
    edit_url = 'http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/saveYqxx'
    formdata = {'info': '{"model":{"id":"' + module +
                        '","dqszd":"01","hwgj":"","hwcs":"",'
                        '"hwxxdz":"","dqszdsheng":"440000","dqszdshi":"440300","dqszdqu":"440305","gnxxdz":"哈工大",'
                        '"dqztm":"01","dqztbz":"","brfsgktt":"0","brzgtw":"35.5","brsfjy":"","brjyyymc":"",'
                        '"brzdjlm":"","brzdjlbz":"","qtbgsx":"","sffwwhhb":"0","sftjwhjhb":"0","tcyhbwhrysfjc":"0",'
                        '"sftzrychbwhhl":"0","sfjdwhhbry":"0","tcjtfs":"","tchbcc":"","tccx":"","tczwh":"","tcjcms":"",'
                        '"gpsxx":"","sfjcqthbwhry":"0","sfjcqthbwhrybz":"","tcjtfsbz":""}}'}
    res = sess.post(edit_url, headers=ua, data=formdata)
    if res.json()['isSuccess']:
        save_log('Add success')
    else:
        save_log('Add failed')


def work_schedule():
    schedule.clear()
    schedule.every(1).days.do(work_once)
    while True:
        schedule.run_pending()

if __name__ == '__main__':
    work_once()
    work_schedule()