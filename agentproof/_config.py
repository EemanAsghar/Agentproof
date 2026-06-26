"""Runtime configuration helper.

When running as a UiPath coded agent, secrets are read from Orchestrator Assets.
When running locally or on Vercel (no UiPath runtime), it falls back to env vars.
"""

import os


def asset_or_env(name: str, folder_path: str = "Shared") -> str:
    """Return a secret from a UiPath Asset if available, else from the environment."""
    try:
        from uipath.platform import UiPath

        sdk = UiPath()
        try:
            v = sdk.assets.retrieve_secret(name, folder_path=folder_path)
            if v:
                return v
        except Exception:
            pass
        try:
            a = sdk.assets.retrieve(name, folder_path=folder_path)
            v = (getattr(a, "value", None) or getattr(a, "string_value", None)
                 or getattr(a, "StringValue", None))
            if v:
                return v
        except Exception:
            pass
    except Exception:
        pass
    return os.environ[name]
