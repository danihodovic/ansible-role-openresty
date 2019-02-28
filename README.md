# ansible-openresty

Role to deploy a Docker container with Openresty.

Includes opt-in config for rate limiting, Prometheus metrics and default proxy
config.

### Examples
```yml
- name: Deploy Openresty
  hosts: localhost
  vars:
    ansible_become: true
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
  tasks:
    - import_role:
        name: ansible-role-openresty
```

### Requirements
- docker daemon installed on the host
- docker pip library installed on the host `pip install docker`
