"""
Threaded worker to manage edsm queries.

The EDSMQueries helper will run in it's own thread and perform
a callback when an item on the queue is processed.
"""

from Queue import Queue, Empty
from threading import Thread, Event

from pprint import pformat
from requests import Session, HTTPError, ConnectionError

from material_api import LOGGER, LOG_INFO, LOG_DEBUG
from version import VERSION


class EDSMQueries(object):
    """Handles queries to EDSM in a queued way."""

    THROTTLE = 5
    API_TIMEOUT = 10
    API_BASE_URL = 'https://www.edsm.net'
    API_SYSTEM_V1 = 'api-system-v1'
    API_SYSTEMS_V1 = 'api-systems-v1'
    API_STATUS_V1 = 'api-status-v1'

    def __init__(self):
        """Initialize `EDSMQueries`."""

        self.queue = ClearableQueue()
        self.resultQueue = []
        self.callbackRoot = None
        self.thread = None
        self.session = Session()
        self.session.headers['User-Agent'] = "{product}/{version}".format(
            product="EDMC-Materializer-Plugin",
            version=VERSION,
        )
        self.logLevel = None
        self.logPrefix = 'EDSMQueries > '
        self.interruptEvent = Event()

    def _init_thread(self):
        if self.thread is None:
            self.thread = Thread(target=self.worker, name='EDSM Queries worker')
            self.thread.daemon = True
        return self.thread

    def get_response(self):
        """Return the first queued response."""

        if not self.resultQueue:
            return None

        return self.resultQueue.pop(0)

    def start(self, callback_root):
        """Start the thread."""

        self.callbackRoot = callback_root
        if self.thread is None:
            self._init_thread()

        self.interruptEvent.clear()
        if self.thread.isAlive():
            LOGGER.log(self, LOG_DEBUG, "Thread already started.")
        else:
            self.thread.start()
            LOGGER.log(self, LOG_INFO, "Started thread.")

    def stop(self):
        """Clear queue and stop the thread."""

        LOGGER.log(self, LOG_DEBUG, "Stopping the EDSM Querier Queue.")
        self.queue.clear()
        self.queue.put(None)
        LOGGER.log(self, LOG_DEBUG, "Waiting for worker to exit.")
        # Send an interrupt if we have any THROTTLE waits in place.
        self.interruptEvent.set()
        self.thread.join()
        self.thread = None
        LOGGER.log(self, LOG_INFO, "Stopped EDSMQuerier.")

    def request_get(self, api, endpoint, **request_params):
        """Queues a GET request.

        See #_request() for information on parameters.
        """

        self._request(api, endpoint, 'GET', **request_params)

    def request_post(self, api, endpoint, **data):
        """Send out a post request.

        See #_request() for information on parameters.
        """

        self._request(api, endpoint, 'POST', **data)

    def _request(self, api, endpoint, method, **request_params):
        """Add a new request to the queue.

        :param api: api you want to get
        :param endpoint: EDSM's api endpoint you want to hit
        :param method: HTTP method to use.
        :param request_params: additional request parameters.
        """

        self.queue.put((api, endpoint, method, request_params), False)

    def _http_request(self, api, endpoint, method, request_params):
        """Perform the http request to edsm.

        If performing a get request, the request_params are send as such.
        If performing a post request, the request_params is used as
        :param api: api you want to get
        :param endpoint: EDSM's api endpoint you want to hit
        :param method: HTTP method to use.
        :param request_params: additional request parameters.
        """

        url = "{base}/{api}/{endpoint}".format(base=self.API_BASE_URL, api=api, endpoint=endpoint)
        LOGGER.log(self, LOG_DEBUG, "request {method} '{url}'".format(method=method, url=url))
        if method == 'GET':
            session_request = self.session.get(url, params=request_params, timeout=self.API_TIMEOUT)
        elif method == 'POST':
            session_request = self.session.post(url, data=request_params, timeout=self.API_TIMEOUT)

        session_request.raise_for_status()
        return session_request.json()

    def worker(self):
        """Wait for a request to come in.

        Executes the http request and makes the callback with the reply.
        """
        while True:
            request = self.queue.get()
            if request is None:
                break

            (api, endpoint, method, request_params) = request
            reply = None
            retrying = 0
            LOGGER.debug(self, "Performing callback for {api}/{endpoint}".format(api=api, endpoint=endpoint))
            while retrying < 3:
                try:
                    reply = self._http_request(api, endpoint, method, request_params)
                    break
                except ConnectionError, err:
                    LOGGER.error(self, "HTTP Connection error: {err}".format(err=err))
                except HTTPError, err:
                    LOGGER.error(self, "HTTP error occured: {err}".format(err=err))
                retrying += 1

            if reply:
                self.resultQueue.append((request, reply))
                self.callbackRoot.event_generate('<<EDSMCallback>>', when='tail')
            else:
                LOGGER.error(self, "Unable to perform request {api}/{endpoint}".format(api=api, endpoint=endpoint))

            if self.THROTTLE > 0:
                self.interruptEvent.wait(self.THROTTLE)
            self.queue.task_done()


class ClearableQueue(Queue):
    """Create a queue that can be cleared."""

    def __init__(self):
        """Initialize the queue."""

        Queue.__init__(self)
        self.logPrefix = 'ClearableQueue > '

    def clear(self):
        """Clear all elements from the queue until we are empty."""

        LOGGER.log(self, LOG_DEBUG, "Clearing queue")
        try:
            while True:
                LOGGER.log(self, LOG_DEBUG, "Queue Item Dropped: {item}".format(item=pformat(self.get_nowait())))
        except Empty:
            LOGGER.log(self, LOG_DEBUG, "Yep, we're empty")

        LOGGER.log(self, LOG_DEBUG, "Queue cleared")


EDSM_QUERIES = EDSMQueries()
