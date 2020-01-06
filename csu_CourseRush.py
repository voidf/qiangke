import requests
import json
import os
import time
import re
import base64
import sys
import copy
import threading
import platform as pf
import termcolor
# try:
#     from pynput.keyboard import Listener
# except:
#     if pf.system() == "Windows":
#         os.system("pip install pynput")
#     else:
#         os.system("pip3 install pynput")
#     from pynput.keyboard import Listener


# def press_interrupt(key_down):
#     termcolor.cprint(key_down.char,'yellow')
#     if key_down.char == 'p':
#         try:
#             if any(thread_list):
#                 for i in thread_list:
#                     i.suicide()
#         except:
#             pass

# with Listener(on_press=press_interrupt) as l:
#     pass

def YNSelection(YNKey, defaultVal):
    if YNKey.lower() in ['y', 'yes', 'ye', 'true', 'ok', 'hai']:
        return True
    elif YNKey.lower() in ['n', 'not', 'non', 'no', 'nope', 'false', 'iie', 'iya']:
        return False
    else:
        return defaultVal


class MutithreadRush(threading.Thread):
    def __init__(self, tlnk):
        threading.Thread.__init__(self, daemon=True)
        self.is_interrupted = False
        self.lnk = tlnk

    def run(self):
        global ses

        if self.is_interrupted == False:
            try:
                do_result = ses.get(self.lnk, timeout=2)
                print(do_result.text, threading.current_thread().name)
            except Exception as e:
                print(e, threading.current_thread().name)

            try:
                do_json = json.loads(do_result.text)
                while do_json["success"] != True:
                    if self.is_interrupted:
                        return
                    try:
                        do_result = ses.get(self.lnk, timeout=1)
                        do_json = json.loads(do_result.text)
                        print(do_json)
                    except Exception as ex:
                        print(ex, threading.current_thread().name)
                        print("于while内部错误")
                print("抢课成功，命令回显:", do_json)
            except Exception as e:
                print(e, threading.current_thread().name)
                print("错误断点2,自动运行rec")
                fixCookie()
                refreshCourses()
                self.run()

    def suicide(self):
        self.is_interrupted = True


try:
    import tkinter
    from tkinter import ttk
    guiFlag = True
except:
    print("导入tk库失败，图形预览不可用")
    guiFlag = False
getList_dt = {
    "sEcho": "1",
    "iColumns": "13",
    "sColumns": "",
    "iDisplayLength": "9999",
    "iDisplayStart": "0",
    "mDataProp_0": "kch",
    "mDataProp_1": "kcmc",
    "mDataProp_2": "ktmc",
    "mDataProp_3": "xf",
    "mDataProp_4": "skls",
    "mDataProp_5": "sksj",
    "mDataProp_6": "skdd",
    "mDataProp_7": "xkrs",
    "mDataProp_8": "syrs",
    "mDataProp_9": "xxrs",
    "mDataProp_10": "ctsm",
    "mDataProp_11": "xkbtf",
    "mDataProp_12": "czOper"
}


def resource_path(relative_path):
    if pf.system() == "Windows":
        p = sys.argv[0]
        p = p[:p.rfind('\\')+1]
        return p+relative_path
    elif pf.system() == "Linux":
        relative_path = relative_path.replace("\\", "/")
        return sys.path[0]+'/'+relative_path
    else:
        relative_path = relative_path.replace("\\", "/")
        return sys.path[0]+relative_path


def ErrorPrint(errmsg, *extramsg):
    termcolor.cprint(errmsg, 'red')
    if any(extramsg):
        for i in extramsg:
            termcolor.cprint(i, 'red')


def refreshSession():
    global ses
    ses = requests.session()
    ses.headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "http://jwctest.its.csu.edu.cn",
        "Host": "jwctest.its.csu.edu.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    ses.get(
        url="http://csujwc.its.csu.edu.cn/jsxsd/"
    )  # 拿JSESSIONID和BIGipServerpool_jwctest


refreshSession()


