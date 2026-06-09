"""Backward-compatible entrypoint for the Power BI table exporter."""

from __future__ import annotations

try:
    from .export_powerbi_tables import main
except ImportError:
    from export_powerbi_tables import main


if __name__ == "__main__":
    main()
