# coding:utf-8
# python2 & pip install docker-py

import argparse
import re
import os

from docker import Client
from docker.utils import kwargs_from_env


def display_cpu(args):
    detail = client.inspect_container(args.container)
    if bool(detail["State"]["Running"]):
        container_id = detail['Id']
        cpu_usage = {}
        with open('/sys/fs/cgroup/cpuacct/docker/' + container_id + '/cpuacct.stat', 'r') as f:
            for line in f:
                m = re.search(r"(system|user)\s+(\d+)", line)
                if m:
                    cpu_usage[m.group(1)] = int(m.group(2))
        if args.type == "all":
            cpu = cpu_usage["system"] + cpu_usage["user"]
        else:
            cpu = cpu_usage[args.type]
        user_ticks = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        print(float(cpu) / user_ticks)
    else:
        print(0)


def display_memory(args):
    detail = client.inspect_container(args.container)
    if bool(detail["State"]["Running"]):
        container_id = detail['Id']
        with open('/sys/fs/cgroup/memory/docker/' + container_id + '/memory.stat', 'r') as f:
            for line in f:
                m = re.search(r"total_rss\s+(\d+)", line)
                if m:
                    print(m.group(1))
                    return
    else:
        print(0)


def display_status(args):
    detail = client.inspect_container(args.container)
    state = detail["State"]
    if bool(state["Paused"]):
        print(0)   # Paused
    elif bool(state["Running"]):
        print(1)   # Running
    elif int(state["ExitCode"]) == 0:
        print(2)   # Stopped
    else:
        print(3)   # Crashed


# 命令行参数解析实例
parser = argparse.ArgumentParser()

# 向解析器添加容器名称
parser.add_argument("container", help="Container name")

# 子解析器(数据类型)
subparsers = parser.add_subparsers(title="Counters", description="Available counters", dest="dataType")

# 向子解析器中添加第二参数cpu
cpu_parser = subparsers.add_parser("cpu", help="Display CPU usage")
# 向第二参数中添加可选参数
cpu_parser.add_argument("type", choices=["system", "user", "all"])
# 参数解析器默认调用函数(display_cpu)
cpu_parser.set_defaults(func=display_cpu)

# 向子解析器中添加第二参数memory
memory_parser = subparsers.add_parser("memory", help="Display memory usage")
memory_parser.set_defaults(func=display_memory)

# 向子解析器中添加第二参数status
status_parser = subparsers.add_parser("status", help="Display the container status")
status_parser.set_defaults(func=display_status)

# 创建客户端实例
client = Client(**(kwargs_from_env()))

# 解析器解析参数
args = parser.parse_args()
# 参数调用函数
args.func(args)
