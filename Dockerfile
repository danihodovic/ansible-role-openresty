FROM openresty/openresty:1.13.6.2-2-alpine-fat
RUN opm install knyar/nginx-lua-prometheus ledgetech/lua-resty-http
