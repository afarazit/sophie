import sys
import os
import subprocess

enable_vhost_creation = True
enable_git_creation = True
enable_chown = False

http_conf_folder = 'c:/Users/afarazit/temp/a2conf/'  # ex. /etc/apache2/conf-available/, web server config directory
http_conf_tpl = 'c:/Users/afarazit/temp/a2vhost.tpl'  # ex. /etc/apache2/conf-available/vhost.tpl, config template file
http_www_path = 'c:/Users/afarazit/temp/var_www/'  # ex. /var/www/

# ex. public_html/ or public_html/public,
# the final path would be /var/www/{vhost_name}/public_html
# or /var/www/{vhost_name}/public_html/public
http_public_path = 'public/'

git_repo_base_path = 'c:/Users/afarazit/temp/var_repos/'  # ex. /var/repos/
git_repo_conf_tpl = 'c:/Users/afarazit/temp/git.tpl'  # ex. /var/repos/post-receive.tpl
git_checkout_path = 'public_html/'  # ex. public_html/, set this to your vhost root folder

git_executable = 'git.exe '


def _get_path(path):
    return path.rstrip(os.sep).rstrip(os.altsep) + os.sep


def _get_public_path(path):
    if path == '':
        return

    return path.rstrip(os.sep).rstrip(os.altsep) + os.sep


def _check_for_access():
    print("TODO: check for file and folder access")


class Sophie:
    def __init__(self):
        self.vhost = ''
        self.repo = ''
        pass

    def run(self):
        if len(sys.argv) > 1:
            self.vhost = sys.argv[1]
        else:
            self.vhost = input('Enter host name: ')

        self.repo = self.vhost + '.git'

        if self.vhost == '':
            exit('You must provide a vhost name.')

        print('Hostname is %s' % self.vhost)

        _check_for_access()
        self.read_config()
        if self.vhost_exists():
            exit('Exiting, hostname already exists...')

        if enable_vhost_creation:
            replacements = {'{vhost}': self.vhost,
                            '{vhost_document_root}': _get_path(http_www_path) + self.vhost + os.sep + _get_public_path(
                                http_public_path)}
            self.create_vhost_dir()
            self.create_vhost_conf(replacements)

        if enable_git_creation:
            replacements = {
                '{vhost_path}': _get_path(http_www_path) + self.repo + os.sep + _get_path(git_checkout_path),
                '{vhost_repo_path}': _get_path(git_repo_base_path) + self.repo}
            self.create_repo_dir()
            self.create_repo_conf(replacements)

    def vhost_exists(self):
        if enable_vhost_creation and enable_git_creation:
            return os.path.isfile(_get_path(http_conf_folder) + self.vhost) \
                   or os.path.isdir(_get_path(git_repo_base_path) + self.vhost + '.git')

        if enable_vhost_creation:
            return os.path.isfile(_get_path(http_conf_folder) + self.vhost)

        if enable_git_creation:
            return os.path.isdir(_get_path(git_repo_base_path) + self.vhost + '.git')

    def read_config(self):
        pass

    def create_vhost_dir(self):
        print("Creating web server directories.")
        base_path = _get_path(http_www_path)
        if not os.path.exists(base_path):
            print("\t%s" % base_path)
            os.makedirs(base_path)

        vhost_path = _get_path(http_www_path) + self.vhost
        print("\t%s" % vhost_path)
        os.makedirs(vhost_path)

    def create_vhost_conf(self, replacements):
        with open(http_conf_tpl) as infile, open(http_conf_folder + self.vhost + '.conf', 'w') as outfile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)

    def create_repo_dir(self):
        print("Creating git directories.")
        base_path = _get_path(git_repo_base_path)
        if not os.path.exists(base_path):
            print("\t%s" % base_path)
            os.makedirs(base_path)

        repo_path = _get_path(git_repo_base_path) + self.repo
        print("\t%s" % repo_path)
        os.makedirs(repo_path)

        # TODO this should be created via git init --bare
        # print("\t%s" % repo_path + os.sep + 'hooks')
        # os.makedirs(repo_path + os.sep + 'hooks')
        print(git_executable + 'init --bare ' + repo_path)
        process = subprocess.Popen([git_executable + ' init --bare ' + repo_path], stdout=subprocess.PIPE)
        test = process.communicate()[0]

    def create_repo_conf(self, replacements):
        print("Copying hook post-receive.")
        hooks_path = _get_path(git_repo_base_path) + self.repo + os.sep + 'hooks' + os.sep
        with open(git_repo_conf_tpl) as infile, open(hooks_path + 'post-receive', 'w') as outfile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                outfile.write(line)


sophie = Sophie()

sophie.run()
