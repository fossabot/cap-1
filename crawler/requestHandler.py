# https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

import random
from urllib.request import getproxies

import requests
from requests.adapters import HTTPAdapter
from requests_html import HTMLResponse
from requests_html import HTMLSession
from urllib3.util.retry import Retry

from utils.logger import setup_logger

logger = setup_logger()


class RequestHandler:
    """
    RequestHandler
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
        # try:
        #     faker = UserAgent(fallback='google')
        #     self._user_agent = faker.chrome
        # except FakeUserAgentError:
        #     pass
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
        # return {'http': 'http://61.135.186.243:80'}

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

        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        # the requests library offers a 'hooks' interface
        # where you can attach callbacks on certain parts of the request process.
        session.hooks['response'] = [assert_status_hook]
        # use faker generate fake user-agent
        # requests_html 本身用的就是fake-user-agent
        # session.headers.update({
        #     "User-Agent": self._user_agent
        # })
        session.proxies.update(self.proxy_strategy)
        return session

    def get(self, url: str, **kwargs) -> HTMLResponse:
        """
        Returns the GET request encoded in `utf-8`.
        """
        request = requests.Request('GET', url)
        prepare = self.session.prepare_request(request)
        try:
            response = self.session.send(prepare, timeout=self.timeout, **kwargs)
            response.encoding = 'utf-8'
            return response
        except requests.exceptions.ProxyError as exc:
            free_proxy_pool = self.cfg.proxy.free_proxy_pool
            if free_proxy_pool is not None:
                self.session.rebuild_proxies(prepare, proxies=random.choice(free_proxy_pool))
                response = self.session.send(prepare, timeout=self.timeout, **kwargs)
                response.encoding = 'utf-8'
                return response
            logger.warning(f'fail to request: {exc}')
        except requests.exceptions as exc:
            logger.warning(f'fail to request: {exc}')

    def post(self, url, data, **kwargs):

        request = requests.Request('POST', url=url, data=data, **kwargs)
        prepare = self.session.prepare_request(request)
        response = self.session.send(prepare, timeout=self.timeout, **kwargs)
        return response
