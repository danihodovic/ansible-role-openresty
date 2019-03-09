FROM openresty/openresty:1.15.8.1rc1-0-alpine-fat
RUN opm install knyar/nginx-lua-prometheus ledgetech/lua-resty-http
