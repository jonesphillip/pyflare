"""
Main App class with decorators
"""

from typing import override
from collections.abc import Callable as CallableType
from .function import Function
from .serializer import FunctionSerializer
from .executor import RemoteExecutor
from .config import load_config


class App:
    """
    Main application container for Flare functions.

    Usage:
        app = App("my-app")

        @app.function(max_containers=5)
        def my_func():
            pass

        @app.local_entrypoint()
        def main():
            result = my_func.remote()
            results = my_func.map([1, 2, 3])
    """

    def __init__(self, name: str):
        self.name: str = name
        self.functions: dict[str, Function] = {}
        self.local_entrypoint_fn: CallableType[..., object] | None = None
        self._executor: RemoteExecutor | None = None

    def function(
        self,
        max_containers: int | None = None,
        min_containers: int = 0,
        timeout: int = 300,
        env: dict[str, str] | None = None,
        **options: object,
    ) -> CallableType[[CallableType[..., object]], Function]:
        """
        Decorator to mark functions for remote execution

        Args:
            max_containers: Max parallel sandboxes (default: Worker's max_instances)
            min_containers: Min sandboxes to keep warm (default: 0, not implemented yet)
            timeout: Execution timeout in seconds (default: 300, max: 86400/24hrs)
            env: Environment variables to inject into sandbox (default: None)
            **options: Additional options for future use

        Usage:
            @app.function(max_containers=10, timeout=600)
            def process(x):
                return x * 2

            @app.function(env={"API_KEY": "secret_value"})
            def authenticated_task(x):
                import os
                api_key = os.environ['API_KEY']
                return x * 2
        """

        def decorator(fn: CallableType[..., object]) -> Function:
            # Validate options
            if max_containers is not None and max_containers < 1:
                raise ValueError("max_containers must be >= 1")
            if min_containers < 0:
                raise ValueError("min_containers must be >= 0")
            if max_containers and min_containers > max_containers:
                raise ValueError("min_containers cannot exceed max_containers")
            if timeout < 1 or timeout > 86400:  # 1 second to 24 hours
                raise ValueError("timeout must be between 1 and 86400 seconds")

            # Serialize the function
            serialized = FunctionSerializer.serialize(fn)

            # Store options
            func_options = {
                "max_containers": max_containers,
                "min_containers": min_containers,
                "timeout": timeout,
                "env": env or {},
                **options,
            }

            # Wrap it in a Function object
            func = Function(fn, self, serialized, func_options)

            # Store it
            self.functions[func.name] = func

            return func

        return decorator

    def local_entrypoint(
        self,
    ) -> CallableType[[CallableType[..., object]], CallableType[..., object]]:
        """
        Decorator to mark the local entry point

        Usage:
            @app.local_entrypoint()
            def main():
                result = process.remote(5)
                print(result)

            # With CLI arguments:
            @app.local_entrypoint()
            def main(name: str, count: int = 5):
                for i in range(count):
                    greet.remote(name)
        """

        def decorator(fn: CallableType[..., object]) -> CallableType[..., object]:
            self.local_entrypoint_fn = fn

            # Execute the entrypoint immediately when the module is run
            # Skip execution if we're doing direct function invocation (::function syntax)
            import sys

            module = sys.modules.get("__flare_main__")
            skip_entrypoint = getattr(module, "__flare_skip_entrypoint__", False) if module else False

            if not skip_entrypoint:
                # Check if CLI arguments were provided via module.__flare_cli_args__
                cli_args = getattr(module, "__flare_cli_args__", {}) if module else {}

                if cli_args:
                    fn(**cli_args)
                else:
                    fn()

            return fn

        return decorator

    @property
    def executor(self) -> RemoteExecutor:
        """Lazy-load executor with config"""
        if not self._executor:
            config = load_config()

            if not config.worker_url:
                raise ValueError(
                    (
                        "Worker URL not configured. Set it with:\n"
                        "  export FLARE_WORKER_URL=http://localhost:8787\n"
                        "Or configure it permanently with:\n"
                        "  flare config init"
                    )
                )

            if not config.api_key:
                raise ValueError(
                    (
                        "API key not configured. Set it with:\n"
                        "  export FLARE_API_KEY=your-api-key\n"
                        "Or configure it permanently with:\n"
                        "  flare config init"
                    )
                )

            self._executor = RemoteExecutor(
                worker_url=config.worker_url, api_key=config.api_key
            )

        return self._executor

    @override
    def __repr__(self) -> str:
        return f"<App {self.name} ({len(self.functions)} functions)>"
