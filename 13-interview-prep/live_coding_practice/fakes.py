"""Small fake systems used by the live-coding practice problems (no network needed)."""


class FakeCRM:
    """A tiny in-memory CRM. Records are dicts with a 'domain'."""

    def __init__(self):
        self.records = []

    def create(self, properties):
        self.records.append(dict(properties))

    def find_by_domain(self, domain):
        for r in self.records:
            if r.get("domain") == domain:
                return r
        return None

    def update(self, record, properties):
        record.update({k: v for k, v in properties.items() if v not in (None, "")})

    def count(self):
        return len(self.records)


class FakePagedAPI:
    """Returns contacts 100 at a time with a cursor, like a real CRM API."""

    def __init__(self, total=2300, page_size=100):
        self.items = [{"id": i, "email": f"contact{i}@example.com"} for i in range(total)]
        self.page_size = page_size
        self.calls = 0

    def list_contacts(self, after=None):
        self.calls += 1
        start = int(after or 0)
        page = self.items[start:start + self.page_size]
        body = {"results": page}
        if start + self.page_size < len(self.items):
            body["paging"] = {"next": {"after": str(start + self.page_size)}}
        return body


class RateLimited(Exception):
    """Raised by FakeFlakyAPI when you're 'rate limited' (like HTTP 429)."""

    def __init__(self, retry_after=0.01):
        super().__init__("429 Too Many Requests")
        self.retry_after = retry_after


class BadRequest(Exception):
    """A permanent error (like HTTP 400). Must NOT be retried."""


class FakeFlakyAPI:
    """Fails with RateLimited a set number of times, then succeeds."""

    def __init__(self, failures_before_success=2, permanent=False):
        self.remaining = failures_before_success
        self.permanent = permanent
        self.calls = 0

    def enrich(self, domain):
        self.calls += 1
        if self.permanent:
            raise BadRequest("domain is invalid")
        if self.remaining > 0:
            self.remaining -= 1
            raise RateLimited()
        return {"domain": domain, "employees": 120}