def reAuth():
    ses.post(url="http://csujwc.its.csu.edu.cn/jsxsd/xk/LoginToXk", data=AuthData)


try:  # 懒人认证功能
    authFile = open(resource_path("auth.log"), "r")
    conf1 = input("使用上次的身份验证？[Use previous authenticate?](Y/n)")
    if YNSelection(conf1, True):
        a = authFile.readlines()
        username_verify = base64.b64decode(a[0]).decode('utf-8')

        AuthData = {"encoded": bytes(
            a[0], "utf-8")+b'%%%'+bytes(a[1], "utf-8")}
        reAuth()
    else:
        raise NameError("Manual Auth")
    authFile.close()
except Exception as e:
    ErrorPrint(e)
    id = input("请输入账号：\n")
    username_verify = id
    id = bytes(id, encoding='utf-8')
    pwd = input("输入密码：\n")
    pwd = bytes(pwd, encoding='utf-8')
    # 登录
    AuthData = {'encoded': base64.b64encode(
        id) + b'%%%' + base64.b64encode(pwd)}
    reAuth()
    with open(resource_path("auth.log"), "w") as f:
        f.write(str(base64.b64encode(id), "utf-8") +
                "\n" + str(base64.b64encode(pwd), "utf-8"))

Courses = []
GX_Courses = []
Ori_Courses = []
Ori_GX_Courses = []


def refreshCourses():
    global Courses
    global GX_Courses
    global Ori_Courses
    global Ori_GX_Courses
    Ori_Courses = []

    Ori_GX_Courses = []
    # ses.headers["Referer"]="http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk"
    getList_res = ses.post(getList_lnk, data=getList_dt)
    GXgetList_res = ses.post(GX_lnk, data=getList_dt)
    print("=====================")

    getList_json = json.loads(getList_res.text)
    GXgetList_json = json.loads(GXgetList_res.text)
    GX_Courses = Ori_GX_Courses = saveCourse("GXcourses.bak", GXgetList_json)
    Courses = Ori_Courses = saveCourse("courses.bak", getList_json)

# ctsm 冲突说明


def saveCourse(save_path, save_json):
    TEMP_Courses = []
    try:
        with open(resource_path(save_path), "w") as fbak:
            pass
        for i in save_json["aaData"]:
            try:
                if i["szkcflmc"] is not None:
                    TEMP_Courses.append({
                        "Lesson_Name": i["kcmc"],
                        "Lesson_Type": i["szkcflmc"],  # szkcflmc kcxzmc
                        "Teachers": i["skls"],
                        "Study_Score": i["xf"],
                        "Time": i["sksj"],
                        "Place": i["skdd"],
                        "Remain": i["syrs"],
                        "Max": i["xxrs"],
                        # "Subsidy": i["xkbtf"],  # 补贴分
                        "Request_ID": i["jx0404id"]
                    })
                elif "kcxzmc" in i:
                    TEMP_Courses.append({
                        "Lesson_Name": i["kcmc"],
                        "Lesson_Type": i["kcxzmc"],
                        "Teachers": i["skls"],
                        "Study_Score": i["xf"],
                        "Time": i["sksj"],
                        "Place": i["skdd"],
                        "Remain": i["syrs"],
                        "Max": i["xxrs"],
                        "Request_ID": i["jx0404id"]
                    })
                else:
                    TEMP_Courses.append({
                        "Lesson_Name": i["kcmc"],
                        "Lesson_Type": '分类不可用',
                        "Teachers": i["skls"],
                        "Study_Score": i["xf"],
                        "Time": i["sksj"],
                        "Place": i["skdd"],
                        "Remain": i["syrs"],
                        "Max": i["xxrs"],
                        "Request_ID": i["jx0404id"]
                    })
                # print(json.dumps(TEMP_Courses[-1])+"\n")
                with open(resource_path(save_path), "a") as fbak:
                    fbak.write(json.dumps(TEMP_Courses[-1])+"\n")
            except Exception as e:
                ErrorPrint(e, "Error occurred at", i)
        termcolor.cprint("Done!Results are in "+save_path, 'green')
    except Exception as e:
        ErrorPrint(e, "save Courses failed!")
    return TEMP_Courses


