"""
calculator_config.py

Centralised runtime configuration for Enhanced Calculator.
Loads values from the OS environment  and exposes
a single immutable Config instance for the rest of the application.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1.  Load environment variables (if a .env file exists in project root)      
# ---------------------------------------------------------------------------
_PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env", override=False)

# --------------------------------------------------------------------------- #
# 2.  Helpers                                                                 #
# --------------------------------------------------------------------------- #
_TRUE = {"1", "true", "yes", "y", "on"}
_FALSE = {"0", "false", "no", "n", "off"}


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    raw_low = raw.lower()
    if raw_low in _TRUE:
        return True
    if raw_low in _FALSE:
        return False
    raise ValueError(f"Environment variable {key} must be boolean-like, got {raw!r}")


def _env_int(key: str, default: int, *, positive: bool = True) -> int:
    raw = os.getenv(key)
    try:
        value = int(raw) if raw is not None else default
    except ValueError as exc:
        raise ValueError(f"{key} must be an integer, got {raw!r}") from exc
    if positive and value <= 0:
        raise ValueError(f"{key} must be > 0, got {value}")
    return value


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


# --------------------------------------------------------------------------- #
# 3.  Configuration dataclass                                                 #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Config:
    # -- Primary directories
    base_dir: Path = field(init=False)
    log_dir: Path = field(init=False)
    history_dir: Path = field(init=False)

    # -- Behaviour toggles
    auto_save: bool
    max_history_size: int
    precision: int
    max_input_value: Decimal

    # -- Derived file paths
    log_file: Path = field(init=False)
    history_file: Path = field(init=False)

    # -- Misc
    default_encoding: str

    # ---- Constructor boilerplate is replaced with factory ----------------- #
    @classmethod
    def load(cls) -> "Config":
        """Read environment variables, apply defaults, validate & materialise."""
        base_dir = Path(os.getenv("CALCULATOR_BASE_DIR", _PROJECT_ROOT)).resolve()

        log_dir = _ensure_dir(
            Path(os.getenv("CALCULATOR_LOG_DIR", base_dir / "logs"))
        )
        history_dir = _ensure_dir(
            Path(os.getenv("CALCULATOR_HISTORY_DIR", base_dir / "history"))
        )

        cfg = cls(
            auto_save=_env_bool("CALCULATOR_AUTO_SAVE", True),
            max_history_size=_env_int("CALCULATOR_MAX_HISTORY_SIZE", 1_000),
            precision=_env_int("CALCULATOR_PRECISION", 4),
            max_input_value=Decimal(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e100")),
            default_encoding=os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8"),
        )

        # Because the dataclass is frozen, we use object.__setattr__
        object.__setattr__(cfg, "base_dir", base_dir)
        object.__setattr__(cfg, "log_dir", log_dir)
        object.__setattr__(cfg, "history_dir", history_dir)
        object.__setattr__(
            cfg,
            "log_file",
            Path(os.getenv("CALCULATOR_LOG_FILE", log_dir / "calculator.log")).resolve(),
        )
        object.__setattr__(
            cfg,
            "history_file",
            Path(
                os.getenv("CALCULATOR_HISTORY_FILE", history_dir / "calculator_history.csv")
            ).resolve(),
        )

        cfg._validate()  # type: ignore[attr-defined]
        return cfg

    # --------------------------------------------------------------------- #
    # 4.  Validation                                                        #
    # --------------------------------------------------------------------- #
    def _validate(self) -> None:
        if self.max_history_size <= 0:
            raise ValueError("max_history_size must be positive")  # pragma: no cover
        if self.precision <= 0:
            raise ValueError("precision must be positive")  # pragma: no cover
        if self.max_input_value <= 0:
            raise ValueError("max_input_value must be positive")  # pragma: no cover
        if not (self.log_dir.is_dir() and self.history_dir.is_dir()):
            raise ValueError("log_dir and history_dir must be directories")  # pragma: no cover

    # --------------------------------------------------------------------- #
    # 5.  Convenience: pretty str                                           #
    # --------------------------------------------------------------------- #
    def __str__(self) -> str:
        """Human-readable dump of key settings (helpful for debugging)."""
        parts = [
            "Calculator Config:",
            f"  auto_save          = {self.auto_save}",
            f"  max_history_size   = {self.max_history_size}",
            f"  precision          = {self.precision}",
            f"  max_input_value    = {self.max_input_value}",
            f"  log_file           = {self.log_file}",
            f"  history_file       = {self.history_file}",
        ]
        return "\n".join(parts)


# --------------------------------------------------------------------------- #
# 6.  Module-level singleton                                                  #
# --------------------------------------------------------------------------- #
CONFIG: Config = Config.load()
