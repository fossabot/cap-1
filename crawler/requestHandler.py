# https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
from urllib.request import getproxies

import requests
from faker import Factory
from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry

from utils.logger import Logger

logger = Logger()


class RequestHandler:
    """
    RequestHandler
    """

    def __init__(self, cfg):
        """
        Instantiates a new request handler object.
        """
        # cfg = get_cfg_defaults()
        self.status_forcelist = cfg.request.status_forcelist
        self.timeout = cfg.request.timeout
        self.total = cfg.request.total
        self.backoff_factor = cfg.request.backoff_factor

        self._user_agent = Factory.create()
        self.cfg = cfg

    @property
    def proxy_strategy(self):
        # proxy in config file
        if self.cfg.proxy.enable:
            if self.cfg.proxy.type in self.cfg.proxy.support:
                proxy = "{}://{}".format(self.cfg.proxy.type, self.cfg.proxy.host)
                proxies = {"http": proxy, "https": proxy}
                return proxies
            logger.warning('using system proxy')
        # logger.info('using system proxy')
        return getproxies()

    @property
    def retry_strategy(self) -> Retry:
        """
        Using Transport Adapters we can set a default timeout for all HTTP calls
        Add a retry strategy to your HTTP client is straightforward.
        We create a HTTPAdapter and pass our strategy to the adapter.
        """
        return Retry(total=self.total,
                     status_forcelist=self.status_forcelist,
                     backoff_factor=self.backoff_factor
                     )

    @property
    def session(self) -> Session:
        """

        """
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=self.retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        # Often when using a third party API you want to verify that the returned response is indeed valid.
        # Requests offers the shorthand helper raise_for_status()
        # which asserts that the response HTTP status code is not a 4xx or a 5xx,
        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        # the requests library offers a 'hooks' interface
        # where you can attach callbacks on certain parts of the request process.
        session.hooks['response'] = [assert_status_hook]
        # use faker generate fake user-agent
        session.headers.update({
            "User-Agent": self._user_agent.user_agent()
        })
        session.proxies.update(self.proxy_strategy)
        return session

    def get(self, url: str, params: dict = None, **kwargs) -> Response:
        """
        Returns the GET request encoded in `utf-8`.
        """
        response = self.session.get(url, timeout=self.timeout, params=params, **kwargs)
        response.encoding = 'utf-8'
        return response

    def post(self, url: str, data, headers, **kwargs):
        response = self.session.post(url, data, timeout=self.timeout, headers=headers, **kwargs)
        return response