def fixCookie():
    retryTime = 0
    while 1:
        res = ses.get("http://csujwc.its.csu.edu.cn/jsxsd/xsxk/xklc_list")
        if res.text.find(username_verify) == -1:
            reAuth()
        URLs = re.findall(
            r'<a\shref="(.*?)"\starget="blank">进入选课</a>', res.text)
        if len(URLs) > 1:
            for i in range(len(URLs)):
                print(i, URLs[i])
            try:
                ress = ses.get("http://csujwc.its.csu.edu.cn"+URLs[int(
                    input("进入哪个选课页？输入序号。[Use which select page?Enter the num_tag]:"))])
                break
            except Exception as e:
                ErrorPrint(e)
        elif len(URLs) == 1:
            ress = ses.get("http://csujwc.its.csu.edu.cn"+URLs[0])
            break
        else:
            print("等待选课系统开放中...已经尝试%d次" % retryTime)
            time.sleep(5)
            retryTime += 1

    getFakeList_lnk = "http://jwctest.its.csu.edu.cn" + \
        re.findall(
            '''<a href="(.*?)" target="mainFrame">本学期计划选课</a>.*?''', ress.text)[0]
    GXList_lnk = "http://jwctest.its.csu.edu.cn" + \
        re.findall(
            '''<a href="(.*?)" target="mainFrame">公选课选课</a>.*?''', ress.text)[0]
    tempR = ses.get(getFakeList_lnk).text
    tempG = ses.get(GXList_lnk).text

    global getList_lnk  # 专选课
    global GX_lnk  # 公选课
    GX_lnk = "http://jwctest.its.csu.edu.cn" + \
        re.findall('''"sAjaxSource":"(.*?)"\\+param,.*?''',
                   tempG)[0]+"?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false"
    getList_lnk = "http://jwctest.its.csu.edu.cn" + \
        re.findall('''"sAjaxSource":"(.*?)"\\+param,.*?''',
                   tempR)[0]+"?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false"

    # kcxx 课程信息
    # skls 上课老师
    # skxq 上课星期
    # skjc 上课节次
    # sfym 是否已满
    # sfct 是否冲突


try:  # 查询可选课程列表
    with open(resource_path("courses.bak"), "r") as f:
        conf1 = input("使用上次的选课查询结果？[Use previous query result?](Y/n)")
        if YNSelection(conf1, True):
            for i in f.readlines():
                Ori_Courses.append(json.loads(i))
            with open(resource_path("GXcourses.bak"), "r") as fGX:
                for i in fGX.readlines():
                    Ori_GX_Courses.append(json.loads(i))
            Courses = copy.deepcopy(Ori_Courses)
            GX_Courses = copy.deepcopy(Ori_GX_Courses)
        else:
            raise NameError("Redo query")
except Exception as e:
    ErrorPrint(e)
    # 获取选课查询链接
    fixCookie()

    refreshCourses()


