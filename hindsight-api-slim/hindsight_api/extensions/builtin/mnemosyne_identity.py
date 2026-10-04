"""Project V // Mnemosyne HTTP identity extension.

Compatibility-first: this module adds Phoenix/Mnemosyne identity endpoints without
changing Hindsight's existing /version response or retain/recall/reflect routes.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter

from hindsight_api import __version__ as hindsight_api_version
from hindsight_api.extensions import HttpExtension

if TYPE_CHECKING:
    from hindsight_api import MemoryEngine


MNEMOSYNE_VERSION = "0.1b"
MNEMOSYNE_PRODUCT = "Project V // Mnemosyne"
MNEMOSYNE_ROLE = "Phoenix Memory Core"


class MnemosyneIdentityExtension(HttpExtension):
    """Expose additive machine-readable identity for Phoenix integration."""

    def _payload(self) -> dict[str, Any]:
        return {
            "product": MNEMOSYNE_PRODUCT,
            "role": MNEMOSYNE_ROLE,
            "mnemosyne_version": MNEMOSYNE_VERSION,
            "compatibility": {
                "hindsight_api_version": hindsight_api_version,
                "retain": True,
                "recall": True,
                "reflect": True,
                "phoenix_contract": "0.1",
            },
            "runtime": {
                "mode": self.config.get("mode", os.getenv("PROJECT_V_MNEMOSYNE_MODE", "development")),
                "production_cutover_authorized": False,
            },
            "safety": {
                "memory_is_context_not_authority": True,
                "remembered_approval_is_not_current_approval": True,
            },
        }

    def get_router(self, memory: "MemoryEngine") -> APIRouter:
        router = APIRouter(tags=["Project V // Mnemosyne"])

        @router.get("/mnemosyne/status")
        async def mnemosyne_status() -> dict[str, Any]:
            return self._payload()

        return router

    def get_root_router(self, memory: "MemoryEngine") -> APIRouter | None:
        router = APIRouter(tags=["Project V // Mnemosyne"])

        @router.get("/.well-known/project-v-mnemosyne")
        async def mnemosyne_identity() -> dict[str, Any]:
            return self._payload()

        return router
