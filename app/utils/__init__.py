"""
Common utility functions and helpers.

This module provides:
- Response wrappers (success/error responses)
- Pagination helpers
- Datetime utilities
- Validation helpers
- Caching decorators
- String utilities
"""

from app.utils.response import (
    APIResponse,
    ErrorResponse,
    PaginatedResponse,
    success_response,
    error_response,
    paginate,
    not_found,
    unauthorized,
    forbidden,
    bad_request,
    internal_error,
)
from app.utils.datetime_utils import (
    utc_now,
    utc_now_timestamp,
    format_datetime,
    parse_datetime,
    get_date_range,
    is_expired,
    add_time,
    time_ago,
    to_unix_timestamp,
    from_unix_timestamp,
)
from app.utils.validators import (
    validate_email,
    validate_password_strength,
    validate_phone_number,
    validate_url,
    validate_username,
    validate_json_string,
    validate_date_range,
)
from app.utils.string_utils import (
    slugify,
    truncate,
    mask_email,
    mask_phone,
    generate_random_string,
    generate_token,
    camel_to_snake,
    snake_to_camel,
    clean_whitespace,
    strip_html,
    extract_numbers,
    capitalize_words,
    remove_special_chars,
)
from app.utils.cache import (
    cache_result,
    clear_cache,
    get_cache_stats,
    redis_cache_result,
)

__all__ = [
    # Response
    "APIResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "success_response",
    "error_response",
    "paginate",
    "not_found",
    "unauthorized",
    "forbidden",
    "bad_request",
    "internal_error",
    # Datetime
    "utc_now",
    "utc_now_timestamp",
    "format_datetime",
    "parse_datetime",
    "get_date_range",
    "is_expired",
    "add_time",
    "time_ago",
    "to_unix_timestamp",
    "from_unix_timestamp",
    # Validators
    "validate_email",
    "validate_password_strength",
    "validate_phone_number",
    "validate_url",
    "validate_username",
    "validate_json_string",
    "validate_date_range",
    # String
    "slugify",
    "truncate",
    "mask_email",
    "mask_phone",
    "generate_random_string",
    "generate_token",
    "camel_to_snake",
    "snake_to_camel",
    "clean_whitespace",
    "strip_html",
    "extract_numbers",
    "capitalize_words",
    "remove_special_chars",
    # Cache
    "cache_result",
    "clear_cache",
    "get_cache_stats",
    "redis_cache_result",
]
