from __future__ import annotations

from importlib.metadata import version

from treaty import App

from .commands.lookup import lookup

app = App("openfigi", version=version("py-openfigi2"), description="OpenFIGI CLI Tool")
app.command(
    "lookup",
    description="Look up a security via OpenFIGI",
    danger_level="safe",
    exit_codes=["NOT_FOUND", "AUTH_REQUIRED", "RATE_LIMITED", "UNAVAILABLE"],
    examples=[
        ("Look up Apple by ISIN", "openfigi lookup --isin US0378331005"),
        ("Find a ticker on one exchange", "openfigi lookup --symbol AIR --exchange FP"),
    ],
    has_network_io=True,
    external=True,
    default_limit=1,
    ordered=True,
)(lookup)


def main() -> None:
    app.main()


if __name__ == "__main__":
    main()
