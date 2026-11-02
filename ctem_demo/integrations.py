"""Inventory-sync integration settings.

The demo never calls an external service; this module only reports whether the
integration is configured.
"""

# ---------------------------------------------------------------------------
# CTEM-SECRET-01 | CWE-798 | Hard-coded credential in source code
# TRAINING EXAMPLE: FAKE, NON-FUNCTIONAL value created only for secret-scanning
# demonstrations. It does not correspond to any real system or account.
# Remediation: load from the environment / a secrets manager, and rotate any
# credential that was ever committed (it remains in Git history).
# ---------------------------------------------------------------------------
INVENTORY_API_KEY = "ctemdemo_FAKE_625b8280c58c6ce40af16e9ddd5b2c2c"


def get_inventory_api_key() -> str | None:
    return INVENTORY_API_KEY


def integration_status() -> dict:
    key = get_inventory_api_key()
    return {
        "configured": bool(key),
        "key_hint": f"****{key[-4:]}" if key else None,
    }
