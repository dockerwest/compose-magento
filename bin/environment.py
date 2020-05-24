"""
Read .env file, basically taken from docker-compose for simplicity and modified
for our usecase
"""

import os
import contextlib
import codecs
import re
import shutil
import sys
import subprocess
import time


def split_env(env):
    if '=' in env:
        return env.split('=', 1)
    else:
        return env, None


def env_vars_from_file(filename):
    """
    Read in a line delimited file of environment variables.
    """
    if not os.path.exists(filename):
        raise Exception("Env file does not exist: %s" % filename)
    elif not os.path.isfile(filename):
        raise Exception("%s is not a file." % (filename))
    env = {}
    with contextlib.closing(codecs.open(filename, 'r', 'utf-8')) as fileobj:
        for line in fileobj:
            line = line.strip()
            if line and not line.startswith('#'):
                k, v = split_env(line)
                env[k] = v
    return env

class Environment:

    required_keys = [
        'BASEHOST', 'APPLICATION', 'WINDOW_MANAGER', 'APPLICATION_FILE_SYNC'
    ]

    def __init__(self, envfile):
        self.environment = env_vars_from_file(envfile)
        self.__check_environment()

    def __check_environment(self):
        for requiredkey in self.required_keys:
            if requiredkey not in self.environment:
                raise ValueError("Env does not contain %s" % requiredkey)

    def is_tool_available(self, toolname):
        from shutil import which
        return which(toolname) is not None

    def get_compose_filename(self):
        if self.is_tool_available('mutagen'):
            return 'docker-compose-mutagen.yml'
        if self.is_tool_available('dinghy'):
            return 'docker-compose-dinghy.yml'
        return 'docker-compose.yml'

    def get_project_name(self):
        regex = re.compile('\\W+')
        basehost = self.get('BASEHOST')
        projectname = regex.sub('', basehost)
        return projectname

    def get_container_id(self, container):
        # TODO: might do with some additional checks, will break quite fast
        container_id_cmd = [
            os.path.dirname(sys.argv[0]) + '/run',
            'ps', '-q', container
        ]

        container_id = subprocess.check_output(container_id_cmd, universal_newlines=True)
        containerId = container_id.strip()

        return containerId

    def get_container_name(self, container):
        container_id = self.get_container_id(container)

        container_name_cmd = [
            'docker',
            'inspect', '-f', '{{.Name}}', container_id
        ]

        container_name = subprocess.check_output(container_name_cmd, universal_newlines=True)
        container_name = container_name.strip().strip('/')

        return container_name
    
    def is_container_running(self, container):
        container_id = self.get_container_id(container)

        if not container_id:
            return False

        container_status_cmd = [
            'docker',
            'inspect', '-f', '{{.State.Running}}', container_id
        ]

        container_status = subprocess.check_output(container_status_cmd, universal_newlines=True)
        container_status = container_status.strip()

        return container_status == 'true'
    
    def is_container_down(self, container):
        return not self.is_container_running(container)

    def await_container(self, container, state, timeout = 10, delay_before = 0, delay_after = 0):
        req_state_map = {
            'running': self.is_container_running,
            'down': self.is_container_down
        }

        state_func = req_state_map.get(state, self.is_container_running)

        if delay_before > 0:
            time.sleep(delay_before)

        daemon_runtime = 0
        while not state_func(container):
            daemon_runtime += 5
            if timeout > 0 and daemon_runtime > timeout:
                raise SystemExit(f'Container await timed out after {timeout}s, still not {state}.')

            time.sleep(5)

        if delay_after > 0:
            time.sleep(delay_after)

    def get(self, key):
        if key not in self.environment:
            return None
        return self.environment[key]
