#!/usr/bin/env python3

import os
import stat
import argparse
import subprocess
from configparser import ConfigParser


def _get_path(path):
    return path.rstrip(os.sep).rstrip(os.altsep) + os.sep


def _get_public_path(path, enable_public_path=False):
    if enable_public_path:
        if path == '':
            return os.sep

        return path.rstrip(os.sep).rstrip(os.altsep) + os.sep

    return ''


def create_dir(directory):
    try:
        os.makedirs(directory)
    except IOError as e:
        exit('Error creating directory \"%s\".\n%s' % (directory, str(e)))


def _args():
    parser = argparse.ArgumentParser(description='Sophie, automating virtual host and git (bare) repo creation')
    parser.add_argument('hostname', help='The hostname.')
    parser.add_argument('-p', '--with-public',
                        help='This will append the public path to DocumentRoot of your virtual host config'
                             'ex. DocumentRoot "/var/www/my_new_virtual_host.com/public".'
                             'Public path can be set via the "http_document_root" config setting', action='store_true')
    parser.add_argument('-np', '--without-public', help='Do not append public path', action='store_false')
    parser.add_argument('-g', '--with-git', help='Create git repo, can also be set via the "enable_git_creation" config'
                                                 ' setting', action='store_true')
    parser.add_argument('-ng', '--without-git', help='Do not create git repo, can also be set via the "enable_git'
                                                     'creation" config setting', action='store_false')
    parser.add_argument('-v', '--with-vhost', help='Create virtual host, can also be set via the "enable_vhost_creation'
                                                   '" config setting', action='store_true')
    parser.add_argument('-nv', '--without-vhost', help='Do not create virtual host, can also be set via the "enable_'
                                                       'vhost_creation" config setting', action='store_false')
    return parser.parse_args()


class Http:
    http_www_path = None
    http_conf_folder = None
    http_conf_tpl = None
    http_document_root = None
    enable_public_path = None

    def __init__(self, vhost):
        self.vhost = vhost

    def run(self):

        self._check_tpls_and_access()
        self.check_if_exists()

        replacements = {'{vhost}': self.vhost,
                        '{vhost_document_root}': _get_path(
                            Http.http_www_path) + self.vhost + os.sep + _get_public_path(
                            Http.http_document_root, Http.enable_public_path)}
        self.create_vhost_www()
        self.create_vhost_conf(replacements)

    def _check_tpls_and_access(self):
        if not os.path.isfile(Http.http_conf_tpl):
            vhost_na = input('Virtual host template file not found, use default? (y/n): ')
            if vhost_na == 'y':
                default_vhost = 'vhost.tpl'
                if not os.path.isfile(default_vhost):
                    exit('Default %s not found.' % default_vhost)
                Http.http_conf_tpl = default_vhost
            else:
                exit('Update your config file.')

        if not os.path.isdir(Http.http_www_path):
            www_path_na = input(Http.http_www_path + ' does not exists, create it? (y/n): ')

            if www_path_na == 'y':
                create_dir(Http.http_www_path)
            else:
                exit('Update your config file (http_www_path).')

    def check_if_exists(self):
        www_vhost_dir = _get_path(Http.http_www_path) + self.vhost
        if os.path.isdir(www_vhost_dir):
            exit('Exiting, "%s" exists.' % www_vhost_dir)

        www_vhost_conf = _get_path(Http.http_conf_folder) + self.vhost
        if os.path.isfile(www_vhost_dir):
            exit('Exiting, "%s" exists.' % www_vhost_conf)

    def create_vhost_www(self):
        print("Creating web server directories.")
        base_path = _get_path(Http.http_www_path)
        if not os.path.exists(base_path):
            print("\t%s" % base_path)
            create_dir(base_path)

        vhost_path = _get_path(Http.http_www_path) + self.vhost + os.sep + _get_public_path(
            Http.http_document_root, Http.enable_public_path)
        print("\t%s" % vhost_path)
        create_dir(vhost_path)

    def create_vhost_conf(self, replacements):
        with open(Http.http_conf_tpl) as infile, open(Http.http_conf_folder + self.vhost + '.conf', 'w+') as outfile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)