def SingleRush(TEMP_sel=[], TEMP_gxsel=[]):
    global ses
    try:
        try:
            retry_time = 0
            while any(TEMP_gxsel) or any(TEMP_sel):
                try:
                    if retry_time == 5:
                        if YNSelection(input("已经尝试了5次了，继续执行直到抢到为止吗(y/N)?"), False):
                            pass
                        else:
                            ErrorPrint("用户终止")
                            return
                    for ind, i in enumerate(TEMP_sel):
                        lnk = 'http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper?jx0404id=%d&xkzy=&trjf=' % i
                        do_result = ses.get(lnk, timeout=1)
                        do_json = json.loads(do_result.text)
                        
                        if do_json["success"] == True:
                            termcolor.cprint("课号%d抢课成功"%TEMP_sel.pop(ind),'green')
                            
                            retry_time = 0
                            break
                        print(do_json,i)

                    for ind, i in enumerate(TEMP_gxsel):
                        lnk = 'http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper?jx0404id=%d&xkzy=&trjf=' % i
                        do_result = ses.get(lnk, timeout=1)
                        do_json = json.loads(do_result.text)
                        
                        if do_json["success"] == True:
                            termcolor.cprint("课号%d抢课成功"%TEMP_gxsel.pop(ind),'green')
                            retry_time = 0
                            break  # pop破坏了列表结构，因此终止
                        print(do_json,i)
                    retry_time += 1

                except Exception as ex:
                    ErrorPrint(ex, "于while内部错误")
                    if do_result.status_code != 200:
                        raise NameError("Non 200 Response")
            
        except Exception as e:
            ErrorPrint(e, "错误断点2,自动运行rec")
            fixCookie()
            refreshCourses()
            SingleRush(lnk)
    except KeyboardInterrupt:
        termcolor.cprint("通过键盘打断,抢课终止", 'yellow')


current_time_table = []
free_time = []


def GetCurrentCoursesList():
    reAuth()
    fixCookie()
    courses_list_html = ses.get(
        "http://csujwc.its.csu.edu.cn/jsxsd/xsxkjg/xsxkkb")
    info_table = re.findall(
        '''<tbody>(.*?)</tbody>.*?''', courses_list_html.text, re.S)[0]
    global current_time_table
    global free_time
    free_time = []
    current_time_table = []
    for i, per_time in enumerate(re.findall('''<tr(.*?)</tr>.*?''', info_table, re.S)):
        TEMP_course_time = []
        for ind, per_cell in enumerate(re.findall('''<td>(.*?)</td>.*?''', per_time, re.S)):
            # if ind == 0:
            #     continue
            TEMP_course_time.append(per_cell)
            if per_cell == "&nbsp;":
                # 前一位是这天第几节课，后一位是星期几 free time format by (course_schedule-1,week_day-1)
                free_time.append((i, ind))
        current_time_table.append(TEMP_course_time)
    # print(free_time)


def AutoTimeFiltration(TEMP_free_table, TEMP_C):
    ind = 0
    m = {
        "一": 0,
        "二": 1,
        "三": 2,
        "四": 3,
        "五": 4,
        "六": 5,
        "日": 6
    }
    while ind < len(TEMP_C):
        try:
            if (int(re.findall(''' \d-(.*?)节.*?''', TEMP_C[ind]["Time"])[0])//2-1,
                    m[re.findall('''星期(.*?) .*?''', TEMP_C[ind]["Time"])[0]]) not in TEMP_free_table:
                TEMP_C.pop(ind)
                ind -= 1

        except Exception as e:
            if TEMP_C[ind]["Time"] == "&nbsp;":
                pass
            else:
                ErrorPrint(e, TEMP_C[ind], TEMP_C[ind]["Time"])
        ind += 1
    return TEMP_C


def AutoFullFiltration(TEMP_C):
    ind = 0
    while ind < len(TEMP_C):
        if TEMP_C[ind]["Remain"] == '0':
            TEMP_C.pop(ind)
            ind -= 1
        ind += 1
    return TEMP_C


def ManualFiltration(TEMP_k, TEMP_dictK, TEMP_C):
    ind = 0
    while ind < len(TEMP_C):
        if TEMP_k not in TEMP_C[ind][TEMP_dictK]:
            TEMP_C.pop(ind)
            ind -= 1
        ind += 1
    return TEMP_C


