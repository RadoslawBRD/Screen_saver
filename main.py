from __future__ import print_function

from pathlib import Path

import PIL.ImageTk

from tkinter import *
from tkinter import filedialog
from datetime import datetime, timedelta

from desktopmagic.screengrab_win32 import *
from PIL import Image, ImageDraw
from os import path, walk
from threading import Thread

import time

windows = []
global self_test
global sel_window
global folder_path
global selected_window
self_test = True
# noinspection PyRedeclaration
sel_window = []
root2 = Tk()
root2.title("Screen Backuper")
root2.attributes("-topmost", 1)
root2.geometry("250x250")


# root2.resizable(width=False, height=False)


def set_info(text):
    info.config(text=text)


def winEnumHandler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        windows.append(win32gui.GetWindowText(hwnd))


def get_windows():
    but1.destroy()
    try:
        win32gui.EnumWindows(winEnumHandler, None)
    finally:
        global v
        v = StringVar(top_frame)
        v.set("Wybierz okno")
        global drop
        drop = OptionMenu(top_frame, v, *windows)
        drop.pack(anchor=W)
        but3.pack(anchor=W, fill=X)
        v.trace("w", getselection)


# noinspection PySimplifyBooleanCheck
def getselection(*args):
    global selected_window
    v.get()
    selected_window = v.get()
    global sel_window
    sel_window = win32gui.GetWindowRect(win32gui.FindWindow(None, v.get()))
    #  print("got info")
    if sel_window != []:
        # tempbut.pack()  #############################################
        but3.config(state=NORMAL)
        but4.pack_forget()
        but6.pack_forget()
        #    print(sel_window)
        chk_f.deselect()


# noinspection PySimplifyBooleanCheck
def lock_window():
    global drop
    if sel_window == []:
        Label(top_frame, "Brak obiektu").pack()
    else:
        chk_o.select()
        # but1.config(state=DISABLED)
        drop.config(state=DISABLED)
        but3.destroy()
        but4.pack(anchor=W)


def folder_lock():
    global folder_path

    folder_path = filedialog.askdirectory()
    #  print(folder_path)

    folder_path = folder_path.replace("/", "\\")
    but4.config(text=folder_path)

    chk_f.select()
    but5.pack()

    but4.config(state=DISABLED)
    but6.pack()


def make_ss():  # chyba nie jest o potrzebne
    #  print("called make_ss")
    global folder_path, selected_window
    rect = win32gui.GetWindowRect(win32gui.FindWindow(None, selected_window))
    czas = datetime.now()
    # saveRectToBmp('test.bmp',rect=rect) #działa
    test2 = getRectAsImage(rect)
    test2.save(folder_path + '\\temp\\' + 'temp.png', format='png')  # robi zrzut

    but6.pack()
    png_loop()


def png_loop():  ##next_try
    start_time = time.time()  ##licznik czasu wykonania
    global folder_path, selected_window
    # rect = win32gui.GetWindowRect(win32gui.FindWindow(None, selected_window))
    im = getRectAsImage(win32gui.GetWindowRect(win32gui.FindWindow(None, selected_window)))

    # crop = 110, 120, int(im.size[0]) - 5, int(im.size[1] - 5)
    im = im.crop(box=(110, 120, int(im.size[0]) - 5, int(im.size[1] - 5)))

    czas = datetime.now()
    ImageDraw.Draw(im).text((95, 80), (czas.strftime("%d-%m-%Y %H:%M:%S")))

    save_path = (folder_path + '\\Zrzuty\\' + czas.strftime("%d-%m-%Y"))

    Path(save_path).mkdir(parents=True, exist_ok=True)

    im.save(save_path + '\\' + czas.strftime("%H-%M-%S.png"), format='png', optimize=TRUE)
    png_time.config(text=str(time.time() - start_time)[:5])
    # print("done in " + str(time.time() - start_time))  ##licznik czasu wykonania


def get_files():
    file_paths = []
    filenames = []
    for root, directories, files in walk(folder_path + '\\temp'):
        for filename in files:
            filepath = path.join(root, filename)
            file_paths.append(filepath)
            filenames.append(filename)
    return filenames, file_paths


def start_prog():
    chk_r.select()
    Thread(target=txt_loop).start()
    Thread(target=loop).start()

    but6.config(state=DISABLED)


