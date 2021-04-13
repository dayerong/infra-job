#!/usr/bin/env python
# -*- encoding: utf-8 -*-


# 企业微信IT监控平台应用信息
wx_infra_config = {
    "Corpid": "",
    "Secret": "",
    "Agentid": ""
}

# 企业微信通讯同步
wx_address_list_config = {
    'Corpid': '',
    'Secret': '',
}

# log设置
log_config = {
    "logformat": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # "loglevel": "logging.INFO",
    "file": "./app/logs/app.log",
    "datefmt": "%Y/%m/%d %H:%M:%S"
}

# 中间数据库连接参数
mid_db_config = {
    'host': '',
    'port': 3306,
    'user': '',
    'passwd': '',
    'db': 'devops',
    'charset': 'utf8'
}

# SAP接口：人员信息全量查询接口
sap_employee_config = {
    "url": "",
    "username": "",
    "password": ""
}

# SAP接口： 查询邮箱接口
sap_emp_email_config = {
    "url": "",
    "username": "",
    "password": ""
}

# 同步SAP任务
sap_jobargs = {
    'id': '1',
    'trigger_type': 'cron',
    'name': 'impEmpDataFromSap',
    'schedule_time': {
        'hour': '6,12',
        'minute': 10
    }
}

# 同步微信通讯录任务
wx_jobargs = {
    'id': '2',
    'trigger_type': 'cron',
    'name': 'impAllFromWeixin',
    'schedule_time': {
        'hour': '6,12',
        'minute': 20
    }
}