def TerminalShow(TEMP_C):
    print('{0:<4.4}{1:{10}<12.12}\t{2:{10}<7.7}{3:{10}<7.7}\t{4:{10}<2.2}\t{5:{10}<16.16}{6:{10}<8.8}\t{7:<5.5}{8:<5.5}{9:<15.15}'.format(
        "下标", "课名", "类型", "教师", "学分", "时间", "地点", "剩余人数", "人数上限", "请求ID", chr(12288)))
    for i in range(len(TEMP_C)):
        print('{0:<4.4}{1:{10}<12.12}\t{2:{10}<7.7}{3:{10}<7.7}\t{4:{10}<2.2}\t{5:{10}<16.16}{6:{10}<12.12}\t{7:<5.5}{8:<5.5}{9:<15.15}'.format(
            str(i), str(TEMP_C[i]["Lesson_Name"]), str(TEMP_C[i]["Lesson_Type"]), str(
                TEMP_C[i]["Teachers"]), str(TEMP_C[i]["Study_Score"]), TEMP_C[i]
            ["Time"], str(TEMP_C[i]["Place"]), str(TEMP_C[i]["Remain"]), str(TEMP_C[i]["Max"]), str(TEMP_C[i]["Request_ID"]), chr(12288)))


def TkinterShow(TEMP_C):
    rt = tkinter.Tk()
    rt.title("Courses Graphic View")
    rt.geometry("1700x900")
    tree_view = ttk.Treeview(rt)
    tree_view["columns"] = ["i", "n", "c", "t",
                            "s", "ti", "p", "r", "m", "su", "rid"]
    tree_view.pack(expand=1, fill="both")
    tree_view.column("i", width=30)
    tree_view.column("n", width=150)
    tree_view.column("c", width=150)
    tree_view.column("t", width=90)
    tree_view.column("s", width=30)
    tree_view.column("ti", width=400)
    tree_view.column("p", width=150)
    tree_view.column("r", width=50)
    tree_view.column("m", width=50)
    tree_view.column("su", width=30)
    tree_view.column("rid", width=150)
    tree_view.heading("i", text="下标")
    tree_view.heading("n", text="课名")
    tree_view.heading("c", text="类型")
    tree_view.heading("t", text="教师")
    tree_view.heading("s", text="学分")
    tree_view.heading("ti", text="时间")
    tree_view.heading("p", text="地点")
    tree_view.heading("r", text="剩余人数")
    tree_view.heading("m", text="人数上限")

    tree_view.heading("rid", text="请求id")
    for i in range(len(TEMP_C)):
        tree_view.insert("", i, values=(i, TEMP_C[i]["Lesson_Name"], TEMP_C[i]["Lesson_Type"], TEMP_C[i]["Teachers"], TEMP_C[i]["Study_Score"],
                                        TEMP_C[i]["Time"], TEMP_C[i]["Place"], TEMP_C[i]["Remain"], TEMP_C[i]["Max"], TEMP_C[i]["Request_ID"]))
    rt.mainloop()

def EchoHelp():
    print('{0:<7}{1:<22}{2}'.format("简写", "命令", "说明"))
    print('{0:<7}{1:<22}{2}'.format("h", "help", "打印此帮助信息,红色慎用"))
    print()
    print('{0:<7}{1:<22}{2}'.format("f", "filter", "自动过滤设置"))
    print('{0:<7}{1:<22}{2}'.format("fm", "manualfilter", "手动关键词过滤设置"))
    print('{0:<7}{1:<22}{2}'.format("fr", "filterreset", "过滤重置"))
    print()
    print('{0:<7}{1:<22}{2}'.format("s", "select", "输入欲选专业课的下标序号（在新的一行里）"))
    print('{0:<7}{1:<22}{2}'.format("sa", "selectall", "全选当前专业课列表，建议配合手动过滤"))
    print('{0:<7}{1:<22}{2}'.format(
        "sg", "selectgx", "输入欲选公选课的下标序号（在新的一行里）"))
    print('{0:<7}{1:<22}{2}'.format("sga", "selectgxall", "全选当前公选课列表，建议配合手动过滤"))
    print('{0:<7}{1:<22}{2}'.format("sl", "selectlist", "查看已选"))
    print()
    print('{0:<7}{1:<22}{2}'.format("rec", "refreshcourses", "重新获取可选课列表"))
    print('{0:<7}{1:<22}{2}'.format("rea", "refreshauth", "重新登录"))
    print()
    print('{0:<7}{1:<22}{2}'.format("sh", "show", "命令行展示可选专选课列表，请确保命令框够大"))
    print('{0:<7}{1:<22}{2}'.format(
        "shg", "showgx", "命令行展示可选公选课列表，请确保命令框够大"))
    print('{0:<7}{1:<22}{2}'.format(
        "stk", "showintkinter", "用tk库展示可选专选课列表"))
    print('{0:<7}{1:<22}{2}'.format(
        "stkg", "showgxintkinter", "用tk库展示可选公选课列表"))
    print('{0:<7}{1:<22}{2}'.format("d", "do", "开始抢课，使用前请先用s设置目的课"))
    print()
    termcolor.cprint('{0:<7}{1:<22}{2}'.format(
        "res", "refreshsession", "重新获取会话，用后自动重新登录"), 'red')
    termcolor.cprint('{0:<7}{1:<22}{2}'.format(
        "e", "eval", "进入eval命令执行模式，调试用"), 'red')
    termcolor.cprint('{0:<7}{1:<22}{2}'.format(
        "dm", "dowithmutithread", "实验性多线程抢课"), 'red')
    print()
    print('{0:<7}{1:<22}{2}'.format("c", "curlist", "打印当前课表"))
    print('{0:<7}{1:<22}{2}'.format("q", "quit", "退出"))

