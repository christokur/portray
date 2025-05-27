#!/usr/bin/env python3  # noqa: EXE001
"""
GitHub Workflow Utilities.

This script provides utilities for interacting with GitHub workflows, specifically
for getting the latest workflow ID and checking workflow action phases.
"""
from __future__ import annotations

import os
import pathlib
import sys
import typing
from pathlib import Path
from typing import TYPE_CHECKING

import dotenv
import toolbag.version
import typer
from toolbag.utils.helpers import want_version

import b2b_cli
from b2b_cli._commands.repositories._repositories_command import B2bRepositoriesCommand
from b2b_cli.cli._options import B2B_CLI_OPTIONS
from b2b_cli.cli.repositories._repositories_options import REPOSITORIES_CLI_OPTIONS
from b2b_cli.errors import B2bEnvironmentError
from b2b_cli.handlers._github.github_workflows import DEFAULT_STEP
from b2b_cli.models.enum_output_format import OutputFormatEnum
from b2b_cli.models.enum_table_coloring import B2bTableColoringEnum

path = str(pathlib.Path(__file__).resolve().parent)
if path not in sys.path:
    sys.path.append(path)

if TYPE_CHECKING:
    from b2b_cli.environment.b2b import B2bEnvironment
    from b2b_cli.handlers.b2b_github_handler import B2bGithubHandler

want_version("python-toolbag", toolbag.version.__version__, ">=0.26.19")
want_version("b2b-cli", b2b_cli.__version__, ">=0.39.26")

# Constants
__version__ = "0.26.74"


REPOSITORIES_CLI_OPTIONS["output_workflows"] = typer.Option(
    OutputFormatEnum.TABLE,
    "--output",
    help="The CLI output format.",
    case_sensitive=False,
)
REPOSITORIES_CLI_OPTIONS["output_result"] = typer.Option(
    OutputFormatEnum.STYLED,
    "--output",
    help="The CLI output format.",
    case_sensitive=False,
)
REPOSITORIES_CLI_OPTIONS["github_repository"] = typer.Option(
    None,
    "--repository",
    "--github-repository",
    envvar="GITHUB_REPOSITORY",
    help="GitHub repository in owner/repo format",
)
REPOSITORIES_CLI_OPTIONS["max_workflows"] = typer.Option(
    100,
    "--max-workflows",
    help="Maximum number of workflows to return",
)
REPOSITORIES_CLI_OPTIONS["use_regex"] = typer.Option(
    False,
    "--use-regex",
    help="Use regex for pattern matching",
)
REPOSITORIES_CLI_OPTIONS["limit"] = typer.Option(
    5,
    "--limit",
    help="Maximum number of results to return",
)
REPOSITORIES_CLI_OPTIONS["environment_name"] = typer.Option(
    None,
    "--environment",
    "--environment-name",
    envvar="ENVIRONMENT_NAME",
    help="Name of the environment",
)
REPOSITORIES_CLI_OPTIONS["branch"] = typer.Option(
    None,
    "--branch",
    envvar="GITHUB_REF_NAME",
    help="Branch name",
)
REPOSITORIES_CLI_OPTIONS["timeout"] = typer.Option(
    None,
    "--timeout",
    envvar="WATCH_TIME_SECONDS",
    help="Maximum time to wait in seconds",
)
REPOSITORIES_CLI_OPTIONS["step"] = typer.Option(
    DEFAULT_STEP,
    "--step",
    help="Time to wait between checks in seconds",
)
REPOSITORIES_CLI_OPTIONS["previous"] = typer.Option(
    "",
    "--previous",
    help="Previous workflow ID to compare against",
)
REPOSITORIES_CLI_OPTIONS["workflow_id"] = typer.Option(
    "",
    "--workflow-id",
    help="Workflow ID",
)
REPOSITORIES_CLI_OPTIONS["workflow"] = typer.Option(
    "",
    "--workflow",
    help="Workflow ID or file name.",
)
REPOSITORIES_CLI_OPTIONS["run_id"] = typer.Option(
    "",
    "--run-id",
    help="Workflow run ID",
)
REPOSITORIES_CLI_OPTIONS["body"] = typer.Option(
    None,
    "--body",
    help="""Github API request data. Default: None.
    Format: YAML, JSON, HCL, TOML or string as per GitHub API:
    https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event""",
)
REPOSITORIES_CLI_OPTIONS["ref"] = typer.Option(
    None,
    "--ref",
    help="Github ref - branch or tag. Default: current branch name",
)
REPOSITORIES_CLI_OPTIONS["inputs"] = typer.Option(
    None,
    "--inputs",
    help="""Github workflow dispatch inputs.
    Dictionary of key-value pairs. Format: YAML, JSON, HCL, TOML or string with format k1[=:]v1[,;]k2[=:]v2""",
)

