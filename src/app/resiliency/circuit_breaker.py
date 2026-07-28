import pybreaker
import requests

# Without a timeout a hung upstream blocks indefinitely and never registers as a
# failure, so the breaker would stay closed through an outage.
request_timeout_seconds = 5


def _is_client_error(exc: BaseException) -> bool:
    """Return whether ``exc`` is a 4xx response.

    A client error means our request was wrong, not that the upstream is
    unhealthy, so it should neither be retried nor count toward tripping the
    breaker.
    """
    return (
        isinstance(exc, requests.HTTPError)
        and exc.response is not None
        and 400 <= exc.response.status_code < 500
    )


def _is_retryable(exc: BaseException) -> bool:
    """Return whether ``exc`` is worth another attempt.

    ``CircuitBreakerError`` is excluded so that an open circuit fails fast
    instead of sleeping through the remaining attempts.
    """
    if isinstance(exc, pybreaker.CircuitBreakerError):
        return False
    return not _is_client_error(exc)


# Module-level so breaker state is shared across all callers; an instance created
# per call would reset its failure count every time and never open.
app_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    exclude=[_is_client_error],
    name="locations",
)