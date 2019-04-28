import hashlib
import random

import pymssql
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

# 连接数据库
serverName = '172.16.1.12\WINCC'

# 登陆用户和密码
userName = "33020"
password = "123456"

# 数据库
database = "PLK_NEW_DB"

# 连接数据库
conn = pymssql.connect(serverName, userName, password, database, autocommit=True)
cursor = conn.cursor(as_dict=True)

global wocode, batch
global TotalCount, CompleteCount


class HelloWorld(View):
    def get(self, request):
        return render(request, 'index.html')


#
#
# class Insert(View):
#     def get(self, request):
#         unit = request.GET.get('unit')
#         unitName = request.GET.get('unitName')
#         sql = f"insert into unit values ({unit}, '{unitName}')"
#         cursor.execute(sql)
#         return JsonResponse({'type': 'success'})
#
#
# class Update(View):
#     def get(self, request):
#         unit = request.GET.get('unit')
#         unitName = request.GET.get('unitName')
#         sql = f"update unit set UnitName='{unitName}' where Unit='{unit}'"
#         cursor.execute(sql)
#         return JsonResponse({'type': 'success'})
#
#
# class Delete(View):
#     def get(self, request):
#         unit = request.GET.get('unit')
#         sql = f"delete unit where Unit='{unit}'"
#         cursor.execute(sql)
#         return JsonResponse({'type': 'success'})
#
#
# class Select(View):
#     def get(self, request):
#         cursor.execute('select * from unit')
#         content = cursor.fetchall()
#         return JsonResponse({'type': 'success', 'content': content})


# class Login(View):
#     def get(self, request):
#
#         username = request.GET.get("username")
#         password = request.GET.get("password")
#         sql = f"select UserPasword from UserDate where UserName='{username}'"
#
#         # 执行数据库操作
#         cursor.execute(sql)
#
#         OutputPassword = cursor.fetchone()
#         if OutputPassword:
#             OutputPassword = OutputPassword['UserPasword'].replace(' ', '')
#
#             m1 = hashlib.md5()
#             m1.update(password.encode("utf-8"))
#             data1 = m1.hexdigest()
#
#             m2 = hashlib.md5()
#             m2.update(OutputPassword.encode("utf-8"))
#             data2 = m2.hexdigest()
#
#             print(data1)
#             print(data2)
#
#             # 密码匹配
#             if data1 == data2:
#                 role = str(random.random())
#
#                 m3 = hashlib.md5()
#                 m3.update(role.encode("utf-8"))
#                 data3 = m3.hexdigest()
#
#                 sql = f"update UserDate set [Check]='{data3}' where UserName='{username}'"
#                 cursor.execute(sql)
#                 return JsonResponse({'type': 'success', 'Role': data3})
#         else:
#             return JsonResponse({'type': 'error'})


class CheckMaterial(View):
    def get(self, request):

        # 再次声明全局变量
        global wocode, batch
        global TotalCount, CompleteCount

        # 获取前端数据
        Content = request.GET.get("Content")

        if Content == "该批次已经全部检料":
            # 清空锁定
            wocode = ""
            batch = ""

        # 获取二维码并解码
        Qrcode = str(request.GET.get("扫描的二维码"))
        QrcodeList = Qrcode.split(",")

        if len(QrcodeList) > 0:  # 判断二维码是否有效

            if QrcodeList[0] == "PL":  # 判断是否为配料二维码

                # 查询配料过程过程是否有该记录
                sql = f" select * from dbo.BurdenProcess where Id={QrcodeList[1]} "

                # 执行数据库操作
                cursor.execute(sql)
                sqlResult = cursor.fetchone()

                # 如果查询结果不为空
                if sqlResult:

                    # 如果工单号和批次号为空，将结果写入全局变量
                    if wocode == "" and batch == "":
                        wocode = sqlResult["Wocode"]
                        batch = sqlResult["WocodeBatch"]

                    # 如果全局变量和获取到的工单号和批次号相等，表示处于当前批次已经锁定
                    if wocode == sqlResult["Wocode"] and batch == sqlResult["WocodeBatch"]:
                        # 查询该配料记录是否检料
                        sql = f"select *from dbo.BurdenProcess where Id={QrcodeList[1]} and State=1;"

                        # 执行数据库操作
                        cursor.execute(sql)
                        sqlresult = cursor.fetchone()

                        # 如果查询结果不为空
                        if sqlResult:
                            # 更新检料状态
                            sql = f"update dbo.BurdenProcess set State=2 where Id={QrcodeList[1]} and State=1;"
                            cursor.execute(sql)
                        else:
                            # 返回前端
                            return JsonResponse({"Error": "该配料记录不为配料状态"})

                        # 获取该批次的已配料数
                        sql = f"select * from dbo.BurdenProcess where Wocode='{wocode}' and WocodeBatch='{batch}'and (State<>0 and State<>4) ;"
                        cursor.execute(sql)
                        sqlresult = cursor.fetchall()
                        TotalCount = len(sqlresult)

                        # 获取该批次的已检料数
                        sql = f"select * from dbo.BurdenProcess where State=2 and Wocode='{wocode}' and WocodeBatch='{batch}';"
                        cursor.execute(sql)
                        sqlresult = cursor.fetchall()
                        CompleteCount = len(sqlresult)

                        # 批次检料数量判断
                        if TotalCount == CompleteCount:

                            # 查询该工单的批次总数
                            sql = f"select * from dbo.Batch where Wocode='{wocode}';"
                            cursor.execute(sql)
                            sqlresult = cursor.fetchall()
                            TotalCount = len(sqlresult)

                            # 查询该工单的批次已检料数
                            sql = f"select * from dbo.Batch where Status=3 and Wocode='{wocode}';"
                            cursor.execute(sql)
                            sqlresult = cursor.fetchall()
                            CompleteCount = len(sqlresult)

                            # 判断工单的批次是否全部检料
                            if TotalCount == CompleteCount:
                                # 更新工单的检料状态
                                sql = f"update dbo.Wocode set Status=3 where Wocode='{wocode}' and Status=2;"
                                cursor.execute(sql)
                            else:
                                # 返回前端
                                pass
                            # 返回前端
                            return JsonResponse({"Content": "该批次已经全部检料"})

                        # 返回前端
                        return JsonResponse({"CompleteCount": CompleteCount, "TotalCount": TotalCount})

                    else:
                        # 返回前端
                        return JsonResponse({"Error": "该批次已经锁定，请选择该批次的配料记录进行检料"})
                else:
                    # 返回前端
                    return JsonResponse({"Error": "该配料记录查询结果为空"})
            else:
                # 返回前端
                return JsonResponse({"Error": "该配料记录不是配料二维码"})
        else:
            # 返回前端
            return JsonResponse({"Error": "无法解析二维码，二维码无效"})
