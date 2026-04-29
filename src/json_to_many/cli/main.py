import sys

try:
    import click
except ImportError:

    def cli() -> None:
        print(
            "The json2many CLI requires click. Install with: pip install 'json_to_many[cli]'",
            file=sys.stderr,
        )
        sys.exit(1)

else:
    from .commands.convert import convert_cmd
    from .commands.schema import schema_cmd

    @click.group()
    def cli() -> None:
        """json2many — convert JSON to markdown, XML, CSV and more."""

    cli.add_command(convert_cmd, name="convert")
    cli.add_command(schema_cmd, name="schema")
