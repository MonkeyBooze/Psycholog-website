from django.http import HttpResponsePermanentRedirect

class DomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        
        # Split host from port if present
        if ':' in host:
            hostname = host.split(':')[0]
        else:
            hostname = host

        # Target domain
        target_domain = 'spektrumumyslu.pl'
        
        # Domains to redirect (www, old domain, old domain www)
        redirect_sources = [
            'www.spektrumumyslu.pl',
            'psychoedukacjaopole.pl',
            'www.psychoedukacjaopole.pl'
        ]

        if hostname in redirect_sources:
            new_url = f"https://{target_domain}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(new_url)

        return self.get_response(request)
