"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Behaviortaskmaster."""


if __name__ == "__main__":
    main(prog_name="BehaviorTaskMaster")  # pragma: no cover
