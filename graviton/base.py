__author__ = 'cristian'

import sys
import paramiko
from yaml import load, dump
from gevent import monkey, Greenlet
from paramiko_gevent import SSHClient
monkey.patch_all()

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


from gevent.pool import Pool

LOCALHOST = ("home", "localhost", "127.0.0.1")


class BColors:
    HEADER = '\033[96m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

execute = []


def task(func):
    # declare a new task
    args = func.func_code.co_varnames
    if 'ssh_client' in args:
        if args[-1] != 'ssh_client':
            raise Exception("ssh_client should be the last argument of the task")
        else:
            def new_func(server_name, server):
                ssh_client = SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(server["ip"], username=server["user"],  port=server["port"])
                ssh_client.server = server
                func(server_name, server, ssh_client)
            execute.append(new_func)

    else:
        execute.append(func)


def exec_command(pmk, cmd, ignore_errors=False):
    """
        Execute command in paramiko and handle error
        @type param pmk: SSHClient
        :return:
    """

    print BColors.WARNING + pmk.server["ip"] + "@: " + cmd + BColors.ENDC
    stdin, stdout, stderr = pmk.exec_command(cmd)
    error = stderr.read()

    if error:
        print BColors.FAIL + pmk.server["ip"] + "@:" + error + BColors.ENDC
        if not ignore_errors:
            exit(1)
    return stdout.read().strip()


def run_tasks():
    """
        Run task asynchronously
    :return:
    """
    server_file = open(sys.argv[1])
    servers = load(server_file, Loader=Loader)
    server_file.close()
    pool = Pool()

    def spawn(func, *args, **kwargs):
        g = Greenlet(func, *args, **kwargs)
        pool.add(g)
        g.start()

    for function in execute:
        for server_name, server in servers.items():
            print u'\u2713 ' + BColors.HEADER + function.__name__ + ": " + server_name + BColors.ENDC
            spawn(function, server_name, server)

    pool.join()
    server_file = open(sys.argv[1], "w+")
    dump(servers, server_file, Dumper=Dumper)
    server_file.close()

    print BColors.OKGREEN + "Done!!!" + BColors.ENDC


def run_sync_task(save=True):
    """
         Run task synchronously
    """
    server_file = open(sys.argv[1])
    servers = load(server_file, Loader=Loader)
    server_file.close()
    pool = Pool()

    def spawn(func, *args, **kwargs):
        g = Greenlet(func, *args, **kwargs)
        pool.add(g)
        g.start()

    for function in execute:
        for server_name, server in servers.items():
            print u'\u2713 ' + BColors.HEADER + function.__name__ + ": " + server_name + BColors.ENDC
            spawn(function, server_name, server)
            pool.join()

    pool.join()

    if save:
        server_file = open(sys.argv[1], "w+")
        dump(servers, server_file, Dumper=Dumper)
        server_file.close()

    print BColors.OKGREEN + "Done!!!" + BColors.ENDC