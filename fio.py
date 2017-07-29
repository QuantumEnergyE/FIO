# -*- coding: utf-8 -*-
import os
import sys
import logging
import subprocess
import json
import re
import itertools
import xlwt
from collections import OrderedDict


__author__ = 'quantum'
__date__ = '2017/7/13'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=os.path.join(os.path.dirname(sys.argv[0]), "fio_test.log"),
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.root.addHandler(console)

re_info = re.compile(r'.*(read|write).*io=(.*)bw=(.*)iops=(.*)runt=(.*).*msec')


class Mail(object):
    pass


class Excel(object):
    def __init__(self):
        self.style_title = xlwt.easyxf('pattern :pattern solid, fore_colour green;font: bold on,height 300;')
        self.style_content = xlwt.easyxf('font: height 250;')
        self.pos = 1

    def open(self):
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet('Sheet1')
        self.ws.col(0).width = 256*15
        self.ws.col(1).width = 256*15
        self.ws.col(2).width = 256*15
        self.ws.col(3).width = 256*15
        self.ws.col(4).width = 256*17
        self.ws.col(5).width = 256*17
        self.ws.col(6).width = 256*17
        self.ws.col(7).width = 256*15
        self.ws.col(8).width = 256*150
        self.ws.write(0, 0, "filename", self.style_title)
        self.ws.write(0, 1, "bs", self.style_title)
        self.ws.write(0, 2, "io pattern", self.style_title)
        self.ws.write(0, 3, "read/write", self.style_title)
        self.ws.write(0, 4, "io", self.style_title)
        self.ws.write(0, 5, "bw", self.style_title)
        self.ws.write(0, 6, "iops", self.style_title)
        self.ws.write(0, 7, "runt", self.style_title)
        self.ws.write(0, 8, "command", self.style_title)

    def close(self):
        self.wb.save("result.xls")

    def __add__(self, other):
        command = other.pop()
        cmd_dict = other.pop()
        for i in other:
            self.ws.write(self.pos, 0, cmd_dict['-filename'], self.style_content)
            self.ws.write(self.pos, 1, cmd_dict['-bs'], self.style_content)
            self.ws.write(self.pos, 2, cmd_dict['-rw'], self.style_content)
            self.ws.write(self.pos, 3, i[0].strip(',').decode("utf-8"), self.style_content)
            self.ws.write(self.pos, 4, i[1].strip(',').decode("utf-8"), self.style_content)
            self.ws.write(self.pos, 5, i[2].strip(',').decode("utf-8"), self.style_content)
            self.ws.write(self.pos, 6, i[3].strip(',').decode("utf-8"), self.style_content)
            self.ws.write(self.pos, 7, i[4].strip(',').decode("utf-8"), self.style_content)
            self.ws.write(self.pos, 8, command, self.style_content)
            self.pos += 1

g_excel = Excel()


def handle_data(command, info):
    cmd_dict = dict(map(lambda x: x.split('=') if len(x.split('=')) > 1 else (0, 0), command.split(' ')))
    info_list = re_info.findall(info)
    info_list.append(cmd_dict)
    info_list.append(command)
    g_excel + info_list


def run_shell(command):
    logging.info(command)
    # cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # for info in cmd.communicate():
    #     logging.info(info)
    #     handle_data(command, info)


class FIO(object):
    def __init__(self):
        self.args = None
        self.commands = None

    def __del__(self):
        pass

    def __sub__(self, other):
        pass

    def read_conf(self, conf_file):
        with open(os.path.join(os.path.dirname(sys.argv[0]), conf_file)) as cfg:
            config = json.load(cfg, object_pairs_hook=OrderedDict)
        cfg_keys = config.keys()
        min_keys = {"filename", "bs", "rw", "size"}
        if not min_keys.issubset(cfg_keys):
            raise Exception("key error!")
        self.args = config

    def create_commands(self):
        self.commands = ['fio -thread -group_reporting '+' '.join(i) for i in itertools.product(*map(lambda x: ["-%s=%s"%(x[0], y) for y in x[1]], self.args.items()))]
        # TODO: del rwmixread on read or wirte only

    def run_task(self):
        for cmd in self.commands:
            run_shell(cmd)

class ADBENCH(object):
    def __init__(self):
        pass

    def run_task(self):
        pass


def run():
    fio = FIO()
    logging.info("init")
    fio.read_conf("conf.json")
    fio.create_commands()
    fio.run_task()


if __name__ == "__main__":
    try:
        g_excel.open()
        run()
    except Exception as ex:
        logging.error(ex)
        logging.exception(ex)
        sys.exit(1)
    finally:
        g_excel.close()
