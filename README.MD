# Sophie, automating virtual host and git (bare) repo creation #

Sophie automates the creation of virtual hosts and git repos

<pre>
$ ./sophie.py --help
usage: sophie.py [-h] [-p] [-g] [-v] [-np] [-ng] [-nv] hostname

Sophie, automating virtual host and git (bare) repo creation

positional arguments:
  hostname              The hostname.

optional arguments:
  -h, --help            show this help message and exit
  -p, --with-public     This will append the public path to DocumentRoot of
                        your virtual host config ex. DocumentRoot
                        "/var/www/{vhost_name}/public". Public path can be set
                        via the "http_document_root" config setting
  -g, --with-git        Create git repo, can also be set via the
                        "enable_git_creation" config setting
  -v, --with-vhost      Create virtual host, can also be set via the
                        "enable_vhost_creation" config setting
  -np, --without-public
                        Do not append public path
  -ng, --without-git    Do not create git repo, can also be set via the
                        "enable_gitcreation" config setting
  -nv, --without-vhost  Do not create virtual host, can also be set via the
                        "enable_vhost_creation" config setting
</pre>