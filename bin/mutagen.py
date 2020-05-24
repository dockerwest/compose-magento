import subprocess
import os
from environment import Environment

class Mutagen:

    EXEC_NAME = 'mutagen'
    EXEC_SYNC_PARAM = 'sync'

    def __init__(self, env: Environment):
        self.env = env

    def session_exists(self, session_name):
        self.check_availability()

        cmd = [
            self.EXEC_NAME, self.EXEC_SYNC_PARAM, 'list'
        ]

        # Using universal_newlines to assure a string is always returned, avoiding issues with the .find params later on
        mutagen_list = subprocess.check_output(cmd, universal_newlines=True)
        mutagen_session_list_ref = 'Name: ' + session_name

        return mutagen_list.find(mutagen_session_list_ref) != -1

    def session_create(self, session_name, alpha_path, beta_container_name):
        self.check_availability()

        cmd = [
                self.EXEC_NAME, 'create', 
                '--label=dockerwest-magento-file-sync',
                '--name=' + session_name,
                '--sync-mode=two-way-resolved',
                '--default-file-mode=0644',
                '--default-directory-mode=0755',
                '--ignore=/.idea',
                '--ignore=/.magento',
                '--ignore=/.docker',
                '--ignore=/.github',
                '--ignore=*.sql',
                '--ignore=*.gz',
                '--ignore=*.zip',
                '--ignore=*.bz2',
                '--ignore-vcs',
                '--symlink-mode=posix-raw',
                alpha_path,
                # TODO: revalidate user. Experiencing permission issues with /generated files after Magerun usage.
                'docker://www-data@' + beta_container_name + '/phpapp'
            ]

        return subprocess.check_output(cmd, universal_newlines=True)

    def session_resume(self, session_name):
        self.check_availability()

        cmd = [
            self.EXEC_NAME, self.EXEC_SYNC_PARAM, 'resume', session_name
        ]

        return subprocess.check_output(cmd, universal_newlines=True)

    def session_pause(self, session_name):
        self.check_availability()

        cmd = [
            self.EXEC_NAME, self.EXEC_SYNC_PARAM, 'pause', session_name
        ]

        return subprocess.check_output(cmd, universal_newlines=True)

    def session_monitor(self, session_name):
        self.check_availability()

        cmd = [
            self.EXEC_NAME, self.EXEC_SYNC_PARAM, 'monitor', session_name
        ]

        os.execvp(cmd[0], cmd)
    
    def session_terminate(self, session_name):
        self.check_availability()

        cmd = [
            self.EXEC_NAME, self.EXEC_SYNC_PARAM, 'terminate', session_name
        ]

        return subprocess.check_output(cmd, universal_newlines=True)

    def session_init(self, session_name, alpha_path, beta_container_name):
        if not self.session_exists(session_name):
            self.session_create(session_name, alpha_path, beta_container_name)

        return self.session_resume(session_name)

    def check_availability(self):
        if not self.env.is_tool_available(self.EXEC_NAME):
            raise SystemExit('Mutagen tooling was called, but not available on system. Please review Mutagen installation.')


    def get_session_name(self):
        return 'dockerwest-sync-' + self.env.get_project_name()