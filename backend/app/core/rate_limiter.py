"""
🚦 Sistema de Rate Limiting y Throttling

Implementación TDD - FASE GREEN
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from enum import Enum


class UserTier(Enum):
    """Niveles de usuarios para diferentes limites"""
    REGULAR = "regular"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class ThrottleConfig:
    """Configuración de throttling"""
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size_seconds: int = 60


@dataclass
class LimitInfo:
    """Información sobre límites actuales del usuario"""
    requests_remaining: int
    reset_time: datetime
    current_usage: int
    max_allowed: int


class RateLimiter:
    """
    Sistema de rate limiting con ventanas deslizantes

    Funcionalidades:
    - Rate limiting por usuario
    - Diferentes límites por tipo de usuario
    - Ventanas deslizantes para precision
    - Burst protection
    """

    def __init__(self, default_config: Optional[ThrottleConfig] = None):
        self.default_config = default_config or ThrottleConfig()

        # Almacenamiento de requests por usuario
        self.user_requests: Dict[str, deque] = defaultdict(deque)
        self.user_tiers: Dict[str, UserTier] = {}
        self.user_configs: Dict[str, ThrottleConfig] = {}

        # Configuraciones por tier
        self.tier_configs = {
            UserTier.REGULAR: ThrottleConfig(
                max_requests_per_minute=30,
                max_requests_per_hour=500,
                burst_limit=5
            ),
            UserTier.PREMIUM: ThrottleConfig(
                max_requests_per_minute=100,
                max_requests_per_hour=2000,
                burst_limit=20
            ),
            UserTier.ENTERPRISE: ThrottleConfig(
                max_requests_per_minute=500,
                max_requests_per_hour=10000,
                burst_limit=100
            )
        }

    def set_user_tier(self, user_id: str, tier: str):
        """Establecer tier del usuario"""
        if isinstance(tier, str):
            tier = UserTier(tier)
        self.user_tiers[user_id] = tier
        self.user_configs[user_id] = self.tier_configs[tier]

    def get_user_limit(self, user_id: str) -> ThrottleConfig:
        """Obtener configuración de límites para usuario"""
        return self.user_configs.get(user_id, self.default_config)

    def _clean_old_requests(self, user_id: str, window_seconds: int = 60):
        """Limpiar requests antiguos fuera de la ventana"""
        now = time.time()
        cutoff = now - window_seconds

        user_queue = self.user_requests[user_id]
        while user_queue and user_queue[0] < cutoff:
            user_queue.popleft()

    def is_allowed(self, user_id: str) -> bool:
        """
        Verificar si el usuario puede hacer un request

        Args:
            user_id: ID del usuario

        Returns:
            True si está permitido, False si excede límites
        """
        config = self.get_user_limit(user_id)
        now = time.time()

        # Limpiar requests antiguos
        self._clean_old_requests(user_id, 60)  # Ventana de 1 minuto

        user_queue = self.user_requests[user_id]
        current_requests = len(user_queue)

        # Verificar límite por minuto
        if current_requests >= config.max_requests_per_minute:
            return False

        # Verificar burst limit (requests en últimos 10 segundos)
        burst_cutoff = now - 10
        burst_requests = sum(1 for req_time in user_queue if req_time > burst_cutoff)
        if burst_requests >= config.burst_limit:
            return False

        return True

    def check_and_increment(self, user_id: str):
        """
        Verificar límites e incrementar contador

        Args:
            user_id: ID del usuario

        Raises:
            RateLimitError: Si se exceden los límites
        """
        if not self.is_allowed(user_id):
            limit_info = self.get_limit_info(user_id)

            from app.core.error_handler import RateLimitError
            raise RateLimitError(
                message=f"Rate limit exceeded for user {user_id}",
                retry_after_seconds=60,
                limit_type="per_minute",
                current_usage=limit_info.current_usage
            )

        # Incrementar contador
        now = time.time()
        self.user_requests[user_id].append(now)

    def get_limit_info(self, user_id: str) -> LimitInfo:
        """
        Obtener información detallada de límites para usuario

        Args:
            user_id: ID del usuario

        Returns:
            Información sobre límites actuales
        """
        config = self.get_user_limit(user_id)
        self._clean_old_requests(user_id, 60)

        current_requests = len(self.user_requests[user_id])
        remaining = max(0, config.max_requests_per_minute - current_requests)

        # Calcular próximo reset (inicio del próximo minuto)
        now = datetime.now()
        next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

        return LimitInfo(
            requests_remaining=remaining,
            reset_time=next_minute,
            current_usage=current_requests,
            max_allowed=config.max_requests_per_minute
        )

    def reset_user_limits(self, user_id: str):
        """Resetear límites para usuario específico"""
        if user_id in self.user_requests:
            self.user_requests[user_id].clear()

    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obtener estadísticas de uso por usuario"""
        stats = {}

        for user_id in self.user_requests:
            self._clean_old_requests(user_id, 60)
            config = self.get_user_limit(user_id)
            current_usage = len(self.user_requests[user_id])

            stats[user_id] = {
                "current_usage": current_usage,
                "max_allowed": config.max_requests_per_minute,
                "usage_percentage": (current_usage / config.max_requests_per_minute) * 100,
                "tier": self.user_tiers.get(user_id, "default").value if user_id in self.user_tiers else "default"
            }

        return stats