def txt_loop():
    global folder_path, selected_window, self_test

    while self_test:  #############

        if int(datetime.now().strftime("%f")) not in range(0, 100000):
            # print("waiting")
            None
        else:
            try:
                start_time = time.time()  ##licznik czasu wykonania

                # print("In txt loop")

                # saveRectToBmp('test.bmp',rect=rect) #działa
                im = getRectAsImage(win32gui.GetWindowRect(win32gui.FindWindow(None, selected_window)))

                # crop = 100, 120, int(im.size[0]), int(im.size[1])
                im = im.crop(box=(100, 120, int(im.size[0]), int(im.size[1])))

                ### [czas]|[x,y],[x,y] i tak dalej w linii
                pix = im.load()
                temp = []
                xx = 0

                czas = datetime.now()
                Path(folder_path + '\\Wykres\\' + czas.strftime("%d-%m-%Y")).mkdir(parents=True, exist_ok=True)
                file = open(folder_path + '\\Wykres\\' + czas.strftime("%d-%m-%Y\\%H") + '.txt', "a+")

                for x in range(200, im.size[0] - 250):
                    for y in range(40, im.size[1] - 100):
                        if (x < 320 and y < 455) or (x > 1000 and y < 455):
                            None
                        else:
                            if pix[x, y][0] < 40 and pix[x, y][1] > 220 and pix[x, y][2] < 40:
                                if xx > 5:
                                    temp.append((x, y))
                                    xx = 0
                                else:
                                    xx += 1
                # print("Saving file")

                file.write(datetime.now().strftime("[%H:%M:%S]|") + str(temp) + '\n')
                file.close()
                # print("done in " + str(time.time() - start_time))  ##licznik czasu wykonania
                graph_time.config(text=str(time.time() - start_time)[:6])
                time.sleep(0.1)
            except:
                chk_r.config(background='red')
                chk_r.deselect()
                self_test = False
                set_info("Uruchom ponownie (E01)")  ### stracił okno


