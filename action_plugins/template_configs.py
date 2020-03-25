from __future__ import absolute_import, division, print_function

import os
from pathlib import Path

from ansible.errors import AnsibleError
from ansible.playbook.task import Task
from ansible.plugins.action import ActionBase
from ansible.plugins.action.copy import ActionModule as Copy

__metaclass__ = type  # pylint: disable=invalid-name


# Remove details in the generated nginx config comments which are path specific
# and causes the role not to be idempotent
def _clean_configs(nginx_config_check_output):
    # Remove the first three lines which are path specific and ruins our diff,
    # e.g
    # nginx: the configuration file /tmp/ansible-role-openresty-m432ku09/nginx.conf syntax is ok
    # nginx: configuration file /tmp/ansible-role-openresty-m432ku09/nginx.conf test is successful
    dirty_lines = nginx_config_check_output.split("\n")[3:]
    lines = []
    # Remove other path specific lines, e.g
    # configuration file /tmp/ansible-role-openresty-javi1rfe/conf.d/proxy.conf:
    for line in dirty_lines:
        if not line.startswith("# configuration file "):
            lines.append(line)
    return "\n".join(lines)


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        # Validate args
        self._execute(
            tmp=tmp, task_vars=task_vars, module_args=module_args,
        )

        self.docker_image = module_args["docker_image"]
        config_dir = module_args["config_dir"]
        config_file = Path(config_dir) / "nginx.conf"
        configs = module_args["configs"]

        tmp_result = self._execute(
            module_name="tempfile",
            module_args={"state": "directory", "prefix": "ansible-role-openresty-"},
        )
        tmp_path = tmp_result["path"]

        for entry in configs:
            path = Path(tmp_path) / entry["dest"]
            self._execute(
                module_name="file",
                module_args={"state": "directory", "path": str(path.parent)},
            )
            self._copy(
                tmp=tmp,
                # task_vars=task_vars,
                task_vars=None,
                dest=str(path),
                content=entry["content"],
            )

        new_config = self._check_config(os.path.join(tmp_path, "nginx.conf"))

        try:
            old_config = self._check_config(str(config_file))
        except AnsibleError:
            old_config = ""

        if new_config != old_config:
            result["changed"] = True

            # Remove old config files for idempotency
            self._connection._shell.remove(f"{config_dir}/*", recurse=True)
            # Template configs
            for entry in configs:
                path = Path(config_dir) / entry["dest"]
                self._execute(
                    module_name="file",
                    module_args={"state": "directory", "path": str(path.parent)},
                )
                self._copy(
                    tmp=tmp,
                    task_vars=None,
                    # tmp=tmp,
                    # task_vars=task_vars,
                    dest=str(path),
                    content=entry["content"],
                )

        else:
            result["changed"] = False

        return result

    def _execute(self, *args, **kwargs):
        res = self._execute_module(*args, **kwargs)
        if res.get("failed"):
            raise AnsibleError(res)
        return res

    def _check_config(self, config_path):
        parent_dir = Path(config_path).parent
        check_config = self._execute(
            module_name="docker_container",
            task_vars={"failed_when": "false"},
            module_args={
                "image": self.docker_image,
                "name": "check-openresty-configs",
                "command": ["openresty", "-T", "-c", config_path,],
                "detach": "false",
                "cleanup": "true",
                "volumes": [f"{parent_dir}:{parent_dir}"],
            },
        )
        return _clean_configs(check_config["container"]["Output"])

    def _copy(
        self, tmp, task_vars, dest, src=None, content=None
    ):  # pylint: disable=too-many-arguments
        task = Task()
        task.args = {
            "dest": dest,
            "content": content,
            "src": src,
        }
        res = Copy(
            task=task,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj,
        ).run(tmp, task_vars)

        if res.get("failed"):
            raise AnsibleError(res)
