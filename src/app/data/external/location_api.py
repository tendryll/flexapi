"""HTTP client for the upstream locations service.

Calls are wrapped in a retry nested inside a circuit breaker: the retry absorbs
transient blips, the breaker stops hammering an upstream that is genuinely down.
See ``get_locations`` for how the two layers compose.
"""
from app.resiliency.circuit_breaker import app_circuit_breaker, _is_retryable, request_timeout_seconds

import os

import pybreaker
import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from ...model.models import LocationResponse

locations_url = os.environ["LOCATIONS_URL"]

@retry(stop=stop_after_attempt(5),
       wait=wait_exponential(multiplier=1, min=2, max=30),
       retry=retry_if_exception(_is_retryable))
@app_circuit_breaker
def get_locations() -> list[LocationResponse]:
    """Fetch every location from the upstream locations service.

    Decorators apply bottom-up, so the breaker sits *inside* the retry and sees
    each individual attempt: five consecutive failures trip it, after which
    calls raise ``CircuitBreakerError`` immediately for ``reset_timeout``
    seconds before a single trial call is allowed through. Wrapping the other
    way round would count a whole exhausted retry cycle as one failure and take
    25 upstream calls to trip.

    Because ``fail_max`` equals the retry's attempt limit, the two thresholds
    coincide: the fifth failure trips the breaker rather than tenacity raising
    ``RetryError``. Callers therefore see ``CircuitBreakerError`` for a sustained
    outage and ``requests.HTTPError`` for a 4xx.
    """
    response = requests.get(locations_url, timeout=request_timeout_seconds)
    # Without this a 5xx is not an exception, so neither the retry nor the
    # breaker would notice the upstream failing.
    response.raise_for_status()

    locations = []

    for result in response.json():
        location = LocationResponse.model_validate(result)
        locations.append(location)

    return locations
