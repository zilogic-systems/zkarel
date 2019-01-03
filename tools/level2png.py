from __future__ import print_function
from zkarel import karelsim

import yaml
import subprocess

levels = yaml.load(open("zkarel/levels.yml"))
view = karelsim.TkView(levels)

for i, level in enumerate(levels):
    for state in ["start", "end"]:
        if state == "end":
            level["alt"][0]["start"] = level["alt"][0]["end"]
        view.change_level(i)
        base_filename = "levels/level-{}-{}".format(state, i)
        ps_filename = base_filename + ".ps"
        png_filename = base_filename + ".png"
        view.screenshot(ps_filename)
        subprocess.call(["convert", ps_filename, png_filename])

    


