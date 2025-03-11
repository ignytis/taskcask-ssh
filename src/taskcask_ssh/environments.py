from typing import Literal

from taskcask_common.environment import BaseEnvironment
from taskcask_common.typedefs import EnvVars


class SshEnvironment(BaseEnvironment):
    """
    Remote server (SSH connection)
    """
    kind: Literal["ssh"] = "ssh"
    env: EnvVars
    host: str
    port: str = "22"
    user: str
    """Environment variables"""
