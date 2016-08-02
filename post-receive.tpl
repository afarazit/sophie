#!/bin/sh
echo 'git checkout'
git --work-tree={vhost_path} --git-dir={vhost_repo_path} checkout -f
echo 'changing permissions to www-data:www-data'
chown -R www-data:www-data {chown}
