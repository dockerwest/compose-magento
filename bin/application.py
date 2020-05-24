import subprocess
import sys
import os
from environment import Environment
from mutagen import Mutagen

class Application:

    CONTAINER_SERVICE_NAME = 'application'

    def __init__(self, env: Environment):
        self.env = env

    def get_file_sync_method_name(self):
        var_map = {
            'mutagen': 'mutagen',
            'none': None
        }

        method_name = var_map.get(self.env.get('APPLICATION_FILE_SYNC'), False)

        if method_name is False:
            raise SystemExit('Invalid APPLICATION_FILE_SYNC value was defined, please review .env settings.')

        return method_name

    def start_file_sync_daemon(self):
        file_sync_method_name = self.get_file_sync_method_name()
        if file_sync_method_name is None:
            return

        # TODO: tried threading, no luck with first attempts. Should get rid of "application" dependency
        file_sync_daemon_cmd = [
            os.path.dirname(sys.argv[0]) + '/application',
            'file-sync', 'daemon', 'up-down'
        ]
        subprocess.Popen(file_sync_daemon_cmd)

    def get_file_sync_method(self, method_type):
        var_map = {
            'up_mutagen': self.up_mutagen_sync,
            'down_mutagen': self.down_mutagen_sync
        }

        sync_method_name = self.get_file_sync_method_name()
        target_func = var_map.get(f'{method_type}_{sync_method_name}', None)

        if target_func is None:
            raise SystemExit(f'Could not map APPLICATION_FILE_SYNC value {sync_method_name} to an up-method, implementation is missing.')

        return target_func

    def up_file_sync(self, ignore_container_state = False, daemon = False):
        up_func = self.get_file_sync_method('up')

        if not ignore_container_state and not self.is_container_running():
            if not daemon:
                raise SystemExit(f'Could not start file sync, {self.CONTAINER_SERVICE_NAME} container is not running.')

            # 1800 secs, 30 min timeout, making sure download time is covered
            # Adding delay_after too, giving the container some time become actually available
            self.await_container('running', 1800, 0, 5)

        return up_func()

    def down_file_sync(self, ignore_container_state = False, daemon = False):
        down_func = self.get_file_sync_method('down')

        if not ignore_container_state and not self.is_container_down():
            if not daemon:
                raise SystemExit(f'Could not stop file sync, {self.CONTAINER_SERVICE_NAME} container is still running. Use helpers or direct command to manually halt the sync.')

            self.await_container('down', -1)

        return down_func()

    def up_down_file_sync(self, ignore_container_state = False, daemon = False):
        self.up_file_sync(ignore_container_state, daemon)

        try:
            self.down_file_sync(ignore_container_state, daemon)
        except KeyboardInterrupt:
            if daemon:
                print('Detected Ctrl+C on file-sync up-down daemon, attempting to stop file sync')
                self.down_file_sync(ignore_container_state)
                return None

        return('Succesfully started and stopped file sync, exiting.')

    def up_mutagen_sync(self):
        mutagen = Mutagen(self.env)
        return mutagen.session_init(mutagen.get_session_name(), self.env.get('APPLICATION'), self.get_container_name())

    def down_mutagen_sync(self):
        mutagen = Mutagen(self.env)
        return mutagen.session_terminate(mutagen.get_session_name())

    def is_container_running(self):
        return self.env.is_container_running(self.CONTAINER_SERVICE_NAME)

    def is_container_down(self):
        return self.env.is_container_down(self.CONTAINER_SERVICE_NAME)

    def get_container_name(self):
        return self.env.get_container_name(self.CONTAINER_SERVICE_NAME)

    def await_container(self, state, timeout = 10, delay_before = 0, delay_after = 0):
        return self.env.await_container(self.CONTAINER_SERVICE_NAME, state, timeout, delay_before, delay_after)