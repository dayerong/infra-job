#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import requests
import json
import urllib3
from config.conf import wx_infra_config

urllib3.disable_warnings()


def GetToken(Corpid, Secret):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=Url, params=Data, verify=False)
    Token = r.json()['access_token']
    return Token


def SendMessage(Token, Userid, Agentid, Subject, Content):
    Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
    Data = {
        "touser": Userid,
        "msgtype": "markdown",
        "agentid": Agentid,
        "markdown": {
            "content": Subject + '\n' + Content
        },
        "safe": "0"
    }
    data = json.dumps(Data, ensure_ascii=False)
    r = requests.post(url=Url, data=data.encode('utf-8'))
    return r.json()


def SendToUser(info=None):
    Corpid = wx_infra_config['Corpid']
    Secret = wx_infra_config['Secret']
    Agentid = wx_infra_config['Agentid']
    Token = GetToken(Corpid, Secret)
    Status = SendMessage(Token, info['userid'], Agentid, info['subject'], info['content'])
    return Status


def sendStartMsg(userid, job_name):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    start_info = {
        "userid": userid,
        "subject": "`自动任务发起通知`\n",
        "content": ">**任务详情**\n > 任务名：<font color=\"comment\">{0}</font>\n > 状   态：<font color=\"info\">任务已发起</font>\n > 时   间：<font color=\"comment\">{1}</font>\n".format(
            job_name, start_time)
    }
    SendToUser(start_info)


def sendFinishMsg(userid, job_name):
    finish_time = time.strftime("%Y-%m-%d %H:%M:%S")
    finish_info = {
        "userid": userid,
        "subject": "`自动任务完成通知`\n",
        "content": ">**任务详情**\n > 任务名：<font color=\"comment\">{0}</font>\n > 状   态：<font color=\"info\">任务已完成</font>\n > 时   间：<font color=\"comment\">{1}</font>\n".format(
            job_name, finish_time)
    }
    SendToUser(finish_info)


def sendErrorMsg(userid, job_name, err):
    job_time = time.strftime("%Y-%m-%d %H:%M:%S")
    start_info = {
        "userid": userid,
        "subject": "`自动任务失败通知`\n",
        "content": ">**任务详情**\n > 任务名：<font color=\"comment\">{0}</font>\n > 状   态：<font color=\"warning\">任务失败</font>\n > 时   间：<font color=\"comment\">{1}</font>\n >错   误：<font color=\"warning\">{2}</font>\n".format(
            job_name, job_time, err)
    }
    SendToUser(start_info)


def sendMainError(userid, err):
    job_time = time.strftime("%Y-%m-%d %H:%M:%S")
    start_info = {
        "userid": userid,
        "subject": "`自动任务失败通知`\n",
        "content": ">**失败详情**\n > 状   态：<font color=\"comment\">任务进程异常</font>\n > 时   间：<font color=\"info\">{0}</font>\n >错   误：<font color=\"warning\">{1}</font>\n".format(
            job_time, err)
    }
    SendToUser(start_info)
