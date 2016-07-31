<VirtualHost *:80>
    ServerAdmin webmaster@{vhost}
    DocumentRoot "{vhost_document_root}"
    ServerName {vhost}
    ErrorLog "logs/{vhost}-error.log"
    CustomLog "logs/{vhost}-access.log" common
    <Directory "{vhost_document_root}">
       Allow from all
       AllowOverride all
       Require all granted
    </Directory>    
</VirtualHost>