from __future__ import annotations

import logging
import sys

from pydantic_market_data.cli_models import GlobalArgs, PatchedCliSettingsSource
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from .commands.lookup import LookupCommand


def setup_logging(v: bool, vv: bool) -> None:
    if vv:
        level = logging.DEBUG
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    elif v:
        level = logging.INFO
        fmt = "%(name)s: %(message)s"
    else:
        level = logging.WARNING
        fmt = "%(message)s"

    logging.basicConfig(
        level=level, format=fmt, datefmt="%Y-%m-%d %H:%M:%S", stream=sys.stderr, force=True
    )
    if not vv:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)


class AppCLI(BaseSettings, GlobalArgs):
    """OpenFIGI CLI Tool"""

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_kebab_case=True,
        cli_implicit_flags="toggle",
        cli_hide_none_type=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            PatchedCliSettingsSource(settings_cls),
        )

    lookup: CliSubCommand[LookupCommand]

    def cli_cmd(self) -> None:
        sub_v = getattr(self.lookup, "v", False) if self.lookup else False
        sub_vv = getattr(self.lookup, "vv", False) if self.lookup else False
        setup_logging(self.v or sub_v, self.vv or sub_vv)
        CliApp.run_subcommand(self)


def main() -> None:
    CliApp.run(AppCLI)


if __name__ == "__main__":
    main()
