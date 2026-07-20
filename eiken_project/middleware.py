"""Project-level HTTP middleware."""

from django.http import HttpResponsePermanentRedirect


class CanonicalHostRedirectMiddleware:
    """Redirect legacy Fly hostname to the custom domain (301).

    Keeps /healthz/ on the Fly hostname so platform health checks stay local.
    """

    CANONICAL_HOST = 'eiken-practice.com'
    LEGACY_HOSTS = frozenset({'eiken-app.fly.dev'})
    EXEMPT_PATH_PREFIXES = ('/healthz',)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use META (not get_host) so legacy hosts can redirect before ALLOWED_HOSTS rejects them.
        host = request.META.get('HTTP_HOST', '').split(':')[0].lower()
        if host in self.LEGACY_HOSTS and not self._is_exempt(request.path):
            target = f'https://{self.CANONICAL_HOST}{request.get_full_path()}'
            return HttpResponsePermanentRedirect(target)
        return self.get_response(request)

    def _is_exempt(self, path: str) -> bool:
        return any(path == prefix or path.startswith(prefix + '/') for prefix in self.EXEMPT_PATH_PREFIXES)
