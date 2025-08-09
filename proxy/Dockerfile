FROM nginxinc/nginx-unprivileged:1-alpine
COPY ./proxy/default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./proxy/run.sh /run.sh
USER root
RUN touch /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh
USER nginx
CMD ["/run.sh"]
