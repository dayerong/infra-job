#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import datetime
import time

from suds.client import Client
from suds.transport.https import HttpAuthenticated
from suds.sudsobject import asdict
import pymysql
from common.logs import Log
from config.conf import mid_db_config, sap_employee_config, sap_emp_email_config

pymysql.install_as_MySQLdb()
import MySQLdb


def recursive_asdict(d):
    """Convert Suds object into serializable format."""
    out = {}
    for k, v in asdict(d).items():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_asdict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


class OperateDB(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(**mid_db_config)
            self.cursor = self.conn.cursor()
        except Exception as err:
            print(err)

    # 写入数据库
    def impEmployeeData(self, data):
        try:
            sql = """
            INSERT INTO employee (PERNR, STAT2, ZCODE, OAUID, USRID, EMAIL, BUKRS, ORGEH, PLANS, STELL, ENAME, MPERNR, LEVEL1, LEVEL2, LEVEL3, LEVEL4, LEVEL5, BEGDA, ENDDA, ZZWLB)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS NEW_EMPLOYEE
            ON DUPLICATE KEY UPDATE
            PERNR = NEW_EMPLOYEE.PERNR, 
            STAT2 = NEW_EMPLOYEE.STAT2, 
            ZCODE = NEW_EMPLOYEE.ZCODE, 
            OAUID = NEW_EMPLOYEE.OAUID, 
            USRID = NEW_EMPLOYEE.USRID, 
            EMAIL = NEW_EMPLOYEE.EMAIL, 
            BUKRS = NEW_EMPLOYEE.BUKRS, 
            ORGEH = NEW_EMPLOYEE.ORGEH, 
            PLANS = NEW_EMPLOYEE.PLANS, 
            STELL = NEW_EMPLOYEE.STELL, 
            ENAME = NEW_EMPLOYEE.ENAME, 
            MPERNR = NEW_EMPLOYEE.MPERNR, 
            LEVEL1 = NEW_EMPLOYEE.LEVEL1, 
            LEVEL2 = NEW_EMPLOYEE.LEVEL2, 
            LEVEL3 = NEW_EMPLOYEE.LEVEL3, 
            LEVEL4 = NEW_EMPLOYEE.LEVEL4, 
            LEVEL5 = NEW_EMPLOYEE.LEVEL5, 
            BEGDA = NEW_EMPLOYEE.BEGDA, 
            ENDDA = NEW_EMPLOYEE.ENDDA, 
            ZZWLB = NEW_EMPLOYEE.ZZWLB
         """
            self.cursor.executemany(sql, data)
            self.conn.commit()
        except Exception as err:
            print(err)
            self.conn.rollback()

    # 写入数据库
    def insertHistory(self, count, begin_time, end_time):
        try:
            sql = """
            INSERT INTO emp_count_history (count,begin_time, end_time)
            VALUES ('%s', '%s','%s')
         """ % (count, begin_time, end_time)
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as err:
            print(err)
            self.conn.rollback()

    # 查询记录数
    def QueryEmployeeCount(self):
        try:
            sql = """
            SELECT 
                COUNT(1)
            FROM
                employee
            """
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            return rows
        except Exception as err:
            print(err)

    # 关闭数据库
    def conn_close(self):
        self.cursor.close()
        self.conn.close()


def getEmpFromSap():
    log = Log()
    url = sap_employee_config["url"]
    username = sap_employee_config["username"]
    password = sap_employee_config["password"]
    today = datetime.date.today()
    start_time = time.time()

    t = HttpAuthenticated(username=username, password=password)
    client = Client(url, transport=t)
    rs = client.service.ZHR_GET_EMPLOYEE(I_BEGDA=today)
    data = recursive_asdict(rs)
    data_json = data["item"]
    log.info('getEmpFromSap', '从SAP获取数据花费时间: {0}s'.format((float('%.2f' % (time.time() - start_time)))))
    return data_json


def getZcodeFromSap(mail):
    url = sap_emp_email_config["url"]
    username = sap_emp_email_config["username"]
    password = sap_emp_email_config["password"]
    today = datetime.date.today()

    t = HttpAuthenticated(username=username, password=password)
    client = Client(url, transport=t)
    rs = client.service.ZHR_GET_EMP_MAIL(I_BEGDA=today, I_EMAIL=mail.upper())
    data = recursive_asdict(rs)
    zcode = data["O_ZCODE"]
    return zcode


def impAll():
    log = Log()
    op = OperateDB()
    begin_time = datetime.datetime.now()
    data = getEmpFromSap()
    valueslist = []
    for i in enumerate(data):
        userinfo = i[1]
        values = [value for value in userinfo.values()]
        valueslist.append(tuple(values))
    op.impEmployeeData(valueslist)
    end_time = datetime.datetime.now()
    count = op.QueryEmployeeCount()[0][0]
    op.insertHistory(count, str(begin_time), str(end_time))
    op.conn_close()
    log.info('impEmpDataFromSap', 'count:{0},begin_time:{1},end_time:{2}'.format(count, str(begin_time), str(end_time)))
    return begin_time, end_time, count
