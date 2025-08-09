#!/bin/sh

set -e

envsubst '${NGINX_PORT},${NGINX_HOST},${APP_PORT}' \
  < /etc/nginx/default.conf.tpl \
  > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'
