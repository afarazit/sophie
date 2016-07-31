#!/usr/bin/env python3

import sys
import os
import subprocess
from configparser import ConfigParser


def _get_path(path):
    return path.rstrip(os.sep).rstrip(os.altsep) + os.sep


def _get_public_path(path, enable_public_path=False):
    if enable_public_path:
        if path == '':
            return ''

        return path.rstrip(os.sep).rstrip(os.altsep) + os.sep

    return ''


def create_dir(directory):
    try:
        os.makedirs(directory)
    except IOError as e:
        exit('Error creating directory \"%s\".\n%s' % (directory, str(e)))


class Sophie:
    def __init__(self):
        self.vhost = ''
        self.repo = ''
        self.enable_public_path = False
        pass

    def run(self):
        # web server might not be install, we are exiting
        # if not os.path.isdir(self.http_conf_folder):
        #     exit('Web server config folder \"%s\" does not exists.' % self.http_conf_folder)

        if len(sys.argv) > 1:
            if '-help' == sys.argv[1]:
                exit('\nUsage: `sophie.py my_new_virtual_host.com`\n\n'
                     'Public path is per host, use -p to enable it, for example\n'
                     '`sophie.py new_new_virtual_host.com -p`\n'
                     'This will append the public path to DocumentRoot of your virtual host config\n'
                     'ex. DocumentRoot "/var/www/my_new_virtual_host.com/public"\n'
                     'Public path can be set via the "http_public_path" config parameter')
            self.vhost = sys.argv[1]
        else:
            self.vhost = input('Enter host name: ')

        if len(sys.argv) > 2:
            if sys.argv[2] == '-p':
                self.enable_public_path = True

        self.repo = self.vhost + '.git'

        # if self.vhost == '':
        #     exit('You must provide a vhost name.')

        print('Hostname is %s' % self.vhost)

        self._read_config()
        self._check_tpls_and_access()
        if self.vhost_exists():
            exit('Exiting, hostname already exists...')

        if self.enable_vhost_creation:
            replacements = {'{vhost}': self.vhost,
                            '{vhost_document_root}': _get_path(
                                self.http_www_path) + self.vhost + os.sep + _get_public_path(
                                self.http_public_path, self.enable_public_path)}
            self.create_vhost_www()
            self.create_vhost_conf(replacements)

        if self.enable_git_creation:
            replacements = {
                '{vhost_path}': _get_path(self.http_www_path) + self.repo + os.sep + _get_path(self.git_checkout_path),
                '{vhost_repo_path}': _get_path(self.git_repo_base_path) + self.repo}
            self.create_repo_dir()
            self.create_repo_conf(replacements)

    def _read_config(self):
        print('Reading config file...')
        config_file = __file__.replace('.py', '.ini')
        if not os.path.isfile(config_file):
            exit(config_file + ' not found.')

        config = ConfigParser()
        config.read(config_file)

        self.enable_vhost_creation = config.getboolean('tools', 'enable_vhost_creation')
        self.enable_git_creation = config.getboolean('tools', 'enable_git_creation')
        self.enable_chown = config.getboolean('tools', 'enable_chown')

        self.http_conf_folder = config.get('paths',
                                           'http_conf_folder')  # ex. /etc/apache2/sites-available/, web server config directory
        self.http_conf_tpl = config.get('paths',
                                        'http_conf_tpl')  # ex. /etc/apache2/conf-available/vhost.tpl, config template file
        self.http_www_path = config.get('paths', 'http_www_path')  # ex. /var/www/

        # ex. public_html/ or public_html/public,
        # the final path would be /var/www/{vhost_name}/public_html
        # or /var/www/{vhost_name}/public_html/public
        self.http_public_path = config.get('paths', 'http_public_path')

        self.git_repo_base_path = config.get('paths', 'git_repo_base_path')  # ex. /var/repos/
        self.git_repo_conf_tpl = config.get('paths', 'git_repo_conf_tpl')  # ex. /var/repos/post-receive.tpl
        self.git_checkout_path = config.get('paths',
                                            'git_checkout_path')  # ex. public_html/, set this to your vhost root folder

        self.git_executable = config.get('paths', 'git_executable')

    def _check_tpls_and_access(self):
        if not os.path.isfile(self.http_conf_tpl):
            vhost_na = input('Virtual host template file not found, use default? (y/n): ')
            if vhost_na == 'y':
                default_vhost = 'vhost.tpl'
                if not os.path.isfile(default_vhost):
                    exit('Default %s not found.' % default_vhost)
                self.http_conf_tpl = default_vhost
            else:
                exit('Update your config file.')

        if not os.path.isfile(self.git_repo_conf_tpl):
            post_receive_na = input('Git post-receive template file not found, use default? (y/n): ')
            if post_receive_na == 'y':
                default_post_receive = 'post-receive.tpl'
                if not os.path.isfile(default_post_receive):
                    exit('Default %s not found.' % default_post_receive)
                self.git_repo_conf_tpl = default_post_receive
            else:
                exit('Update your config file.')

        if not os.path.isdir(self.http_www_path):
            www_path_na = input(self.http_www_path + ' does not exists, create it? (y/n): ')

            if www_path_na == 'y':
                create_dir(self.http_www_path)
            else:
                exit('Update your config file (http_www_path).')

        if not os.path.isdir(self.git_repo_base_path):
            repo_base_na = input(self.git_repo_base_path + ' does not exists, create it? (y/n): ')

            if repo_base_na == 'y':
                create_dir(self.git_repo_base_path)
            else:
                exit('Update your config file (git_repo_base_path).')

    def vhost_exists(self):
        if self.enable_vhost_creation and self.enable_git_creation:
            return os.path.isfile(_get_path(self.http_conf_folder) + self.vhost) \
                   or os.path.isdir(_get_path(self.git_repo_base_path) + self.repo)

        if self.enable_vhost_creation:
            return os.path.isfile(_get_path(self.http_conf_folder) + self.vhost)

        if self.enable_git_creation:
            return os.path.isdir(_get_path(self.git_repo_base_path) + self.repo)

    def create_vhost_www(self):
        print("Creating web server directories.")
        base_path = _get_path(self.http_www_path)
        if not os.path.exists(base_path):
            print("\t%s" % base_path)
            create_dir(base_path)

        vhost_path = _get_path(self.http_www_path) + self.vhost
        print("\t%s" % vhost_path)
        create_dir(vhost_path)

    def create_vhost_conf(self, replacements):
        with open(self.http_conf_tpl) as infile, open(self.http_conf_folder + self.vhost + '.conf', 'w') as outfile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)

    def create_repo_dir(self):
        print("Creating git directories.")
        base_path = _get_path(self.git_repo_base_path)
        if not os.path.exists(base_path):
            print("\t%s" % base_path)
            create_dir(base_path)

        repo_path = _get_path(self.git_repo_base_path) + self.repo
        print("\t%s" % repo_path)
        create_dir(repo_path)

        # TODO this should be created via git init --bare
        # print("\t%s" % repo_path + os.sep + 'hooks')
        # create_dir(repo_path + os.sep + 'hooks')
        output = subprocess.check_output([self.git_executable + ' init --bare ' + repo_path],
                                   stderr=subprocess.PIPE,
                                   shell=True)
        print(str(output).replace("/\\n'",'').replace("b'",""))

    def create_repo_conf(self, replacements):
        print("Copying hook post-receive.")
        hooks_path = _get_path(self.git_repo_base_path) + self.repo + os.sep + 'hooks' + os.sep
        with open(self.git_repo_conf_tpl) as infile, open(hooks_path + 'post-receive', 'w') as outfile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)


sophie = Sophie()
sophie.run()
