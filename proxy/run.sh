#!/bin/sh

set -e

envsubst '${NGINX_HOST},${NGINX_PORT},${FLASK_HOST},${FLASK_PORT}' \
  < /etc/nginx/default.conf.tpl \
  > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'
