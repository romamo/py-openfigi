from __future__ import annotations

import agentyper

from .commands.lookup import lookup

app = agentyper.Agentyper(name="openfigi", help="OpenFIGI CLI Tool")
app.command(help=lookup.__doc__)(lookup)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