def txt_reader(self):
    global folder_path, selected_window
    global d, m, y, minut, hr, sec, data_txt
    global check_selection
    check_selection = "Wykres"

    data_txt = datetime.now()
    sec = data_txt.strftime("%S")

    def set_date():
        global d, m, y, minut, hr, sec, data_txt, check_selection

        if check_selection == "Zrzut":
            if int(data_txt.strftime("%S")) % 10 == 0:
                sec = data_txt.strftime("%S")
        else:
            sec = data_txt.strftime("%S")
        if data_txt > datetime.now():
            if check_selection == "Zrzut":
                data_txt = datetime.now().replace(second=int(int(datetime.now().strftime("%S")) / 10) * 10)
            else:
                data_txt = datetime.now()

        d = data_txt.strftime("%d")
        m = data_txt.strftime("%m")
        y = data_txt.strftime("%Y")
        minut = data_txt.strftime("%M")
        hr = data_txt.strftime("%H")
        sec = data_txt.strftime("%S")

    set_date()

    def click(event, nazwa):
        # print(event.num)
        global data_txt
        change = 1
        if check_selection == "Wykres":
            change = 1
        if check_selection == "Zrzut":
            change = 10

        if event.num == 3:
            if nazwa == "Day":
                data_txt = data_txt + timedelta(days=-1)
            if nazwa == "Month":
                data_txt = data_txt + timedelta(weeks=-4)
            if nazwa == "Year":
                data_txt = data_txt + timedelta(weeks=-56)
            if nazwa == "Minute10":
                data_txt = data_txt + timedelta(minutes=-10)
            if nazwa == "Minute0":
                data_txt = data_txt + timedelta(minutes=-1)
            if nazwa == "Hour":
                data_txt = data_txt + timedelta(hours=-1)
            if nazwa == "Second":
                data_txt = data_txt + timedelta(seconds=-change)

        if event.num == 1:
            if nazwa == "Day":
                data_txt = data_txt + timedelta(days=+1)
            if nazwa == "Month":
                data_txt = data_txt + timedelta(weeks=+4)
            if nazwa == "Year":
                data_txt = data_txt + timedelta(weeks=+56)
            if nazwa == "Minute10":
                data_txt = data_txt + timedelta(minutes=+10)
            if nazwa == "Minute0":
                data_txt = data_txt + timedelta(minutes=+1)
            if nazwa == "Hour":
                data_txt = data_txt + timedelta(hours=+1)
            if nazwa == "Second":
                data_txt = data_txt + timedelta(seconds=+change)
        set_date()
        butt_update()

    rootg = Toplevel()
    rootg.title("Wykres")

    top_frameg = Frame(rootg)
    top_frameg.pack(side=TOP, fill=X)

    bottom_frameg = Frame(rootg)
    bottom_frameg.pack(side=BOTTOM, fill=X)

    image_show = Label(rootg)
    image_show.pack()

    # <editor-fold desc="Date buttons pack">
    bd = Button(top_frameg, text=d)
    bd.bind("<Button-1>", lambda e: click(e, "Day"))
    bd.bind("<Button-3>", lambda e: click(e, "Day"))
    bd.pack(side=LEFT)

    Label(top_frameg, text="-").pack(side=LEFT)

    bm = Button(top_frameg, text=m)
    bm.bind("<Button-1>", lambda e: click(e, "Month"))
    bm.bind("<Button-3>", lambda e: click(e, "Month"))
    bm.pack(side=LEFT)

    Label(top_frameg, text="-").pack(side=LEFT)

    by = Button(top_frameg, text=y)
    by.bind("<Button-1>", lambda e: click(e, "Year"))
    by.bind("<Button-3>", lambda e: click(e, "Year"))
    by.pack(side=LEFT)

    Label(top_frameg, text=" | ").pack(side=LEFT)

    bhr = Button(top_frameg, text=hr)
    bhr.bind("<Button-1>", lambda e: click(e, "Hour"))
    bhr.bind("<Button-3>", lambda e: click(e, "Hour"))
    bhr.pack(side=LEFT)

    Label(top_frameg, text=":").pack(side=LEFT)

    bmin = Button(top_frameg, text=int(int(minut) / 10))
    bmin.bind("<Button-1>", lambda e: click(e, "Minute10"))
    bmin.bind("<Button-3>", lambda e: click(e, "Minute10"))
    bmin.pack(side=LEFT)

    bmin2 = Button(top_frameg, text=int(minut) % 10)
    bmin2.bind("<Button-1>", lambda e: click(e, "Minute0"))
    bmin2.bind("<Button-3>", lambda e: click(e, "Minute0"))
    bmin2.pack(side=LEFT)

    Label(top_frameg, text=":").pack(side=LEFT)

    bsec = Button(top_frameg, text=sec)
    bsec.bind("<Button-1>", lambda e: click(e, "Second"))
    bsec.bind("<Button-3>", lambda e: click(e, "Second"))
    bsec.pack(side=LEFT)

    img_scale = Scale(top_frameg, from_=1, to=100, orient=HORIZONTAL)
    img_scale.pack(side=LEFT)

    # </editor-fold>

    def check_box(*args):
        global check_selection, data_txt, sec
        check_selection = str(varcheck.get())
        butt_update()

    checkselection = ["Zrzut", "Wykres"]
    varcheck = StringVar(top_frameg)
    varcheck.set("Wykres")
    dropcheck = OptionMenu(top_frameg, varcheck, *checkselection)
    dropcheck.pack(side=RIGHT)
    varcheck.trace("w", check_box)

    def resize_value():
        # print(img_scale.get())
        return img_scale.get()

    def show_graph():
        global folder_path, selected_window
        global d, m, y, minut, hr, sec, data_txt
        global check_selection
        path = ""
        if check_selection == "Zrzut":
            temp = int(int(sec) / 10)
            sec = str(int(temp * 10))
            bsec.config(text=sec)
            if sec == "0":
                sec = "00"
            try:
                path = folder_path + '\\Zrzuty\\' + \
                       d + "-" + m + "-" + y + '\\' \
                       + hr + "-" + minut + "-" + sec + '.png'

            except Exception as e:

                # print(str(e) + "brak obrazu" + folder_path + '\\Zrzuty\\' +
                #       d + "-" + m + "-" + y + '\\'
                #       + hr + "-" + minut + "-" + sec + '.png')
                set_info("Nie znalazłem obrazu")
            try:
                # print(path)
                photo2 = Image.open(path)
                tempval = resize_value()
                temps1 = photo2.size[0] * tempval / 100
                temps2 = photo2.size[1] * tempval / 100
                photo2 = photo2.resize((int(temps1),
                                        int(temps2)), Image.ANTIALIAS)

                photo = PIL.ImageTk.PhotoImage(photo2)

                image_show.config(image=photo)

                image_show.image = photo
                set_info("Wyświetlam: " + hr + ":" + minut + ":" + sec + ".png")

                image_show.update()

            except Exception as e:
                # print(str(e) + "|" + path)
                set_info("Nie moge wyswietlic")

        elif check_selection == "Wykres":
            try:
                if len(m) == 1:
                    m = "0" + m
                with open(folder_path + "\\Wykres\\" + str(d) + "-" + str(m) + "-" + str(y) + "\\" + str(hr) + ".txt") as f:
                    datafile = f.readlines()
                for line in datafile:

                    if line.startswith("[" + hr + ":" + minut + ":" + sec + "]"):
                        read_line = line[line.index("|") + 3:-3]
                        read_line = read_line.split("), (")
                        # print(read_line)

                        try_graph1 = Image.new('RGB', (1200, 900))  # TODO tło jako tło analizatora
                        pix2 = try_graph1.load()
                        ##rysowanie grafu
                        for x in read_line:
                            pix2[int(x[0:x.index(",")]), int(x[x.index(",") + 1:])] = (255, 255, 0)

                        try:
                            crop = 200, 200, int(try_graph1.size[0]), int(try_graph1.size[1])
                            try_graph1 = try_graph1.crop(box=crop)

                            tempval = resize_value()
                            temps1 = try_graph1.size[0] * tempval / 100
                            temps2 = try_graph1.size[1] * tempval / 100
                            try_graph1 = try_graph1.resize((int(temps1),
                                                            int(temps2)), Image.ANTIALIAS)

                            photo = PIL.ImageTk.PhotoImage(try_graph1)

                            image_show.config(image=photo)

                            image_show.image = photo
                            set_info("Wyświetlam: " + hr + ".txt")
                            image_show.update()

                        except Exception as e:
                            #    print(str(e) + "|" + path)
                            set_info("Nie moge wyswietlic wykrsu")
            except Exception as e:
                # print(str(e) + "|" + folder_path + "\\Wykres\\" + d + "-" + m + "-" + y + "\\" + hr + ".txt")
                # set_info(folder_path+ d +  m +  y + "\\" + hr + ".txt")
                # set_info("Brak pliku txt")
                set_info(str(e))

    def butt_update():
        bd.config(text=d)
        bm.config(text=m)
        by.config(text=y)
        bhr.config(text=hr)
        bmin.config(text=int(int(minut) / 10))
        bmin2.config(text=int(minut) % 10)
        bsec.config(text=sec)
        show_graph()