# Load environment variables from .env file if it exists
try:
    # Capture the output of load_dotenv to check if it was successful
    env_path = Path(".env")
    if env_path.exists():
        result = dotenv.load_dotenv(dotenv_path=env_path, override=True)
        if not result:
            typer.echo("Error: Failed to load environment variables from .env file.", err=True)
            typer.echo("Please check the format of your .env file.", err=True)
            typer.echo("Each line should be in the format: KEY=VALUE", err=True)
            typer.echo("Lines starting with # are treated as comments.", err=True)
            sys.exit(1)
except Exception as e:
    typer.echo(f"Error loading .env file: {e}", err=True)
    typer.echo("Please check the format of your .env file.", err=True)
    typer.echo("Each line should be in the format: KEY=VALUE", err=True)
    typer.echo("Lines starting with # are treated as comments.", err=True)
    sys.exit(1)


class B2bRepositoriesWorkflowCommand(B2bRepositoriesCommand):
    """B2B repositories workflow command."""

    def setup_github_handler(self, b2b_environment: B2bEnvironment) -> None:
        """Set up the GitHub handler."""
        if self._github_handler:
            if self._github_handler.b2b_command and self._github_handler.b2b_command != self:
                raise B2bEnvironmentError(
                    "Internal error: b2b_command of github_handler does not match our self.",
                )
            if self._github_handler.b2b_environment and self._github_handler.b2b_environment != b2b_environment:
                raise B2bEnvironmentError(
                    "Internal error: b2b_environment of github_handler does not match given b2b_environment.",
                )
            self._github_handler.b2b_environment = b2b_environment
        else:
            # noinspection PyUnresolvedReferences
            from b2b_cli._commands.b2b_command import B2bCommand  # noqa: TC001
            from b2b_cli.handlers.b2b_github_handler import B2bGithubHandler

            if b2b_environment:
                self.set_b2b_environment(b2b_environment=b2b_environment)
            self._github_handler = B2bGithubHandler(
                cli_io=self.io,
                workspace_handler=self.workspace_handler,
                b2b_environment=b2b_environment,
                b2b_command=typing.cast("B2bCommand", self),
            )

    @property
    def github_handler(self) -> B2bGithubHandler | None:
        """Github handler."""
        handler = getattr(self, "_github_handler", None)
        if handler:
            return handler
        wsh = getattr(self, "_workspace_handler", None)
        wsh_b2b_environment = wsh.b2b_environment if wsh else None
        b2b_environment = self.b2b_environment or wsh_b2b_environment
        self.setup_github_handler(b2b_environment=b2b_environment)
        return getattr(self, "_github_handler", None)


class B2bRepositoriesWorkflowDispatchCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow dispatch command."""

    def __call__(  # noqa: C901, PLR0912
        self,
        *args,  # noqa: ARG002
        name_pattern: str,
        github_repository: str,
        use_regex: bool,
        workflow: str | None = None,
        ref: str | None = None,
        inputs: str | None = None,
        body: str | None = None,
        debug: bool = False,
        verbose: int = 0,
        output: OutputFormatEnum = OutputFormatEnum.STYLED,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """Find workflow by name pattern or regex."""
        try:
            if not workflow:
                try:
                    workflow_id = int(name_pattern)
                    workflow_o = self.github_handler.get_workflow(
                        workflow_id=workflow_id,
                        github_repository=github_repository,
                        debug=debug,
                        verbose=verbose,
                    )
                    if not workflow_o:
                        raise ValueError(f"No workflow found matching '{name_pattern}'")
                    workflows = [workflow_o]
                except Exception:
                    try:
                        workflow_o = self.github_handler.get_workflow(
                            workflow_id=name_pattern,
                            github_repository=github_repository,
                            debug=debug,
                            verbose=verbose,
                        )
                        if not workflow_o:
                            raise ValueError(f"No workflow found matching '{name_pattern}'")
                        workflows = [workflow_o]
                    except Exception as exc:
                        self.io.info(msg=f"Cannot get workflow '{workflow}: {exc!s}", verbosity=1)
                        workflows = self.github_handler.find_workflows_by_name(
                            name_pattern=name_pattern,
                            github_repository=github_repository,
                            use_regex=use_regex,
                            debug=debug,
                            verbose=verbose,
                            raw=True,
                        )

                if not workflows:
                    typer.echo(f"No workflows found matching '{name_pattern}'")
                    return 1

                if len(workflows) > 1:
                    typer.echo(f"{len(workflows)} workflows found matching '{name_pattern}'")
                    return 2

                workflow = workflows[0].id

            self.io.info(msg=f"Workflow: {workflow}", verbosity=1)

            from toolbag.utils.load_file import load_file, load_stream_structured

            body_d = (load_file(body) if "://" in body else load_stream_structured("body", stream=body)) if body else {}
            if body_d:
                self.workspace_handler.print_data_formatted(
                    context={"body": [body_d] if output == OutputFormatEnum.TABLE else body_d},
                    output=output,
                    table_entry="body",
                    debug=debug,
                    verbose=verbose,
                )
            if ref:
                ref_l = self.workspace_handler.split_parameter_list(ref, default="")
                ref_ = ref_l[0] if ref_l else ""
                body_d["ref"] = ref_
            if inputs:
                inputs_d = self.workspace_handler.split_kvp_pairs(inputs)
                body_d["inputs"] = inputs_d
            ref_ = body_d.get("ref", ...)
            inputs_ = body_d.get("inputs", ...)
            if ref_ is ... or inputs_ is ...:
                raise ValueError("'ref' and 'inputs' must be provided!")

            self.io.info(msg=f"Ref: {ref_}", verbosity=1)
            if verbose:
                self.workspace_handler.print_data_formatted(
                    context={"inputs": [inputs_] if output == OutputFormatEnum.TABLE else inputs_},
                    output=output,
                    table_entry="inputs",
                    debug=debug,
                    verbose=verbose,
                )

            return self.github_handler.dispatch_workflow(
                workflow=workflow,
                github_repository=github_repository,
                ref=ref_,
                inputs=inputs_,
                debug=debug,
                verbose=verbose,
            )
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            typer.echo(f"ERROR: {exc!s}", err=True)
            raise typer.Exit(code=1) from exc


class B2bRepositoriesWorkflowFindCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        name_pattern: str,
        github_repository: str,
        use_regex: bool,
        limit: int,
        debug: bool = False,
        verbose: int = 0,
        output: OutputFormatEnum = OutputFormatEnum.STYLED,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """Find workflow by name pattern or regex."""
        try:
            workflows = self.github_handler.find_workflows_by_name(
                name_pattern=name_pattern,
                github_repository=github_repository,
                use_regex=use_regex,
                limit=limit,
                debug=debug,
            )

            if workflows:
                self.github_handler.print_data_formatted(
                    context={"workflows": workflows} if output == OutputFormatEnum.TABLE else workflows,
                    output=output,
                    table_entry="workflows",
                    heading=f"Workflows for repository: {github_repository}",
                    debug=debug,
                    verbose=verbose,
                )

                return 0

            typer.echo(f"No workflows found matching '{name_pattern}'")
            return 1
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            typer.echo(f"ERROR: {exc!s}", err=True)
            raise typer.Exit(code=1) from exc


class B2bRepositoriesWorkflowLastRunIdCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow last run id command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        workflow_id: str,
        github_repository: str,
        environment_name: str,
        branch: str,
        output: OutputFormatEnum = OutputFormatEnum.STYLED,
        debug: bool = False,
        verbose: int = 0,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """Get the latest workflow ID for a specific workflow and environment/branch."""
        try:
            run_id, age = self.github_handler.get_workflow_latest_run_id(
                workflow_id=workflow_id,
                github_repository=github_repository,
                environment_name=environment_name,
                branch=branch,
                debug=debug,
                verbose=verbose,
                age_format="int",
            )

            # Create result data structure
            result = {
                "workflow_id": workflow_id,
                "run_id": run_id,
                "age": age,
                "repository": github_repository,
                "environment": environment_name,
                "branch": branch,
            }

            # Always print workflow ID to stdout for piping
            if output.value == "plain":
                # Print raw ID for pipelines to capture
                typer.echo(f"\n{run_id}")
            else:
                # Format and print the output
                self.github_handler.print_data_formatted(
                    context={"result": [result]} if output == OutputFormatEnum.TABLE else result,
                    output=output,
                    table_entry="result",
                    heading=f"Run ID '{run_id}' in {github_repository}",
                    debug=debug,
                    verbose=verbose,
                )
            return 0
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            typer.echo(f"ERROR: {exc!s}", err=True)
            raise exc


class B2bRepositoriesWorkflowRunListCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow run list command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        workflow_id: str,
        github_repository: str,
        environment_name: str | None = None,
        branch: str | None = None,
        output: OutputFormatEnum = OutputFormatEnum.TABLE,
        debug: bool = False,
        verbose: int = 0,
        **kwargs,  # noqa: ARG002
    ) -> int | None:
        """Get the workflow run list for a specific workflow and environment/branch."""
        try:
            matching_runs = self.github_handler.list_workflow_runs(
                workflow_id=workflow_id,
                github_repository=github_repository,
                environment_name=environment_name,
                branch=branch,
                debug=debug,
                verbose=verbose,
                age_format="github",
            )

            if not matching_runs:
                typer.echo(f"No workflows found matching '{workflow_id}'")
                return 1

            workflow = self.github_handler.get_workflow(
                workflow_id=workflow_id,
                github_repository=github_repository,
                debug=debug,
                verbose=verbose,
            )
            # Always print workflow ID to stdout for piping
            # Format and print the output
            self.github_handler.print_data_formatted(
                context={"runs": matching_runs} if output == OutputFormatEnum.TABLE else matching_runs,
                output=output,
                table_entry="runs",
                heading=f"Run list for workflow '{workflow.name}' in {github_repository}",
                table_headings=["id", "name", "path", "display_title", "head_branch", "event", "status", "age"],
                debug=debug,
                verbose=verbose,
                table_coloring=B2bTableColoringEnum.ROW,
                table_coloring_alternates=3,
            )
            return 0
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            typer.echo(f"ERROR: {exc!s}", err=True)


class B2bRepositoriesWorkflowRunCheckCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow run check command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        workflow_id: str,
        timeout: int,
        step: int,
        debug: bool = False,
        verbose: int = 0,  # noqa: ARG002
        previous: str = "",
        output: OutputFormatEnum = OutputFormatEnum.STYLED,
        environment_name: str | None = None,
        branch: str | None = None,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """Check the status of a workflow action."""
        try:
            # Call the check_phase_action method from the handler
            rc, run_id = self.github_handler.check_workflow_run(
                workflow_id=workflow_id,
                timeout=timeout,
                step=step,
                debug=debug,
                previous=previous,
                environment_name=environment_name,
                branch=branch,
            )

            # For this command, we'll just return the rc code
            # This command produces continuous output, so most formatting doesn't apply
            # We'll just handle the JSON/YAML case for when errors occur
            result = {"result_code": rc, "workflow_id": workflow_id, "run_id": run_id}

            if output not in [OutputFormatEnum.PLAIN, OutputFormatEnum.TEXT]:
                # Only format the error output for non-simple formats
                self.github_handler.print_data_formatted(
                    context={"result": [result]} if output == OutputFormatEnum.TABLE else result,
                    table_entry="result",
                    output=output,
                    debug=debug,
                )
            else:
                # Just output the return code for simple output
                typer.echo(result["result_code"])

            return rc
        except ValueError as e:
            result = {"error": str(e), "workflow_id": workflow_id}

            if output not in [OutputFormatEnum.PLAIN, OutputFormatEnum.TEXT]:
                # Only format the error output for non-simple formats
                self.github_handler.print_data_formatted(
                    context={"result": [result]} if output == OutputFormatEnum.TABLE else result,
                    output=output,
                    debug=debug,
                )

            return 1
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            raise exc


class B2bRepositoriesWorkflowRunGetCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow run get command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        workflow_id: str,
        run_id: str,
        debug: bool = False,
        verbose: int = 0,
        output: OutputFormatEnum = OutputFormatEnum.STYLED,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """Check the status of a workflow action."""
        try:
            github_repository = os.environ.get("GITHUB_REPOSITORY")
            if not github_repository:
                raise ValueError("GITHUB_REPOSITORY was not provided")

            workflow_run = self.github_handler.get_workflow_run(
                workflow_id=workflow_id,
                run_id=run_id,
                github_repository=github_repository,
                debug=debug,
                verbose=verbose,
            )

            if output not in [OutputFormatEnum.PLAIN, OutputFormatEnum.TEXT]:
                wfr_d = dict(workflow_run)
                # Only format the error output for non-simple formats
                self.github_handler.print_data_formatted(
                    context={"result": [wfr_d]} if output == OutputFormatEnum.TABLE else wfr_d,
                    table_entry="result",
                    output=output,
                    debug=debug,
                )
            else:
                # Just output the return code for simple output
                typer.echo(
                    f'{workflow_run["id"]} {workflow_run["event"]} {workflow_run["head_branch"]} "'
                    f'{workflow_run["status"]} {workflow_run["conclusion"]} {workflow_run["updated_at"]}',
                )

            return 0
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            result = {"error": str(exc), "workflow_id": workflow_id, "run_id": run_id}

            if output not in [OutputFormatEnum.PLAIN, OutputFormatEnum.TEXT]:
                # Only format the error output for non-simple formats
                self.github_handler.print_data_formatted(
                    context={"result": [result]} if output == OutputFormatEnum.TABLE else result,
                    output=output,
                    debug=debug,
                )

            return 1


class B2bRepositoriesWorkflowListCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow list command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        github_repository: str,
        limit: int,
        debug: bool = False,
        verbose: int = 0,
        output: OutputFormatEnum = OutputFormatEnum.TABLE,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """List all workflows for a given repository."""
        # Print debug information about environment variables
        if debug:
            typer.echo(f"Environment GITHUB_REPOSITORY: {os.environ.get('GITHUB_REPOSITORY')}")
            typer.echo(f"Argument github_repository: {github_repository}")

        try:
            workflows = self.github_handler.list_all_workflows(
                github_repository=github_repository,
                limit=limit,
                debug=debug,
            )

            if workflows:
                self.github_handler.print_data_formatted(
                    context={"workflows": workflows} if output == OutputFormatEnum.TABLE else workflows,
                    table_entry="workflows",
                    output=output,
                    heading=f"Workflows for repository: {github_repository}",
                    table_coloring=B2bTableColoringEnum.COLUMN,
                    table_coloring_alternates=3,
                    debug=debug,
                    verbose=verbose,
                )
                return 0

            typer.echo("No workflows found")
            return 1
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            typer.echo(f"ERROR: {exc!s}", err=True)
            raise exc


class B2bRepositoriesWorkflowGetCommand(B2bRepositoriesWorkflowCommand):
    """B2B repositories workflow get command."""

    def __call__(
        self,
        *args,  # noqa: ARG002
        workflow_id: str,
        github_repository: str,
        debug: bool = False,
        verbose: int = 0,
        output: OutputFormatEnum = OutputFormatEnum.STYLED,
        **kwargs,  # noqa: ARG002
    ) -> int:
        """List all workflows for a given repository."""
        # Print debug information about environment variables
        if debug:
            typer.echo(f"Environment GITHUB_REPOSITORY: {os.environ.get('GITHUB_REPOSITORY')}")
            typer.echo(f"Argument github_repository: {github_repository}")

        try:
            workflow = self.github_handler.get_workflow(
                github_repository=github_repository,
                workflow_id=workflow_id,
                debug=debug,
                verbose=verbose,
            )

            if workflow:
                self.github_handler.print_data_formatted(
                    context={"workflow": [workflow]} if output == OutputFormatEnum.TABLE else workflow,
                    output=output,
                    heading=f"Workflow '{workflow.name}' for repository: {github_repository}",
                    debug=debug,
                    verbose=verbose,
                )
                return 0

            typer.echo("Workflow not found")
            return 1
        except Exception as exc:
            if debug:
                self.traceback_pattern(exc=exc, debug=debug)
            typer.echo(f"ERROR: {exc!s}", err=True)
            raise exc


app = typer.Typer(
    pretty_exceptions_enable=False,
)


@app.command("dispatch")
def dispatch_workflow(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    name_pattern: str = typer.Argument(None, help="Workflow name pattern to find"),
    workflow: str = REPOSITORIES_CLI_OPTIONS["workflow"],
    github_repository: str = REPOSITORIES_CLI_OPTIONS["github_repository"],
    use_regex: bool = REPOSITORIES_CLI_OPTIONS["use_regex"],
    ref: str = REPOSITORIES_CLI_OPTIONS["ref"],
    inputs: str = REPOSITORIES_CLI_OPTIONS["inputs"],
    body: str = REPOSITORIES_CLI_OPTIONS["body"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_result"],
) -> int:
    """Dispatch workflows by name pattern or regex."""
    try:
        return B2bRepositoriesWorkflowDispatchCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            overwrite_if_exists=overwrite_if_exists,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            workflow=workflow,
            name_pattern=name_pattern,
            github_repository=github_repository,
            use_regex=use_regex,
            ref=ref,
            inputs=inputs,
            body=body,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("find")
def find_workflow(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    name_pattern: str = typer.Argument(None, help="Workflow name pattern to find"),
    github_repository: str = REPOSITORIES_CLI_OPTIONS["github_repository"],
    use_regex: bool = REPOSITORIES_CLI_OPTIONS["use_regex"],
    limit: int = REPOSITORIES_CLI_OPTIONS["limit"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_workflows"],
) -> int:
    """Find workflows by name pattern or regex."""
    try:
        return B2bRepositoriesWorkflowFindCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            overwrite_if_exists=overwrite_if_exists,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            name_pattern=name_pattern,
            github_repository=github_repository,
            use_regex=use_regex,
            limit=limit,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("run-list")
def get_run_list(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    workflow_id: str = typer.Argument(..., help="The ID of the workflow"),
    github_repository: str = REPOSITORIES_CLI_OPTIONS["github_repository"],
    # environment_name: str = REPOSITORIES_CLI_OPTIONS["environment_name"],
    branch: str = REPOSITORIES_CLI_OPTIONS["branch"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_workflows"],
) -> int:
    """Get the latest workflow ID for a specific workflow and environment/branch."""
    try:
        return B2bRepositoriesWorkflowRunListCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            overwrite_if_exists=overwrite_if_exists,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            workflow_id=workflow_id,
            github_repository=github_repository,
            # environment_name=environment_name,
            branch=branch,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("run-last-id")
def get_run_last_id(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    workflow_id: str = typer.Argument(..., help="The ID of the workflow"),
    github_repository: str = REPOSITORIES_CLI_OPTIONS["github_repository"],
    environment_name: str = REPOSITORIES_CLI_OPTIONS["environment_name"],
    branch: str = REPOSITORIES_CLI_OPTIONS["branch"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_result"],
) -> int:
    """Get the latest workflow ID for a specific workflow and environment/branch."""
    try:
        return B2bRepositoriesWorkflowLastRunIdCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            overwrite_if_exists=overwrite_if_exists,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            workflow_id=workflow_id,
            github_repository=github_repository,
            environment_name=environment_name,
            branch=branch,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("run-get")
def get_workflow_run(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    workflow_id: str = REPOSITORIES_CLI_OPTIONS["workflow_id"],
    run_id: str = REPOSITORIES_CLI_OPTIONS["run_id"],
    run_id_: str = typer.Argument(None, help="The ID of the run"),
    timeout: int = REPOSITORIES_CLI_OPTIONS["timeout"],
    step: int = REPOSITORIES_CLI_OPTIONS["step"],
    previous: str = REPOSITORIES_CLI_OPTIONS["previous"],
    environment_name: str = REPOSITORIES_CLI_OPTIONS["environment_name"],
    branch: str = REPOSITORIES_CLI_OPTIONS["branch"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_result"],
) -> int:
    """Check the status of a workflow action."""
    try:
        return B2bRepositoriesWorkflowRunGetCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            workflow_id=workflow_id,
            run_id=run_id_ or run_id,
            timeout=timeout,
            step=step,
            previous=previous,
            environment_name=environment_name,
            branch=branch,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("run-check")
def check_workflow_run(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    workflow_id_: str = typer.Argument(None, help="The ID of the workflow"),
    workflow_id: str = REPOSITORIES_CLI_OPTIONS["workflow_id"],
    timeout: int = REPOSITORIES_CLI_OPTIONS["timeout"],
    step: int = REPOSITORIES_CLI_OPTIONS["step"],
    previous: str = REPOSITORIES_CLI_OPTIONS["previous"],
    environment_name: str = REPOSITORIES_CLI_OPTIONS["environment_name"],
    branch: str = REPOSITORIES_CLI_OPTIONS["branch"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_result"],
) -> int:
    """Check the status of a workflow action."""
    try:
        return B2bRepositoriesWorkflowRunCheckCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            overwrite_if_exists=overwrite_if_exists,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            workflow_id=workflow_id_ or workflow_id,
            timeout=timeout,
            step=step,
            previous=previous,
            environment_name=environment_name,
            branch=branch,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("list")
def list_workflows(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    github_repository: str = REPOSITORIES_CLI_OPTIONS["github_repository"],
    limit: int = REPOSITORIES_CLI_OPTIONS["limit"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_workflows"],
) -> int:
    """List all workflows for a given repository."""
    try:
        return B2bRepositoriesWorkflowListCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            overwrite_if_exists=overwrite_if_exists,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            github_repository=github_repository,
            limit=limit,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


@app.command("get")
def get_workflow(  # noqa: PLR0913
    dry_run: bool = B2B_CLI_OPTIONS["dry_run"],
    force: bool = B2B_CLI_OPTIONS["force"],
    no_input: bool = B2B_CLI_OPTIONS["no_input"],
    # overwrite_if_exists: bool = B2B_CLI_OPTIONS["overwrite_if_exists"],
    ansi: bool = B2B_CLI_OPTIONS["ansi"],
    debug: bool = B2B_CLI_OPTIONS["debug"],
    verbose: int = B2B_CLI_OPTIONS["verbose"],
    log_level: str = B2B_CLI_OPTIONS["log_level"],
    log_config: str = B2B_CLI_OPTIONS["log_config"],
    log_only: bool = B2B_CLI_OPTIONS["log_only"],
    log_mode: int = B2B_CLI_OPTIONS["log_mode"],
    b2b_config_file: str = B2B_CLI_OPTIONS["b2b_config_file"],
    github_repository: str = REPOSITORIES_CLI_OPTIONS["github_repository"],
    workflow_id_: str = typer.Argument(..., help="The ID of the workflow"),
    workflow_id: str = REPOSITORIES_CLI_OPTIONS["workflow_id"],
    output: OutputFormatEnum = REPOSITORIES_CLI_OPTIONS["output_result"],
) -> int:
    """List all workflows for a given repository."""
    try:
        return B2bRepositoriesWorkflowGetCommand(
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
        )(
            dry_run=dry_run,
            force=force,
            no_input=no_input,
            ansi=ansi,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_config=log_config,
            log_only=log_only,
            log_mode=log_mode,
            b2b_config_file=b2b_config_file,
            github_repository=github_repository,
            workflow_id=workflow_id_ or workflow_id,
            output=output,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e!s}", err=True)
        raise e


if __name__ == "__main__":
    app()
