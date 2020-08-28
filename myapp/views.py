from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from myapp import models
import re, datetime, time

# Create your views here.

baseList = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


# 10进制转62进制
def changeBase(n, b):
    # 返回一个包含商和余数的元组(n // b, n % b)
    x, y = divmod(n, b)
    print(x, y)
    if x > 0:
        return changeBase(x, b) + baseList[y]
    else:
        return baseList[y]


# 利用mysql数据库的自增id生成n，然后转成62进制，再将62进制应对的长url存进mysql，下次访问时查询62进制的短url对应的长url，
# 最后重定向301到长url上

def index(request):
    if request.method == "GET":
        return render(request, "index.html")


def url(request, url):
    if request.method == "GET":
        res = models.ShortUrl.objects.filter(short_url=url).first()
        if not res or not res.ori_url:
            return HttpResponse("没有此短网址")
        if time.time() - int(time.mktime(res.period.timetuple())) > 0:
            return HttpResponse("短网址已失效")
        return redirect(res.ori_url)
    if request.method == "POST":
        return HttpResponse("Request error")


def addShortUrl(request):
    if request.is_ajax():
        response = {"status": 100, "msg": None}
        long = request.POST.get('long')
        period = request.POST.get('period')
        print(long, period)
        res = re.search("^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&%\$\-]+)*@)?"
                        "((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\."
                        "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\."
                        "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\."
                        "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|"
                        "([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,4})(\:[0-9]+)?"
                        "(/[^/][a-zA-Z0-9\.\,\?\'\\/\+&%\$#\=~_\-@]*)*$", long)
        if not res:
            response["msg"] = "网址错误"
            response["status"] = 101
        elif period != "一年期" and period != "长期":
            response["msg"] = "有效期格式错误"
            response["status"] = 102
        else:
            date = datetime.datetime.now()
            if period == "一年期":
                date = datetime.datetime.now() + datetime.timedelta(days=365)
            if period == "长期":
                date = datetime.datetime.now() + datetime.timedelta(days=365 * 5)
            res = models.ShortUrl.objects.create(period=date)
            print(res.id)
            n = res.id
            short_url = changeBase(n, 62)
            if short_url == "admin" or short_url == "addShortUrl" or short_url == "restoreUrl":
                response["msg"] = "请求再转换一次试试"
                response["status"] = 103
            else:
                models.ShortUrl.objects.filter(id=n).update(short_url=short_url, ori_url=long)
                response["msg"] = short_url

        return JsonResponse(response)
    if request.method == "GET":
        return HttpResponse("No get method")


def restoreUrl(request):
    if request.is_ajax():
        response = {"status": 100, "msg": None}
        short = request.POST.get('short')
        res = re.search("^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&%\$\-]+)*@)?"
                        "((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\."
                        "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\."
                        "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\."
                        "(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|"
                        "([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,4})(\:[0-9]+)?"
                        "(/[^/][a-zA-Z0-9\.\,\?\'\\/\+&%\$#\=~_\-@]*)*$", short)
        if not res or "/" not in short:
            response["msg"] = "网址错误"
            response["status"] = 101

        else:
            short_url = short.split("/")[-1]
            res = models.ShortUrl.objects.filter(short_url=short_url).first()
            print(res)
            if not res:
                response["msg"] = "没有该短网址"
                response["status"] = 102
            else:
                response["msg"] = res.ori_url

        return JsonResponse(response)
