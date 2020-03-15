# ansible-openresty

Role to deploy a Docker container with Openresty.

Includes opt-in config for rate limiting, Prometheus metrics and default proxy
config.

## Examples

```yml
- name: Deploy Openresty
  hosts: localhost
  vars:
    ansible_become: true
  tasks:
    - import_role:
        name: ansible-role-openresty
      vars:
        openresty_vhosts:
          default: |
            server {
              # if no Host match, close the connection to prevent host spoofing
              return 444;
            }
          myserver: |
            server {
              server myserver.org;
              location / {
                proxy_pass: http://mycontainer;
              }
            }
        openresty_includes:
          - proxy.conf
          - rate_limit.conf
          - prometheus_metrics.conf
```

### With lua-resty-auto-ssl

For running Openresty with auto SSL the following additions are needed:

- Defining the variable openresty_ssl_domains. The domains in the list will be added to a regex pattern and only these domains will be eligible for querying Let's Encrypt for a SSL certificate.
- Add the '{{ nginx_auto_ssl_config|index(2)}}' to your vhost server block as this will add the necessary lua blocks for starting the SSL certificate creation process and it will define fallback SSL certs so that nginx can start.

```yml
- name: Deploy Openresty
  hosts: localhost
  become: true
  tasks:
    - import_role:
        name: ansible-openresty
      vars:
        openresty_vhosts:
          findwork-dev: |
            server {
              listen 443 ssl;
              server_name findwork.dev;

              {{ nginx_auto_ssl_config|indent(2) }}

              location / {
                add_header Content-Type text/plain;
                return 200 'Hello HTTPS world!';
              }
            }
        openresty_includes:
          - proxy.conf
          - ssl.conf
          - logging.conf
        openresty_ssl_domains:
          - findwork.dev
```

## Requirements
- docker daemon installed on the host
- docker pip library installed on the host `pip install docker`
