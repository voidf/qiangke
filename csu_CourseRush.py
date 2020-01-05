import requests
import json
import os
import time
import re
import base64
import sys
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
    elif YNKey.lower() in ['n','not','non', 'no', 'nope', 'false', 'iie', 'iya']:
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
    print(e)
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


def refreshCourses():
    global Courses
    Courses = []
    global GX_Courses
    GX_Courses = []
    # ses.headers["Referer"]="http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk"
    getList_res = ses.post(getList_lnk, data=getList_dt)
    GXgetList_res = ses.post(GX_lnk, data=getList_dt)
    print("=====================")

    getList_json = json.loads(getList_res.text)
    GXgetList_json = json.loads(GXgetList_res.text)
    GX_Courses = saveCourse("GXcourses.bak", GXgetList_json)
    Courses = saveCourse("courses.bak", getList_json)

# ctsm 冲突说明


def saveCourse(save_path, save_json):
    TEMP_Courses = []
    try:
        with open(resource_path(save_path), "w") as fbak:
            pass
        for i in save_json["aaData"]:
            try:
                TEMP_Courses.append({
                    "Lesson_Name": i["ktmc"],
                    "Lesson_Type": i["kcmc"],
                    "Teachers": i["skls"],
                    "Study_Score": i["xf"],
                    "Time": i["sksj"],
                    "Place": i["skdd"],
                    "Remain": i["syrs"],
                    "Max": i["xxrs"],
                    # "Subsidy": i["xkbtf"],  # 补贴分
                    "Request_ID": i["jx0404id"]
                })
                # print(json.dumps(TEMP_Courses[-1])+"\n")
                with open(resource_path(save_path), "a") as fbak:
                    fbak.write(json.dumps(TEMP_Courses[-1])+"\n")
            except Exception as e:
                termcolor.cprint(e, 'red')
                termcolor.cprint("Error occurred at", 'red')
                termcolor.cprint(i, 'red')
        termcolor.cprint("Done!Results are in "+save_path, 'green')
    except Exception as e:
        print(e)
        termcolor.cprint("save Courses failed!", 'red')
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
                termcolor.cprint(e, 'red')
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

    global getList_lnk  # 必选课
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
                Courses.append(json.loads(i))
            with open(resource_path("GXcourses.bak"), "r") as fGX:
                for i in fGX.readlines():
                    GX_Courses.append(json.loads(i))
        else:
            raise NameError("W:Redo query")
except Exception as e:
    termcolor.cprint(e, 'red')
    # 获取选课查询链接
    fixCookie()

    refreshCourses()


def SingleRush(TEMP_sel,TEMP_gxsel=[]):
    global ses
    done_list=[0 for i in (TEMP_sel+TEMP_gxsel)]

    try:
        try:
            while 0 in done_list:
                try:
                    for ind,i in enumerate(TEMP_sel):
                        lnk='http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper?jx0404id=%d&xkzy=&trjf=' % i
                        do_result = ses.get(lnk, timeout=1)
                        do_json = json.loads(do_result.text)
                        print(do_json)
                        if do_json["success"] == True:
                            done_list.pop(ind)
                            TEMP_sel.pop(ind)
                            break
                        
                    for ind,i in enumerate(TEMP_gxsel):
                        lnk='http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper?jx0404id=%d&xkzy=&trjf=' % i
                        do_result = ses.get(lnk, timeout=1)
                        do_json = json.loads(do_result.text)
                        print(do_json)
                        if do_json["success"] == True:
                            done_list.pop(len(TEMP_sel)+ind)
                            TEMP_gxsel.pop(ind)
                            break # pop破坏了列表结构，因此终止

                except Exception as ex:
                    termcolor.cprint(ex,'red')
                    termcolor.cprint("于while内部错误",'red')
                    if do_result.status_code!=200:
                        raise NameError("Non 200 Response")
            print("抢课成功，命令回显:", do_json)
        except Exception as e:
            termcolor.cprint(e,'red')
            termcolor.cprint("错误断点2,自动运行rec",'red')
            fixCookie()
            refreshCourses()
            SingleRush(lnk)
    except KeyboardInterrupt:
        termcolor.cprint("通过键盘打断,抢课终止", 'yellow')


current_time_table = []
free_time = []


