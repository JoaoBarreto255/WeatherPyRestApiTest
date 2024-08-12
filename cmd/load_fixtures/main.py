"""script for startup app database"""

import asyncio
from datetime import datetime

import click

import sys
from pathlib import Path

print(Path(__file__).parent.parent.parent.absolute())
# type: ignore
sys.path.append(str(Path(Path(__file__).parent, "..", "..").absolute()))

from internal.database.repositories import base_startup


@click.command("load-fixtures")
def main() -> None:
    """database populate city info repo startup"""

    click.echo(f'{click.style("Running", fg="green")} load-fixtures', nl=False)
    date = click.style(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fg="yellow"
    )
    click.echo(f' {click.style("at", fg="green")} "{date}" ...')
    asyncio.run(base_startup())
    click.echo(click.style("\nDone!", fg="green"))


if __name__ == "__main__":
    main()
