import importlib
import importlib.util
import io
import logging
from typing import Any

from fabric import Connection

from ..environments import SshEnvironment

from taskcask_common.environment import BaseEnvironment
from taskcask_common.executor import BaseExecutor
from taskcask_common.task import Task
from taskcask_common.utils.sys import args_to_args_and_kwargs

from taskcask.stdlib.task_templates.python import PythonTaskTemplate


class PythonExecutor(BaseExecutor):
    """
    Runs a python script
    """
    log = logging.getLogger(__name__)

    def can_execute(task: Task, env: BaseEnvironment) -> bool:
        return isinstance(task.template, PythonTaskTemplate) \
            and isinstance(env, SshEnvironment)

    def execute(self, task: Task, env: BaseEnvironment) -> Any:
        tpl: PythonTaskTemplate = task.template

        if tpl.module_path is not None:
            module_path, function_name = tpl.module_path.rsplit(":", 1)
            module = importlib.import_module(module_path)
        elif tpl.file_path is not None:
            module_path, function_name = tpl.file_path.rsplit(":", 1)
            spec = importlib.util.spec_from_file_location("my_module", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        (task_args, task_kwargs) = args_to_args_and_kwargs(task.args)
        args = tpl.args + task_args
        kwargs = {**tpl.kwargs, **task_kwargs}

        output: str = None
        with open(module.__file__, "r") as f:
            py_code = f.read()
        fn_signature = _format_function_signature(args, kwargs)
        py_code += f"\n{function_name}({fn_signature})"
        py_code = io.StringIO(py_code)
        with Connection(env.host, user=env.user, port=env.port) as c:
            result = c.run("python -", hide=True, env=env.env, in_stream=py_code)
        output = result.stdout

        return output


def _format_function_signature(py_args: list, py_kwargs: dict) -> str:
    """
    Converts Python args and kwargs into string representations parseable inside scripts.
    Works with simple types and collections only
    """
    args_str = ", ".join(map(repr, py_args))
    kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in py_kwargs.items())
    if args_str and kwargs_str:
        return f"{args_str}, {kwargs_str}"
    elif args_str:
        return args_str
    elif kwargs_str:
        return kwargs_str
    else:
        return ""
