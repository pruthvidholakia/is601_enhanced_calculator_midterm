import pytest
from decimal import Decimal
import os
import importlib



def _reload_config(env: dict[str, str]):
    """
    Helper: patch env, reload module, return CONFIG instance.
    """
    # 1 – clear previous import
    if "app.calculator_config" in list(importlib.sys.modules):
        del importlib.sys.modules["app.calculator_config"]

    # 2 – patch env
    original = os.environ.copy()
    os.environ.update(env)
    try:
        from app.calculator_config import CONFIG  # re-import
        return CONFIG
    finally:
        # restore environment
        os.environ.clear()
        os.environ.update(original)

def test_defaults(tmp_path, monkeypatch):
    # override BASE_DIR to a tmp folder so we don’t touch real FS
    cfg = _reload_config({"CALCULATOR_BASE_DIR": str(tmp_path)})
    assert cfg.auto_save is True
    assert cfg.max_history_size == 1_000
    assert cfg.precision == 4
    assert cfg.log_dir.exists()
    assert cfg.history_dir.exists()

def test_env_overrides(tmp_path):
    env = {
        "CALCULATOR_BASE_DIR": str(tmp_path),
        "CALCULATOR_AUTO_SAVE": "false",
        "CALCULATOR_PRECISION": "7",
        "CALCULATOR_MAX_HISTORY_SIZE": "42",
        "CALCULATOR_LOG_DIR": str(tmp_path / "custom_logs"),
    }
    cfg = _reload_config(env)
    assert cfg.auto_save is False
    assert cfg.precision == 7
    assert cfg.max_history_size == 42
    assert cfg.log_dir.name == "custom_logs"

def test_validation_errors(tmp_path):
    env = {
        "CALCULATOR_BASE_DIR": str(tmp_path),
        "CALCULATOR_MAX_HISTORY_SIZE": "0",  # invalid (≤0)
    }
    import pytest
    with pytest.raises(ValueError):
        _reload_config(env)

def _fresh_config(env: dict[str, str]):
    """
    Reload app.calculator_config with patched env and return CONFIG.
    """
    # wipe old module
    if "app.calculator_config" in importlib.sys.modules:
        del importlib.sys.modules["app.calculator_config"]

    # patch env
    original = os.environ.copy()
    os.environ.update(env)
    try:
        from app.calculator_config import CONFIG  # re-import fresh
        return CONFIG
    finally:
        os.environ.clear()
        os.environ.update(original)


# _env_bool branches 
def test_env_bool_true_branch(tmp_path):
    cfg = _fresh_config({
        "CALCULATOR_BASE_DIR": str(tmp_path),
        "CALCULATOR_AUTO_SAVE": "True",   # triggers _TRUE branch
    })
    assert cfg.auto_save is True


def test_env_bool_false_branch(tmp_path):
    cfg = _fresh_config({
        "CALCULATOR_BASE_DIR": str(tmp_path),
        "CALCULATOR_AUTO_SAVE": "false",  # triggers _FALSE branch
    })
    assert cfg.auto_save is False


def test_env_bool_invalid(tmp_path):
    with pytest.raises(ValueError):
        _fresh_config({
            "CALCULATOR_BASE_DIR": str(tmp_path),
            "CALCULATOR_AUTO_SAVE": "maybe",   # invalid boolean
        })


# _env_int branches 
def test_env_int_invalid(tmp_path):
    with pytest.raises(ValueError):
        _fresh_config({
            "CALCULATOR_BASE_DIR": str(tmp_path),
            "CALCULATOR_MAX_HISTORY_SIZE": "abc",   # non-integer
        })


def test_validation_precision_zero(tmp_path):
    with pytest.raises(ValueError):
        _fresh_config({
            "CALCULATOR_BASE_DIR": str(tmp_path),
            "CALCULATOR_PRECISION": "0",    # ≤0 triggers validation error
        })


# __str__ convenience 
def test_config_str(tmp_path):
    cfg = _fresh_config({"CALCULATOR_BASE_DIR": str(tmp_path)})
    s = str(cfg)
    # Quick sanity — don’t assert full string, just key markers
    assert "Calculator Config:" in s and "auto_save" in s
    
def test_str_method_executes_all_lines(tmp_path):
    """
    Call str(CONFIG) after a reload to ensure every line in __str__ runs.
    """
    os.environ["CALCULATOR_BASE_DIR"] = str(tmp_path)

    # Reload the module so CONFIG picks up the tmp_path base_dir
    mod = importlib.import_module("app.calculator_config")
    importlib.reload(mod)

    text = str(mod.CONFIG)

    # Simple sanity check
    assert "Calculator Config:" in text
    assert "log_file" in text and "history_file" in text