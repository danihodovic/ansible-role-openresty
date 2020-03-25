FROM openresty/openresty:latest

COPY /usr/local/openresty/bin/openresty /usr/local/bin/

# SSL dependency
RUN apk add --update openssl && \
    rm -rf /var/cache/apk/*

RUN mkdir /etc/resty-auto-ssl
# Generate fallback ssl cert
RUN openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
    -subj '/CN=sni-support-required-for-valid-ssl' \
    -keyout /etc/ssl/resty-auto-ssl-fallback.key \
    -out /etc/ssl/resty-auto-ssl-fallback.crt

# Install LuaRocks, does not support opm
# https://github.com/auto-ssl/lua-resty-auto-ssl/issues/45#issuecomment-333378971
RUN wget http://luarocks.org/releases/luarocks-3.3.1.tar.gz && \
    tar -xzvf luarocks-3.3.1.tar.gz && \
    cd luarocks-3.3.1/ && \
    ./configure --prefix=/usr/local/openresty/luajit \
    --with-lua=/usr/local/openresty/luajit/ \
    --lua-suffix=jit \
    --with-lua-include=/usr/local/openresty/luajit/include/luajit-2.1 && \
    make && \
    make install

RUN luarocks install lua-resty-auto-ssl

RUN opm install knyar/nginx-lua-prometheus ledgetech/lua-resty-http
