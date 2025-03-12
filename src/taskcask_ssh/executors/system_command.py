import logging
from typing import Any

from fabric import Connection

from taskcask_common.environment import BaseEnvironment
from taskcask_common.executor import BaseExecutor
from taskcask_common.task import Task
from taskcask_common.task_templates.system_command import SystemCommandTaskTemplate
from ..environments import SshEnvironment


class SystemCommandExecutor(BaseExecutor):
    """
    Runs a system command with provided arguments
    """
    log = logging.getLogger(__name__)

    def can_execute(task: Task, env: BaseEnvironment) -> bool:

        return isinstance(task.template, SystemCommandTaskTemplate) \
            and isinstance(env, SshEnvironment)

    def execute(self, task: Task, env: BaseEnvironment) -> Any:
        tpl: SystemCommandTaskTemplate = task.template
        cmd = tpl.cmd + task.args
        env_dict = {**env.env, **tpl.env}
        command_string = " ".join(['"'+part+'"' if " " in part else part for part in cmd])

        with Connection(env.host, user=env.user, port=env.port) as c:
            result = c.run(command_string, hide=True, env=env_dict)
        return result.stdout
