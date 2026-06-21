"""ARQ worker for forecast model training — wired with backend Redis."""
from ccam_backend.config import settings
from ccam_backend.redis_client import _redis_settings_from_url
from ccam_forecast.worker import train_forecast_models as _train

# Re-export for registration
train_forecast_models = _train


class WorkerSettings:
    functions = [train_forecast_models]
    redis_settings = _redis_settings_from_url(settings.redis_url)
    max_tries = 3
    job_retry_after = 300
    keep_result = 86400 * 7
    keep_result_failed = 86400 * 3