def loop():
    global self_test
    while self_test:
        czas = datetime.now()

        if (int(czas.strftime("%S")) % 10) == 0:
            set_info("SS at: " + czas.strftime("%H:%M:%S"))
            Thread(target=png_loop).start()  # make_ss
            time.sleep(9.55)


def start():
    txt_reader(self=txt_reader)


tempbut = Button(root2, text="Wykresy", command=start)

top_frame = Frame(root2)
top_frame.pack(side=TOP, fill=X)
bottom_frame = Frame(root2)
bottom_frame.pack(side=BOTTOM, fill=X)

control_frame = Frame(bottom_frame)
control_frame.pack(anchor=W, fill=Y)

option_frame = Frame(bottom_frame)
option_frame.pack(fill=X)

graph_time = Label(option_frame, text="0.00")
graph_time.pack(side=RIGHT)

png_time = Label(option_frame, text="0.00")
png_time.pack(side=RIGHT)

info = Label(option_frame, text="Rozpocznij wyszukiwanie")
info.pack(side=LEFT)

chk_o = Checkbutton(control_frame, text="Okno", state=DISABLED)
chk_o.pack(side=LEFT)

chk_f = Checkbutton(control_frame, text="Folder", state=DISABLED)
chk_f.pack(side=LEFT)

chk_r = Checkbutton(control_frame, text="Uruchomiony", state=DISABLED)
chk_r.pack(side=LEFT)

but1 = Button(top_frame, text="Get windows", command=get_windows)
but1.pack(side=TOP, anchor=W)

but3 = Button(top_frame, text="Potwierdz", command=lock_window, state=DISABLED)

but4 = Button(top_frame, text="Wybierz folder", command=folder_lock)

but5 = Button(top_frame, text="Wykresy", command=start)  # next_try # command=make_ss

but6 = Button(top_frame, text="Start", command=start_prog)

but7 = Button(top_frame, text="ss", command=make_ss)


def kill_app():
    global self_test
    self_test = False
    sys.exit("Closed by TkInter \"X\"")


root2.protocol("WM_DELETE_WINDOW", kill_app)

if __name__ == '__main__':
    root2.mainloop()