class Git:
    http_www_path = None
    git_repo_base_path = None
    git_repo_conf_tpl = None
    git_checkout_path = None
    git_executable = None

    def __init__(self, vhost):
        self.vhost = vhost
        self.repo = vhost + '.git'

    def run(self):

        self._check_tpls_and_access()
        self.check_if_exists()

        replacements = {
            '{vhost_path}': _get_path(Git.http_www_path) + self.vhost + os.sep + _get_path(Git.git_checkout_path),
            '{vhost_repo_path}': _get_path(Git.git_repo_base_path) + self.repo,
            '{chown}': _get_path(Git.http_www_path) + self.vhost + os.sep}
        self.create_repo_dir()
        self.create_repo_conf(replacements)

    def _check_tpls_and_access(self):
        if not os.path.isfile(Git.git_repo_conf_tpl):
            post_receive_na = input('Git post-receive template file not found, use default? (y/n): ')
            if post_receive_na == 'y':
                default_post_receive = 'post-receive.tpl'
                if not os.path.isfile(default_post_receive):
                    exit('Default %s not found.' % default_post_receive)
                self.git_repo_conf_tpl = default_post_receive
            else:
                exit('Update your config file.')

        if not os.path.isdir(Git.git_repo_base_path):
            repo_base_na = input(Git.git_repo_base_path + ' does not exists, create it? (y/n): ')

            if repo_base_na == 'y':
                create_dir(Git.git_repo_base_path)
            else:
                exit('Update your config file (git_repo_base_path).')

    def check_if_exists(self):
        git_base_path = _get_path(Git.git_repo_base_path) + self.repo
        if os.path.isdir(git_base_path):
            exit('Exiting, "%s" exists.' % git_base_path)

    def create_repo_dir(self):
        print("Creating git directories.")
        base_path = _get_path(Git.git_repo_base_path)
        if not os.path.exists(base_path):
            print("\t%s" % base_path)
            create_dir(base_path)

        repo_path = _get_path(Git.git_repo_base_path) + self.repo
        print("\t%s" % repo_path)
        create_dir(repo_path)

        # print("\t%s" % repo_path + os.sep + 'hooks')
        # create_dir(repo_path + os.sep + 'hooks')
        output = subprocess.check_output([Git.git_executable + ' init --bare ' + repo_path],
                                         stderr=subprocess.PIPE,
                                         shell=True)
        print(str(output).replace("/\\n'", '').replace("b'", ""))

    def create_repo_conf(self, replacements):
        print("Copying hook post-receive.")
        hooks_path = _get_path(Git.git_repo_base_path) + self.repo + os.sep + 'hooks' + os.sep
        post_receive_file = hooks_path + 'post-receive'
        with open(Git.git_repo_conf_tpl) as infile, open(post_receive_file, 'w+') as outfile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)

        if os.name == 'posix':
            st = os.stat(post_receive_file)
            os.chmod(post_receive_file, st.st_mode | stat.S_IEXEC)


class Sophie:
    def __init__(self):
        self.vhost = ''
        self.repo = ''

        self.args = None

    def run(self):
        self.args = _args()
        self._read_config()

        if self.enable_vhost_creation is False and self.enable_git_creation is False:
            exit('It seems you do not want to create anything...')

        self.vhost = self.args.hostname

        confirm = input('Hostname is %s, continue? (y/n): ' % self.vhost)
        if confirm != 'y':
            exit()

        if self.enable_vhost_creation:
            http = Http(vhost=self.vhost)
            http.run()

        if self.enable_git_creation:
            git = Git(vhost=self.vhost)
            git.run()

    def _read_config(self):
        config_file = __file__.replace('.py', '.ini')
        if not os.path.isfile(config_file):
            exit(config_file + ' not found.')

        config = ConfigParser()
        config.read(config_file)

        self.enable_vhost_creation = config.getboolean('tools', 'enable_vhost_creation')
        self.enable_git_creation = config.getboolean('tools', 'enable_git_creation')
        self.enable_chown = config.getboolean('tools', 'enable_chown')
        Http.enable_public_path = config.getboolean('tools', 'enable_public_path')
        Http.http_conf_folder = config.get('paths', 'http_conf_folder')
        Http.http_conf_tpl = config.get('paths', 'http_conf_tpl')
        Http.http_www_path = Git.http_www_path = config.get('paths', 'http_www_path')
        Http.http_document_root = config.get('paths', 'http_document_root')
        Git.git_repo_base_path = config.get('paths', 'git_repo_base_path')
        Git.git_repo_conf_tpl = config.get('paths', 'git_repo_conf_tpl')
        Git.git_checkout_path = config.get('paths', 'git_checkout_path')
        Git.git_executable = config.get('paths', 'git_executable')

        if self.args.with_git:
            self.enable_git_creation = True

        if self.args.without_git is False:
            self.enable_git_creation = False

        if self.args.with_public:
            Http.enable_public_path = True

        if self.args.without_public is False:
            Http.enable_public_path = False

        if self.args.with_vhost is True:
            self.enable_vhost_creation = True

        if self.args.without_vhost is False:
            self.enable_vhost_creation = False


sophie = Sophie()
sophie.run()
