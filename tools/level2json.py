from __future__ import print_function

import yaml
import json

with open("zkarel/levels.yml") as yml_fp:
    with open("zkarel/levels.json", "w") as json_fp:
        levels = yaml.load(yml_fp)
        json_fp.write(json.dumps(levels))