def GetCurrentCoursesList():
    courses_list_html = ses.get(
        "http://csujwc.its.csu.edu.cn/jsxsd/xsxkjg/xsxkkb")
    info_table = re.findall(
        '''<tbody>(.*?)</tbody>.*?''', courses_list_html.text, re.S)[0]
    global current_time_table
    global free_time
    free_time = []
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


GetCurrentCoursesList()
print(free_time)

selectCode = []
termcolor.cprint("表格数据建立完成", 'green')
print("伪交互模块启动，输入help或者h查看帮助")
while 1:
    cmd = input(">>>").lower()
    if cmd in ["h", "help"]:
        print("简写\t命令\t说明")
        print("h\thelp\t打印此帮助信息")
        print("e\teval\t进入eval命令执行模式，调试用")
        print("f\tfilter\t过滤设置")
        print("s\tselect\t输入欲选课的下标序号（在新的一行里）")
        print("rec\trefreshcourses\t重新获取可选课列表")
        print("rea\trefreshauth\t重新登录")
        print("res\trefreshsession\t重新获取会话，用后自动重新登录（慎用）")
        print("sh\tshow\t命令行展示可选必选课列表，请确保命令框够大")
        print("shg\tshowgx\t命令行展示可选公选课列表，请确保命令框够大")
        print("stk\tshowintkinter\t用tk库展示可选必选课列表")
        print("stkg\tshowgxintkinter\t用tk库展示可选公选课列表")
        print("d\tdo\t开始抢课，使用前请先用s设置目的课")
        print("dm\tdowithmutithread\t实验性多线程抢课")
        print("c\tcurlist\t打印当前课表")
        print("q\tquit\t退出")
    elif cmd in ["e", "eval"]:
        termcolor.cprint("eval模式已启动，输入q回到上级",'yellow')
        try:
            while 1:
                evalcmd = input(">>>")
                if evalcmd == "q":
                    break
                else:
                    termcolor.cprint(eval(evalcmd),'cyan')
        except KeyboardInterrupt:
            termcolor.cprint("键盘打断，回到上级",'yellow')
    elif cmd in ["s", "select"]:
        try:
            TEMP_inp = input("下标序号（从零开始的，并不是行号，以空格隔开）:").split(' ')
            for TEMP_per_inp in TEMP_inp:
                selectCode = int(Courses[int(TEMP_per_inp)]["Request_ID"])
            termcolor.cprint(selectCode,'yellow')
        except Exception as e:
            termcolor.cprint(e, 'red')
            termcolor.cprint("更新选课代码失败", 'red')
    elif cmd in ["rec", "refreshcourses"]:
        fixCookie()
        refreshCourses()
    elif cmd in ["rea", "refreshauth"]:
        reAuth()
    elif cmd in ["res", "refreshsession"]:
        refreshSession()
        reAuth()
    elif cmd in ["sh", "show"]:
        print("下标\t课名\t类型\t教师\t学分\t时间\t地点\t剩余人数\t人数上限\t请求ID")
        for i in range(len(Courses)):
            print(i, Courses[i]["Lesson_Name"], Courses[i]["Lesson_Type"], Courses[i]["Teachers"], Courses[i]["Study_Score"], Courses[i]
                  ["Time"], Courses[i]["Place"], Courses[i]["Remain"], Courses[i]["Max"], Courses[i]["Request_ID"], sep="\t")
    elif cmd in ["stk", "showintkinter"]:
        if guiFlag == False:
            termcolor.cprint("Tk库尚未就绪[Tkinter is not ready]", 'red')
            continue
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
        for i in range(len(Courses)):
            tree_view.insert("", i, values=(i, Courses[i]["Lesson_Name"], Courses[i]["Lesson_Type"], Courses[i]["Teachers"], Courses[i]["Study_Score"],
                                            Courses[i]["Time"], Courses[i]["Place"], Courses[i]["Remain"], Courses[i]["Max"], Courses[i]["Request_ID"]))
        rt.mainloop()
    elif cmd in ["d", "do"]:
        if not any(selectCode):
            print("请先运行s以确认选课！")
            continue
        SingleRush(selectCode)
    elif cmd in ["dowithmutithread", "dm"]:
        if not any(selectCode):
            print("请先运行s以确认选课！")
            continue
        lnk = "http://jwctest.its.csu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper?jx0404id=%d&xkzy=&trjf=" % selectCode
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
            print(e)
    elif cmd in ["q", "quit"]:
        break
    else:
        print("无法理解的命令:", cmd)
