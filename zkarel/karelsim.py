from __future__ import print_function
from collections import namedtuple
from functools import partial

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import tkMessageBox as tkmb
except ImportError:
    import tkinter.messagebox as tkmb

try:
    import tkFileDialog as tkfd
except ImportError:
    import tkinter.filedialog as tkfd

import random
import json
import time
import socket
import os.path
import pkg_resources

CellInfo = namedtuple("CellInfo", "n e w s")
Position = namedtuple("Position", "x y")

VEL_NORTH = (0, -1)
VEL_SOUTH = (0, 1)
VEL_EAST = (1, 0)
VEL_WEST = (-1, 0)

VELOCITY_DIR = [VEL_NORTH, VEL_EAST, VEL_WEST, VEL_SOUTH]

DIR_NORTH = 0
DIR_EAST = 1
DIR_WEST = 2
DIR_SOUTH = 3

KAREL_DIR = "^><v"


def get_img_path(filename):
    return pkg_resources.resource_filename(__name__, os.path.join("images", filename))


def circle(canvas, x, y, r, **kwargs):
    id = canvas.create_oval(x-r,y-r,x+r,y+r,fill="grey", **kwargs)
    return id


class ScrollableCanvas(tk.Frame):
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.canvas = tk.Canvas(self)
        self.hbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self,orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(width=300, height=300)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


