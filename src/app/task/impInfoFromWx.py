#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import urllib3
import pymysql
from config.conf import mid_db_config, wx_address_list_config
from common.logs import Log

urllib3.disable_warnings()

pymysql.install_as_MySQLdb()
import MySQLdb


def GetToken(Corpid, Secret):
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    para = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=url, params=para, verify=False)
    token = r.json()['access_token']
    return token


# 获取部门列表
def GetDeptList(Token, DepartmentID):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?'
    para = {
        'access_token': Token,
        'id': DepartmentID
    }
    r = requests.get(url=url, params=para, verify=False)
    info = r.json()
    return info


# 获取部门成员详情
def GetUserInfo(Token, DepartmentID, fetch_child):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?'
    para = {
        'access_token': Token,
        'department_id': DepartmentID,
        'fetch_child': fetch_child  # 1/0：是否递归获取子部门下面的成员
    }
    r = requests.get(url=url, params=para, verify=False)
    info = r.json()
    return info


class GetWeworkInfo(object):
    def __init__(self):
        corpid = wx_address_list_config['Corpid']
        secret = wx_address_list_config['Secret']
        self.token = GetToken(corpid, secret)

    # 根据工号获取部门成员详情
    def queryuserinfo(self, account):
        data = GetUserInfo(self.token, 2, 1)['userlist']

        for i in data:
            try:
                attrs = i['extattr']['attrs']
                zcodes = [i['value'] for i in attrs if i['name'] == '工号']
                zcode = ''.join(zcodes)
                if zcode == account:
                    deptid = i['main_department']
                    dept_name = self.querydeptinfo(deptid)
                    info = {
                        'name': i['name'],
                        'userid': i['userid'],
                        'mobile': i['mobile'],
                        'department': dept_name
                    }
                    return info
            except:
                continue

    # 获取部门名称
    def querydeptinfo(self, deptid):
        data = GetDeptList(self.token, deptid)

        dept_name = data['department'][0]['name']
        return dept_name

    # 根据姓名获取部门成员userid
    def queryuserid(self, username):
        data = GetUserInfo(self.token, 2, 1)['userlist']

        for i in data:
            try:
                name = i['name']
                if name == username:
                    userid = i['userid']
                    return userid
            except:
                continue

    # 获取所有部门信息
    def getalldeptinfo(self, deptid):
        data = GetDeptList(self.token, deptid)['department']

        return data

    # 根据部门获取部门成员信息
    def listuserinfo(self, department_id):
        data = GetUserInfo(self.token, department_id, 0)['userlist']

        return data

    # 根据部门获取部门成员信息
    def getalluserinfo(self, department_id):
        data = GetUserInfo(self.token, department_id, 1)['userlist']

        return data


class OperateDB(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(**mid_db_config)
            self.cursor = self.conn.cursor()
        except Exception as err:
            print(err)

    # 部门信息写入数据库
    def impDepartmentData(self, data):
        log = Log()
        try:
            sql = """
            INSERT INTO wx_department (id, name, parentid)
            VALUES (%s, %s, %s) AS NEW_DEMPT
            ON DUPLICATE KEY UPDATE
            id = NEW_DEMPT.id, 
            name = NEW_DEMPT.name, 
            parentid = NEW_DEMPT.parentid
         """
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as err:
            log.info('impDepartmentData', err)
            log.info('Detail:', data)
            self.conn.rollback()

    # 部门成员信息写入数据库
    def impEmpData(self, data):
        log = Log()
        try:
            sql = """
            INSERT INTO wx_user (userid, name, zcode, mobile, department, position, gender, status, main_department)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) AS NEW_USER
            ON DUPLICATE KEY UPDATE
            userid = NEW_USER.userid,
            name = NEW_USER.name,
            zcode = NEW_USER.zcode,
            mobile = NEW_USER.mobile,
            department = NEW_USER.department,
            position = NEW_USER.position,
            gender = NEW_USER.gender,
            status = NEW_USER.status,
            main_department = NEW_USER.main_department
         """
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as err:
            log.info('impEmpData', err)
            log.info('Detail:', data)
            self.conn.rollback()

    # 关闭数据库
    def conn_close(self):
        self.cursor.close()
        self.conn.close()


class impWxInfo(object):

    # 同步所有部门信息
    def impDeptInfo(self):
        log = Log()
        wx = GetWeworkInfo()
        data = wx.getalldeptinfo(1)
        op = OperateDB()
        for i in data:
            info = (i['id'], i['name'], i['parentid'])
            op.impDepartmentData(info)
        op.conn_close()
        log.info('impDeptInfo', 'count: {0}'.format(len(data)))

    # 按部门同步成员信息
    def impUserInfoByDept(self, dept_id):
        wx = GetWeworkInfo()
        data = wx.getalldeptinfo(dept_id)
        op = OperateDB()

        for i in data:
            department_id = i['id']

            userinfo = wx.listuserinfo(department_id)
            for d in userinfo:
                try:
                    attrs = d['extattr']['attrs']
                    zcodes = [i['value'] for i in attrs if i['name'] == '工号']
                    zcode = ''.join(zcodes)
                    info = {
                        'userid': d['userid'],
                        'name': d['name'],
                        'zcode': zcode,
                        'mobile': d['mobile'],
                        'department': ','.join('%s' % i for i in d['department']),
                        'position': d['position'],
                        'gender': d['gender'],
                        'status': d['status'],
                        'main_department': d['main_department']
                    }
                    row = tuple(info.values())
                    op.impEmpData(row)
                except:
                    zcode = ''
                    info = {
                        'userid': d['userid'],
                        'name': d['name'],
                        'zcode': zcode,
                        'mobile': d['mobile'],
                        'department': ','.join('%s' % i for i in d['department']),
                        'position': d['position'],
                        'gender': d['gender'],
                        'status': d['status'],
                        'main_department': d['main_department']
                    }
                    row = tuple(info.values())
                    op.impEmpData(row)
        op.conn_close()

    # 同步所有成员信息
    def impAllUserInfo(self):
        log = Log()
        wx = GetWeworkInfo()
        data = wx.getalluserinfo(1)
        op = OperateDB()

        for d in data:
            try:
                attrs = d['extattr']['attrs']
                zcodes = [i['value'] for i in attrs if i['name'] == '工号']
                zcode = ''.join(zcodes)
                info = {
                    'userid': d['userid'],
                    'name': d['name'],
                    'zcode': zcode,
                    'mobile': d['mobile'],
                    'department': ','.join('%s' % i for i in d['department']),
                    'position': d['position'],
                    'gender': d['gender'],
                    'status': d['status'],
                    'main_department': d['main_department']
                }
                row = tuple(info.values())
                op.impEmpData(row)
            except:
                zcode = ''
                info = {
                    'userid': d['userid'],
                    'name': d['name'],
                    'zcode': zcode,
                    'mobile': d['mobile'],
                    'department': ','.join('%s' % i for i in d['department']),
                    'position': d['position'],
                    'gender': d['gender'],
                    'status': d['status'],
                    'main_department': d['main_department']
                }
                row = tuple(info.values())
                op.impEmpData(row)
        op.conn_close()
        log.info('impAllUserInfo', 'count: {0}'.format(len(data)))
