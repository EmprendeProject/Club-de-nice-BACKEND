def supabase_error(exc: Exception) -> str:
    """Extract the human-readable message from supabase-py / gotrue-py exceptions.

    supabase-py wraps errors in AuthApiError / PostgrestAPIError which store
    the real message in .message rather than in __str__.
    """
    return getattr(exc, "message", None) or str(exc)
