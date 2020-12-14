import random
from urllib.request import getproxies

import requests
from requests.adapters import HTTPAdapter
from requests_html import HTMLSession, HTMLResponse
from urllib3 import Retry

from utils.logger import setup_logger

logger = setup_logger()


class RequestHandler:
    """
    RequestHandler
    # https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    """

    def __init__(self, cfg):
        """
        Instantiates a new request handler object.
        """
        self.status_forcelist = cfg.request.status_forcelist
        self.timeout = cfg.request.timeout
        self.total = cfg.request.total
        self.backoff_factor = cfg.request.backoff_factor
        self.delay = cfg.request.delay
        self.cfg = cfg

    @property
    def proxy_strategy(self):
        # proxy in config file
        if self.cfg.proxy.enable:

            if self.cfg.proxy.type in self.cfg.proxy.support:
                proxy = "{}://{}".format(self.cfg.proxy.type,
                                         self.cfg.proxy.host)
                return {"http": proxy, "https": proxy}
        # logger.debug('using system proxy')
        return getproxies()

    @property
    def retry_strategy(self) -> Retry:
        """
        Using Transport Adapters we can set a default timeout for all HTTP calls
        Add a retry strategy to your HTTP client is straightforward.
        We create a HTTPAdapter and pass our strategy to the adapter.
        """
        return Retry(
            total=self.total,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor,
        )

    @property
    def session(self) -> HTMLSession:
        """
        Often when using a third party API you want to verify that the returned response is indeed valid.
        Requests offers the shorthand helper raise_for_status()
        which asserts that the response HTTP status code is not a 4xx or a 5xx,
        """
        session = HTMLSession()
        adapter = HTTPAdapter(max_retries=self.retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        assert_status_hook = (
            lambda response, *args, **kwargs: response.raise_for_status()
        )
        # the requests library offers a 'hooks' interface
        # where you can attach callbacks on certain parts of the request process.
        session.hooks["response"] = [assert_status_hook]
        return session

    @property
    def rebuild_proxies(self) -> dict:
        # noinspection PyBroadException
        try:
            free_proxy_pool = self.cfg.proxy.free_proxy_pool
            return random.choice(free_proxy_pool)
        except Exception:
            pass

    def get(self, url: str, **kwargs) -> HTMLResponse:
        """
        Returns the GET request encoded in `utf-8`.
        """
        try:
            response = self.session.get(
                url, timeout=self.timeout, proxies=self.proxy_strategy, **kwargs
            )
            response.encoding = "utf-8"
            return response
        except requests.exceptions.ProxyError as exc:
            logger.warning(f"ProxyError: {exc}")
            response = self.session.get(
                url, timeout=self.timeout, proxies=self.rebuild_proxies, **kwargs
            )
            response.encoding = "utf-8"
            return response
        except requests.exceptions.RequestException as exc:
            logger.warning(f"RequestError: {exc}")

    def post(self, url, data, **kwargs):
        try:
            return self.session.post(
                url,
                timeout=self.timeout,
                proxies=self.proxy_strategy,
                data=data,
                **kwargs,
            )
        except requests.exceptions.ProxyError as exc:
            logger.warning(f"ProxyError: {exc}")
            return self.session.post(
                url,
                timeout=self.timeout,
                proxies=self.rebuild_proxies,
                data=data,
                **kwargs,
            )
        except requests.exceptions.RequestException as exc:
            logger.warning(f"RequestError: {exc}")
