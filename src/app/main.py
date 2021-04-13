#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from apscheduler.schedulers.blocking import BlockingScheduler
from config.conf import sap_jobargs, wx_jobargs
from task import impEmpFromSap, impInfoFromWx
from common.sendWxMsg import *


# 同步SAP员工信息数据
def impEmpDataFromSap(userid, job_name):
    sendStartMsg(userid, job_name)
    try:
        impEmpFromSap.impAll()
        sendFinishMsg(userid, job_name)
    except Exception as err:
        sendErrorMsg(userid, job_name, err)


# 同步企业微信通讯录部门及员工信息
def impAllFromWeixin(userid, job_name):
    sendStartMsg(userid, job_name)
    try:
        wx = impInfoFromWx.impWxInfo()
        wx.impDeptInfo()
        wx.impAllUserInfo()
        sendFinishMsg(userid, job_name)
    except Exception as err:
        sendErrorMsg(userid, job_name, err)


def start_jobs(userid):
    scheduler = BlockingScheduler()
    scheduler.add_job(func=impEmpDataFromSap, trigger=sap_jobargs['trigger_type'], id=sap_jobargs['id'],
                      **sap_jobargs['schedule_time'], args=(userid, sap_jobargs['name']))

    scheduler.add_job(func=impAllFromWeixin, trigger=wx_jobargs['trigger_type'], id=wx_jobargs['id'],
                      **wx_jobargs['schedule_time'], args=(userid, wx_jobargs['name']))

    try:
        scheduler.start()
    except Exception as err:
        sendMainError(userid, err)


if __name__ == '__main__':
    receiver = 8333
    start_jobs(receiver)
