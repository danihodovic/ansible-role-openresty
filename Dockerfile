FROM openresty/openresty:1.19.3.1-0-alpine-fat

RUN ln -s /usr/local/openresty/bin/openresty /usr/local/bin/

# SSL dependency
RUN apk add --update openssl && \
    rm -rf /var/cache/apk/*

RUN mkdir /etc/resty-auto-ssl

# Generate fallback ssl cert
RUN openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
    -subj '/CN=sni-support-required-for-valid-ssl' \
    -keyout /etc/ssl/resty-auto-ssl-fallback.key \
    -out /etc/ssl/resty-auto-ssl-fallback.crt

RUN luarocks install lua-resty-auto-ssl

RUN opm install knyar/nginx-lua-prometheus ledgetech/lua-resty-http
