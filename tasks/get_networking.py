__author__ = 'cristian'

from graviton import *


@task
def get_networking(server_name, server, ssh_client):
    get_hostmame(server, ssh_client)
    get_ip(server, ssh_client)

    if server["provider"].lower() in LOCALHOST:
        server["hostname"] = server_name


def get_hostmame(server, ssh_client):

    """
        get hostname of hosts
        @type param server_name: str
        @type param server: dict
        :return:
    """
    server["hostname"] = exec_command(ssh_client, "hostname")


def get_ip(server, ssh_client):
    """
        get private ip of servers
        @type param server_name: str
        @type param server: dict
        :return:
    """

    interface = "eth1"

    if server["provider"].lower() in LOCALHOST:
        interface = "eth0"

    server["private_ip"] = exec_command(ssh_client,
                                        "ifconfig " + interface + "|grep inet|head -1|sed 's/\:/ /'|awk '{print $3}'")


if __name__ == "__main__":
    run_tasks()



