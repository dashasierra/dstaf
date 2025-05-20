"""
Application and Application Server Classes

This module enables Applications to start without first declaring an
ApplicationServer instance in the event that the user wants a single
application to run in the application server instance.
"""

from __future__ import annotations

import concurrent
import inspect
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from multiprocessing.shared_memory import SharedMemory
from uuid import UUID, uuid4

_app_server_default_instance = None


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d+00:00 [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.Formatter.converter = time.gmtime


class ApplicationServer:
    """
    The Application Server is responsible for displaying and interacting with
    any Application that is added to it.
    """

    class Exceptions:
        """
        Server Exceptions
        """

        class NotFound(Exception):
            """
            No Application Server Found
            """

        class NotFuture(Exception):
            """
            Provided Thread is not a Future
            """

    class ApplicationData:
        def __init__(self, application: Application):
            self.runtime = application

    def __init__(
        self,
        name: str = "PyVision Application Server",
        workers: int = int((cpu_count() * 2) + 1),
        autostart=False,
    ):
        """
        Initialise the Application Server

        :param name: [str] Cosmetic name of the server
        :param workers: [int] Number of worker threads
        :param autostart: [bool] Start threading immediately
        """
        self.server_name = name
        self.thread_pool = ThreadPoolExecutor(workers)
        self.token_memory = SharedMemory(create=True, name="TokenStore", size=64)
        self.applications = {}
        self.__autostart = autostart
        self.__started = False

        # Set this instance as the default application server if one is not
        # setup
        logging.info("ApplicationServer started (%s) instance", self.server_name)
        global _app_server_default_instance
        if _app_server_default_instance is None:
            logging.debug(
                "Creating default ApplicationServer instance as one is not set"
            )
            _app_server_default_instance = self

    def start_application(self, app: Application) -> None:
        if not isinstance(app, Application):
            raise TypeError(
                f"""start_application expected app of type '{
                    Application.__name__}'. Got '{
                    app.__class__.__name__}'."""
            )

        if str(inspect.getsource(app.run)).count("while self.running") == 0:
            logger.warning(
                f"""Application '{
                    app.__class__.__name__}' does not have a 'while self.running' loop"""
            )
        self.applications[self.thread_pool.submit(app.run)] = self.ApplicationData(
            application=app
        )
        logger.debug(
            f"""{
                app.__class__.__name__}(name:str('{
                app.app_name}'), app_id:UUID('{
                app.app_id}')) added to {
                    self.__class__.__name__}('{
                        self.server_name}')."""
        )
        if self.__autostart and self.__started == False:
            logger.debug("Starting application server automatically")
            self.run()

    def remove_application(self, thread):
        if not isinstance(thread, concurrent.futures._base.Future):
            raise self.Exceptions.NotFuture(
                f"remove_application expected Future, got {
                    type(thread)}"
            )
        logger.debug(
            "remove_application %s called, setting running=False to runtime", id(thread)
        )
        while thread.running():
            self.applications[thread].runtime.running = False
        logger.info(
            "Application 0x%s (%s) removed",
            id(thread),
            self.applications[thread].runtime.app_name,
        )
        del self.applications[thread]

    def shutdown(self):
        logger.info(
            "Shutdown %s (%s) Signal Received",
            self.__class__.__name__,
            self.server_name,
        )
        for application_thread in list(self.applications.keys()):
            logger.debug("Calling remove_application for %s", application_thread)
            self.remove_application(application_thread)

    def run(self):
        self.__started = True
        try:
            logger.debug("Press Ctrl-C to shit it all")
            while True:
                pass
        except KeyboardInterrupt:
            self.shutdown()
            self.thread_pool.shutdown()


class Application(ABC):

    def __repr__(self):
        return f"{self.__class__.__name__} at 0x{id(self)}"

    def __init__(self, name, app_id: UUID = uuid4(), server=None):
        """
        Application Class.

        The ApplicationClass will attempt to attach itself to the default
        ApplicationServer if one does not exist. If no
        default ApplicationServer exists, the application will
        create one.

        :param name: Cosmetic Name of the Application
        :param app_id: Unique UUID of the Application
        :param server: Optional Server Instance
        """

        # Type Checks
        if not isinstance(app_id, UUID):
            raise TypeError(f"{self.__class__.__name__}(app_id) must be of type UUID")
        # Set Instance Variables
        self.app_name = name
        self.app_id = app_id
        self.running = True
        self.logger = logger

        # Import Global Server Instance
        global _app_server_default_instance

        self.server = (
            server or _app_server_default_instance
        )  # Use default if none provided
        if not self.server:
            # Create default server instance, and start it
            self.server = _app_server_default_instance = ApplicationServer(
                autostart=True
            )
        if self.server:
            self.server.start_application(self)
        else:
            raise ApplicationServer.Exceptions.NotFound(
                "No application server available!"
            )

    @abstractmethod
    def run(self):
        raise NotImplementedError("Run function not implemented")
