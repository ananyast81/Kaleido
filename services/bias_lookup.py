from urllib.parse import urlsplit

# Represent the articles related to same topic as the one user is currently seeing
source_bias = {
    "reuters.com": "center",
    "foxnews.com": "right",
    "theguardian.com": "left"
}

def get_outlet_bias(url: str) -> str | None:
    # Extract host name from url
    hostname = urlsplit(url).hostname
    if hostname is None:
        return None
    hostname = hostname.removeprefix("www.")
    # domain_bias[o.hostname] - gives error if host is not in the dict, instead use .get() - return None
    return source_bias.get(hostname)