select_code = []
select_g_code = []
_temp_list = []
_temp_g_list = []

termcolor.cprint("表格数据建立完成", 'green')
termcolor.cprint("伪交互模块启动，输入help或者h查看帮助", 'green')

filter_map = {
    'ln': "Lesson_Name",
    'lt': "Lesson_Type",
    't': "Teachers",
    's': "Study_Score",
    'ti': "Time",
    'p': "Place",
    'r': "Remain",
    'm': "Max",
    'ri': "Request_ID"
}

while 1:
    cmd = input(">>>").lower()
    if cmd in ["h", "help"]:
        EchoHelp()
    elif cmd in ["f", "filter"]: # 可预吟唱

        GetCurrentCoursesList()
        if YNSelection(input("自动过滤时间有冲突课程？(Y/n)"), True):
            Courses = AutoTimeFiltration(free_time, Courses)
            GX_Courses = AutoTimeFiltration(free_time, GX_Courses)
        if YNSelection(input("自动过滤人数已满课程？(Y/n)"), True):
            Courses = AutoFullFiltration(Courses)
            GX_Courses = AutoFullFiltration(GX_Courses)
    elif cmd in ["fm", "manualfilter"]: # 可预吟唱
        print("筛选出上课地点为414的命令示例:\np 414")
        print("可用条目:")
        for k, v in filter_map.items():
            print("\t", k, ' : ', v)
        filter_rule = input("请选择一个条目，输入过滤关键词：").split(' ')
        if filter_rule[0] not in filter_map:
            termcolor.cprint("无效的条目简写:"+filter_rule[0], 'red')
        else:
            Courses = ManualFiltration(
                filter_rule[1], filter_map[filter_rule[0]], Courses)
            GX_Courses = ManualFiltration(
                filter_rule[1], filter_map[filter_rule[0]], GX_Courses)
    elif cmd in ["fr", "filterreset"]: # 可预吟唱
        Courses = copy.deepcopy(Ori_Courses)
        GX_Courses = copy.deepcopy(Ori_GX_Courses)
    elif cmd in ["e", "eval"]:
        termcolor.cprint("eval模式已启动，输入q回到上级", 'yellow')
        try:
            while 1:
                termcolor.cprint(">>>", 'yellow', end='')
                evalcmd = input()
                if evalcmd == "q":
                    break
                else:
                    termcolor.cprint(eval(evalcmd), 'cyan')
        except KeyboardInterrupt:
            termcolor.cprint("键盘打断，回到上级", 'yellow')
    elif cmd in ["sl", "selectlist"]:
        termcolor.cprint("专选课:", 'cyan')
        TerminalShow(_temp_list)
        print()
        termcolor.cprint("公选课:", 'cyan')
        TerminalShow(_temp_g_list)
    elif cmd in ["s", "select"]: # 可预吟唱
        try:
            _temp_inp = input("下标序号（从零开始的，并不是行号，以空格隔开）:").split(' ')
            _temp_list = []
            for _temp_per_inp in _temp_inp:
                select_code.append(int(Courses[int(_temp_per_inp)]["Request_ID"]))
                _temp_list.append(Courses[int(_temp_per_inp)])
            termcolor.cprint(select_code, 'yellow')
        except Exception as e:
            ErrorPrint(e, "更新选课代码失败")
    elif cmd in ["sa","selectall"]: # 可预吟唱
        _temp_list=Courses
        select_code=[]
        for i in _temp_list:
            select_code.append(i["Request_ID"])
    elif cmd in ["sga","selectgxall"]: # 可预吟唱
        _temp_g_list=GX_Courses
        select_g_code=[]
        for i in _temp_g_list:
            select_g_code.append(i["Request_ID"])
    elif cmd in ["sg", "selectgx"]: # 可预吟唱
        try:
            _temp_inp = input("下标序号（从零开始的，并不是行号，以空格隔开）:").split(' ')
            _temp_g_list = []
            for _temp_per_inp in _temp_inp:
                select_g_code.append(int(GX_Courses[int(_temp_per_inp)]["Request_ID"]))
                _temp_g_list.append(GX_Courses[int(_temp_per_inp)])
            termcolor.cprint(select_g_code, 'yellow')
        except Exception as e:
            ErrorPrint(e, "更新选课代码失败")
    elif cmd in ["rec", "refreshcourses"]: # 可预吟唱
        fixCookie()
        refreshCourses()
    elif cmd in ["rea", "refreshauth"]: # 可预吟唱
        reAuth()
    elif cmd in ["res", "refreshsession"]: # 可预吟唱
        refreshSession()
        reAuth()
    elif cmd in ["sh", "show"]:
        TerminalShow(Courses)
    elif cmd in ["shg", "showgx"]:
        TerminalShow(GX_Courses)
    elif cmd in ["stk", "showintkinter"]:
        if guiFlag == False:
            termcolor.cprint("Tk库尚未就绪[Tkinter is not ready]", 'red')
            continue
        TkinterShow(Courses)
    elif cmd in ["stkg", "showgxintkinter"]:
        if guiFlag == False:
            termcolor.cprint("Tk库尚未就绪[Tkinter is not ready]", 'red')
            continue
        TkinterShow(GX_Courses)
    elif cmd in ["d", "do"]: # 可预吟唱
        if not any(select_code) and not any(select_g_code):
            ErrorPrint("请先运行s或sg以确认选课！")
            continue
        SingleRush(select_code, select_g_code)
    elif cmd in ["dm", "dowithmutithread"]:
        if not any(select_code) or not any(select_g_code):
            print("请先运行s或sg以确认选课！")
            continue
        lnk = "http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper?jx0404id=%d&xkzy=&trjf=" % select_code
        print("按p键终止")
        thread_list = []
        for i in range(8):
            #print("t", i)
            thread_list.append(MutithreadRush(lnk))
            thread_list[-1].start()
    elif cmd == "p":
        try:
            if any(thread_list):
                for i in thread_list:
                    print(len(thread_list), i)
                    i._stop()
        except Exception as e:
            ErrorPrint(e)
    elif cmd in ["c", "curlist"]:
        GetCurrentCoursesList()
        for ind, i in enumerate(current_time_table):
            for jnd, j in enumerate(i):

                print('周%d第%d-%d节' % (jnd+1, (ind+1)*2-1, (ind+1)*2), end='\t')
                if j == "&nbsp;":
                    termcolor.cprint('空闲', 'green')
                else:
                    print(j)
            print('\n')
    elif cmd in ["q", "quit"]:
        break
    else:
        print("无法理解的命令:", cmd)
