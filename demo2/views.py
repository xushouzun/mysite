from django.shortcuts import render, HttpResponse
from django.views import View
import pymssql
from django.http import JsonResponse

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


class HelloWorld(View):
    def get(self, request):
        return render(request, 'index.html')


class Insert(View):
    def get(self, request):
        unit = request.GET.get('unit')
        unitName = request.GET.get('unitName')
        sql = f"insert into unit values ({unit}, '{unitName}')"
        cursor.execute(sql)
        return JsonResponse({'type': 'success'})


class Update(View):
    def get(self, request):
        unit = request.GET.get('unit')
        unitName = request.GET.get('unitName')
        sql = f"update unit set UnitName='{unitName}' where Unit='{unit}'"
        cursor.execute(sql)
        return JsonResponse({'type': 'success'})


class Delete(View):
    def get(self, request):
        unit = request.GET.get('unit')
        sql = f"delete unit where Unit='{unit}'"
        cursor.execute(sql)
        return JsonResponse({'type': 'success'})


class Select(View):
    def get(self, request):
        cursor.execute('select * from unit')
        content = cursor.fetchall()
        return JsonResponse({'type': 'success', 'content': content})

# Create your views here.
