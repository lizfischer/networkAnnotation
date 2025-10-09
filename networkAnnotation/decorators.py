from functools import wraps
from django.shortcuts import redirect


def htmx_only(view_func):
    """Disallow direct access to a URL, only HTMX access. Redirect user to "parent" path"""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.headers.get("HX-Request"):
            # Attempt to redirect to the parent path
            path_parts = request.path.rstrip("/").split("/")
            if len(path_parts) > 1:
                parent_path = "/".join(path_parts[:-1]) + "/"
            else:
                parent_path = "/"
            return redirect(parent_path)
        return view_func(request, *args, **kwargs)

    return _wrapped
