upstream socketio_nodes {
  ip_hash;
  server chat:${APP_PORT};
  # to scale the app, just add more nodes here!
}

server {
  listen ${NGINX_PORT};
  server_name ${NGINX_HOST};
  client_max_body_size 10M;

  location / {
    proxy_pass http://chat:${APP_PORT};
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Host $host;
    proxy_set_header X-Original-URI $request_uri;
  }

  location /static/ {
    alias /app/static/;
  }

  location /socket.io {
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_pass http://socketio_nodes/socket.io;
  }
}
