# Sophie, automating virtual host and git (bare) repo creation #


Usage: `sophie.py my_new_virtual_host.com`

Public path is per host, use -p to enable it, for example
`sophie.py new_new_virtual_host.com -p`
This will append the public path to DocumentRoot of your virtual host config
ex. DocumentRoot "/var/www/my_new_virtual_host.com/public"
Public path can be set via the "http_public_path" config parameter