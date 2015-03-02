.PHONY : get-networking

CURRENT_DIRECTORY := $(shell pwd)
TASKS_DIR:=$(CURRENT_DIRECTORY)/tasks
SERVERS_FILE:=$(TASKS_DIR)/servers.yml

get-networking:
	exec $(CURRENT_DIRECTORY)/bin/python $(TASKS_DIR)/get_networking.py $(SERVERS_FILE)