class TkView(object):
    CS = 40
    CC = CS / 2

    def __init__(self, level_list):
        self._level_list = level_list
        self._curr_level = 0
        self._level = None

        self._root = tk.Tk()
        self._root.title("Karel")
        self._frame = None
        self._canvas = None

        self._border_width = 10
        self._wall_width = 2
        self._karel_images = None
        self._beeper_image = None
        self._init_ui()

        self.karel = None
        self.active = False
        self._new_level(0)
        self._start_level()

    def _load_images(self):
        self._karel_images = [tk.PhotoImage(file=get_img_path("karel-n.gif")),
                              tk.PhotoImage(file=get_img_path("karel-e.gif")),
                              tk.PhotoImage(file=get_img_path("karel-w.gif")),
                              tk.PhotoImage(file=get_img_path("karel-s.gif"))]
        self._beeper_image = tk.PhotoImage(file=get_img_path("beeper.gif"))


    def _init_level_menu(self, level_menu):
        for i, level in enumerate(self._level_list):
            on_change_level = partial(self.change_level, i)
            menu_label = "Level {0}: {1}".format(i+1, level["title"])
            level_menu.add_command(label=menu_label, underline=6,
                                   command=on_change_level)

    def _init_game_menu(self, game_menu):
        level_menu = tk.Menu(self._frame, tearoff=0)
        self._init_level_menu(level_menu)

        game_menu.add_command(label="Restart", underline=0,
                              command=self._on_restart)
        game_menu.add_command(label="Screenshot ...", underline=0,
                              command=self._on_screenshot)
        game_menu.add_cascade(label="Change Level", underline=0,
                              menu=level_menu)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", underline=0,
                              command=self._on_quit)

    def _init_help_menu(self, help_menu):
        help_menu.add_command(label="About", underline=0,
                              command=self._on_about)

    def _init_ui(self):
        self._load_images()

        self._frame = ScrollableCanvas(self._root)
        self._canvas = self._frame.canvas
        self._canvas.config(width=640, height=480)
        self._canvas.config(bg="white")
        self._frame.grid(row=0, column=0)
        self._frame.pack(fill=tk.BOTH, expand=tk.YES)

        menubar = tk.Menu(self._frame)
        game_menu = tk.Menu(self._frame, tearoff=0)
        help_menu = tk.Menu(self._frame, tearoff=0)

        menubar.add_cascade(label="Game", underline=0, menu=game_menu)
        menubar.add_cascade(label="Help", underline=0, menu=help_menu)

        self._init_game_menu(game_menu)
        self._init_help_menu(help_menu)

        self._root.config(menu=menubar)

    def _new_level(self, level=None):
        if level is None:
            self._curr_level += 1
            self._curr_level %= len(self._level_list)
        else:
            self._curr_level = level
        self._level = Level(self._level_list[self._curr_level])

    def _get_canvas_dim(self):
        ncols = self._level.current.ncols
        nrows = self._level.current.nrows

        canvas_width = (ncols * self.CS
                        + self._border_width * 2
                        + self._wall_width)
        canvas_height = (nrows * self.CS
                         + self._border_width * 2
                         + self._wall_width)

        canvas_height *= 2

        return canvas_width, canvas_height

    def _start_level(self):
        self.karel = self._level.current.karel
        canvas_width, canvas_height = self._get_canvas_dim()
        self._canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        self._draw_background()
        self._draw_foreground()

    def _on_restart(self):
        self.start()

    def change_level(self, i):
        self.active = False
        self._new_level(i)
        self._start_level()

    def screenshot(self, psfilename):
        canvas_width, canvas_height = self._get_canvas_dim()
        zoom_level = 2
        self._canvas.postscript(file=psfilename,
                                pagewidth=(canvas_width * zoom_level),
                                width=canvas_width,
                                height=canvas_height)

    def _on_screenshot(self):
        psfilename = tkfd.asksaveasfilename(defaultextension=".ps")
        self.screenshot(psfilename)

    def _on_quit(self):
        exit(0)

    def _on_about(self):
        print("About")

    def _draw_background(self):
        CS = self.CS
        CC = self.CC
        self._canvas.delete("bg")
        offset = 0

        for bg in (self._level.current, self._level.goal):
            for row in range(bg.nrows):
                for col in range(bg.ncols):
                    topx = col * CS + self._border_width + self._wall_width
                    topy = offset + row * CS + self._border_width + self._wall_width
                    cx = topx + CC
                    cy = topy + CC

                    circle(self._canvas, cx, cy, 2, tag="bg")
                    if bg.is_wall_direction((col, row), DIR_NORTH):
                        self._canvas.create_line(topx, topy, topx + CS, topy, width=4,
                                                 fill="brown", tag="bg")

                    if bg.is_wall_direction((col, row), DIR_SOUTH):
                        self._canvas.create_line(topx, topy + CS, topx + CS, topy + CS, width=4,
                                                 fill="brown", tag="bg")

                    if bg.is_wall_direction((col, row), DIR_WEST):
                        self._canvas.create_line(topx, topy, topx, topy + CS, width=4,
                                                 fill="brown", tag="bg")

                    if bg.is_wall_direction((col, row), DIR_EAST):
                        self._canvas.create_line(topx + CS, topy, topx + CS, topy + CS, width=4,
                                                 fill="brown", tag="bg")

            offset += self._level.current.nrows * CS + self._border_width + self._wall_width

    def _draw_foreground(self):
        CS = self.CS
        CC = self.CC
        self._canvas.delete("karel")
        self._canvas.delete("beeper")
        offset = 0

        for fg in (self._level.current, self._level.goal):
            for row in range(self._level.current.nrows):
                for col in range(self._level.current.ncols):
                    topx = col * CS + self._border_width
                    topy = offset + row * CS + self._border_width
                    cx = topx + CC
                    cy = topy + CC

                    if fg.has_beeper((col, row)):
                        self._canvas.create_image(topx, topy,
                                                  image=self._beeper_image,
                                                  tag="beeper",
                                                  anchor=tk.NW)
                        count = fg.get_beepers((col, row))
                        self._canvas.create_text(cx, cy, tag="beeper",
                                                 text=str(count))

            karel = fg.karel
            karel_pos = karel.pos
            topx = karel_pos.x * CS + self._border_width
            topy = offset + karel_pos.y * CS + self._border_width

            direction = VELOCITY_DIR.index(karel.velocity)
            self._canvas.create_image(topx, topy, image=self._karel_images[direction],
                                      tag="karel", anchor=tk.NW)

            offset += self._level.current.nrows * CS + self._border_width + self._wall_width

    def update(self):
        self._draw_foreground()

    def run(self, callback, args):
        def wrapped_callback():
            callback(*args)
            self._root.after(20, wrapped_callback)
        self._root.after(20, wrapped_callback)
        tk.mainloop()

    def close(self):
        pass

    def start(self):
        self._level.rotate()
        self._start_level()
        self.active = True

    def stop(self):
        self.active = False
        status = self._level.check_goal_reached()
        if all(status):
            message = "Level Complete!"
            self._root.after(1000, tkmb.showinfo, "Result!", message)
        else:
            pf = ["FAIL", "PASS"]
            karel_pos, karel_velocity, karel_beepers, world_beepers = status
            result = ("Karel Position: {0}\n"
                      "Karel Direction: {1}\n"
                      "Karel Bag: {2}\n"
                      "Beeper Position: {3}\n").format(pf[karel_pos],
                                                       pf[karel_velocity],
                                                       pf[karel_beepers],
                                                       pf[world_beepers])
            self._root.after(1000, tkmb.showerror, "Result!", result)


