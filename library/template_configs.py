#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

def main():
    module_args = dict(
        docker_image=dict(type="str", required=True),
        config_dir=dict(type="str", required=True),
        configs=dict(type="list", required=True),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    module.exit_json()


if __name__ == "__main__":
    main()
