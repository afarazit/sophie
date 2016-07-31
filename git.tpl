#!/bin/sh
git --work-tree={vhost_path} --git-dir={vhost_repo_path} checkout -f
chown -R www-data:www-data {vhost_path}