class Level(object):
    def __init__(self, level_info):
        self._level_info = level_info
        self._nalts = len(self._level_info["alt"])
        self._select = 0
        self._setup_level()

    def _setup_level(self):
        self.current = GameState(self._level_info["alt"][self._select]["start"])
        self.goal = GameState(self._level_info["alt"][self._select]["end"])

    def rotate(self):
        self._select += 1
        self._select %= self._nalts
        self._setup_level()

    def check_goal_reached(self):
        karel_pos = True
        karel_velocity = True
        karel_beepers = True
        world_beepers = True

        if self.current.karel.pos != self.goal.karel.pos:
            karel_pos = False

        if self.current.karel.velocity != self.goal.karel.velocity:
            karel_velocity = False

        if self.current.karel.beepers != self.goal.karel.beepers:
            karel_beepers = False

        for row in range(self.current.nrows):
            for col in range(self.current.ncols):
                if (self.current.get_beepers(Position(row, col))
                    != self.goal.get_beepers(Position(row, col))):
                    world_beepers = False

        return (karel_pos, karel_velocity, karel_beepers, world_beepers)


class GameState(object):
    def __init__(self, state_info):
        self._state_info = state_info
        self.cols = None
        self.nrows = None
        self._cells = None
        self._beepers = None
        self.karel = None

        self.reset()

    def reset(self):
        bag = self._state_info["bag"]
        state_info = self._state_info["pos"].split("\n")

        self.ncols = int((max([len(line) for line in state_info]) - 1) / 2)
        self.nrows = int((len(state_info) - 1) / 2)

        self._cells = [[None for x in range(self.ncols)]
                       for y in range(self.nrows)]
        self._beepers = {}
        self.karel = None

        for y in range(self.nrows):
            for x in range(self.ncols):
                level_y = (y * 2) + 1
                level_x = (x * 2) + 1
                cell_type = state_info[level_y][level_x]

                try:
                    beepers = int(cell_type)
                except ValueError:
                    pass
                else:
                    self._beepers[Position(x, y)] = beepers

                if cell_type in KAREL_DIR:
                    kdir = KAREL_DIR.index(cell_type)
                    kpos = Position(x, y)
                    self.karel = Karel(kpos, VELOCITY_DIR[kdir], bag, self)

                nw = (state_info[level_y - 1][level_x] == "#")
                sw = (state_info[level_y + 1][level_x] == "#")
                ww = (state_info[level_y][level_x - 1] == "#")
                ew = (state_info[level_y][level_x + 1] == "#")

                self._cells[y][x] = CellInfo(nw, ew, ww, sw)

    def is_wall(self, pos, velocity):
        d = VELOCITY_DIR.index(velocity)
        return self.is_wall_direction(pos, d)

    def is_wall_direction(self, pos, d):
        pos = Position(*pos)
        return self._cells[pos.y][pos.x][d]

    def get_beepers(self, pos):
        return self._beepers.get(pos, 0)

    def has_beeper(self, pos):
        return bool(self.get_beepers(pos))

    def remove_beeper(self, pos):
        self._beepers[pos] -= 1

    def add_beeper(self, pos):
        if pos not in self._beepers:
            self._beepers[pos] = 0

        self._beepers[pos] += 1


class Error(Exception):
    pass


class Karel(object):
    def __init__(self, pos, velocity, beepers, level):
        self.pos = pos
        self.velocity = velocity
        self.beepers = beepers
        self._level = level

    def _next_pos(self, pos, velocity):
        return Position(pos[0] + velocity[0],
                        pos[1] + velocity[1])

    def move(self):
        if self._level.is_wall(self.pos, self.velocity):
            raise Error("Oops! Can't move, there is a wall!")

        self.pos = self._next_pos(self.pos, self.velocity)

    def _next_velocity(self, velocity):
        return (velocity[1], -velocity[0])

    def turn_left(self):
        self.velocity = self._next_velocity(self.velocity)

    def pick_beeper(self):
        if not self._level.has_beeper(self.pos):
            raise Error("Oops! No beeper at current position!")

        self.beepers += 1

        self._level.remove_beeper(self.pos)

    def put_beeper(self):
        if self.beepers == 0:
            raise Error("Oops! No beepers to put!")

        self.beepers -= 1

        self._level.add_beeper(self.pos)

    def front_is_clear(self):
        return not self._level.is_wall(self.pos, self.velocity)

    def left_is_clear(self):
        next_velocity = self._next_velocity(self.velocity)
        return not self._level.is_wall(self.pos, next_velocity)

    def right_is_clear(self):
        next_velocity = self.velocity
        for i in range(3):
            next_velocity = self._next_velocity(next_velocity)
        return not self._level.is_wall(self.pos, next_velocity)

    def next_to_a_beeper(self):
        return self._level.has_beeper(self.pos)

    def facing_north(self):
        return self.velocity == VEL_NORTH

    def facing_south(self):
        return self.velocity == VEL_SOUTH

    def facing_east(self):
        return self.velocity == VEL_EAST

    def facing_west(self):
        return self.velocity == VEL_WEST

    def any_beepers_in_beeper_bag(self):
        return bool(self._beepers)

    def no_beepers_in_beeper_bag(self):
        return not bool(self._beepers)

    def avenue(self):
        return self.pos[0]

    def street(self):
        return self.pos[1]

def run_command(view, cmd):
    val = None

    actions = ["move", "turn_left", "pick_beeper", "put_beeper"]
    delayed_actions = ["move", "turn_left"]
    sensors = ["front_is_clear", "left_is_clear", "right_is_clear",
               "next_to_a_beeper", "facing_north", "facing_south",
               "facing_east", "facing_west", "any_beepers_in_beeper_bag",
               "no_beepers_in_beeper_bag", "avenue", "street"]

    if cmd == "start":
        view.start()
        return "OK"
    elif cmd == "stop":
        view.stop()
        return "OK"

    if not view.active:
        return "ER: not started yet"

    try:
        if cmd in actions:
            action_method = getattr(view.karel, cmd)
            action_method()
            if cmd in delayed_actions:
                time.sleep(0.2)
            resp = "OK"
        elif cmd in sensors and view.active:
            sensor_method = getattr(view.karel, cmd)
            result = sensor_method()
            resp = "OK: {0:d}".format(result)
        else:
            resp = "ER: unknown command"
    except Error as err:
        resp = "ER: {0}".format(err.args[0])

    view.update()
    return resp


def process_command(sock, view):
    try:
        cmd, client = sock.recvfrom(4096)
        resp = run_command(view, cmd.decode("utf-8"))
        sock.sendto(resp.encode("utf-8"), client)
    except socket.timeout:
        pass

    return True


def listen_for_commands(view):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", 9999))
    sock.settimeout(0.01)

    view.run(process_command, (sock, view))


def main():
    levels_filename = pkg_resources.resource_filename(__name__, "levels.json")
    levels_fp = open(levels_filename)
    levels = json.load(levels_fp)
    view = TkView(levels)
    view.update()

    try:
        listen_for_commands(view)
    except KeyboardInterrupt:
        pass

    view.close()


if __name__ == "__main__":
    main()
