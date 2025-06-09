"""
Application and Application Server Classes

This module enables Applications to start without first declaring an
ApplicationServer instance in the event that the user wants a single
application to run in the application server instance.
"""

from __future__ import annotations

import concurrent
import inspect
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from multiprocessing.shared_memory import SharedMemory
from typing import Union
from uuid import UUID, uuid4

from .enumerators import HorizontalAlignment, VerticalAlignment

APP_SERVER_DEFAULT_INSTANCE = None


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d+00:00 [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.Formatter.converter = time.gmtime


class ApplicationServer:
    """
    The Application Server is responsible for displaying and interacting with
    any Application that is added to it.
    """

    class Exceptions:  # pylint: disable=too-few-public-methods
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

    class ApplicationData:  # pylint: disable=too-few-public-methods
        """
        Class for tracking of Application Data
        """

        def __init__(self, application: Application):
            """
            Create ApplicationData Instance

            :param application: Application(type) to add
            """
            self.runtime = application

    def __init__(
        self,
        name: str = "DS Application Server",
        workers: int = int((cpu_count() * 2) - 1),
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
        global APP_SERVER_DEFAULT_INSTANCE  # pylint: disable=global-statement
        if APP_SERVER_DEFAULT_INSTANCE is None:
            logging.debug(
                "Creating default ApplicationServer instance as one is not set"
            )
            APP_SERVER_DEFAULT_INSTANCE = self

    def start_application(self, app: Application) -> None:
        """
        Create Thread Futures for Application and
        commence the application's .run() component

        :param app: Application to run
        :return:
        """
        if not isinstance(app, Application):
            raise TypeError(
                f"""start_application expected app of type '{
                    Application.__name__}'. Got '{
                    app.__class__.__name__}'."""
            )

        if str(inspect.getsource(app.run)).count("while self.running") == 0:
            logger.warning(
                "Application '%s' does not have a 'while self.running' loop",
                app.__class__.__name__,
            )
        self.applications[self.thread_pool.submit(app.run)] = self.ApplicationData(
            application=app
        )
        # logger.debug(
        #    f"""{
        #        app.__class__.__name__}(name:str('{
        #        app.app_name}'), app_id:UUID('{
        #        app.app_id}')) added to {
        #            self.__class__.__name__}('{
        #                self.server_name}')."""
        # )
        logger.debug(
            "%s(name:str('%s'), app_id:UUID('%s')) added to %s('%s')",
            app.__class__.__name__,
            app.app_name,
            app.app_id,
            self.__class__.__name__,
            self.server_name,
        )
        if self.__autostart and self.__started is False:
            logger.debug("Starting application server automatically")
            self.run()

    def remove_application(self, thread: concurrent.futures._base.Future):
        """
        Remove Application from the server gracefully,
        then forcefully if the application thread does
        not self-terminate.

        :param thread: Thread Future for the application
        """
        if not isinstance(
            thread, concurrent.futures._base.Future  # pylint: disable=protected-access
        ):
            raise self.Exceptions.NotFuture(
                "remove_application expected Future, " f"got {type(thread)}"
            )
        logger.debug("Sending stop to Application at 0x%s", id(thread))
        start = time.time()
        logger.debug("Waiting for 0x%s to terminate...", id(thread))
        while thread.running():
            self.applications[thread].runtime.running = False
            if time.time() - start >= 3.0:
                logger.warning(
                    (
                        "Application 0x%s is not responding to termination signal",
                        id(thread),
                    )
                )
                logger.info(("Attempting forceful termination for 0x%s", id(thread)))
                exception = thread.exception(2)
                if exception:
                    logger.error(
                        (
                            "Application at 0x%s threw exception: %s",
                            id(thread),
                            exception,
                        )
                    )
        logger.info(
            "Application 0x%s (%s) Terminated",
            id(thread),
            self.applications[thread].runtime.app_name,
        )
        del self.applications[thread]

    def shutdown(self):
        """
        Shut Down Application Server and all Applications within.
        """
        logger.info(
            "Shutdown %s (%s) Signal Received",
            self.__class__.__name__,
            self.server_name,
        )
        for application_thread in list(self.applications.keys()):
            logger.info("Terminating Application at 0x%s", id(application_thread))
            self.remove_application(application_thread)

    def application_check(
        self, thread: Union[concurrent.futures._base.Future, None] = None
    ) -> tuple:
        """
        Checks if an application is alive or not

        :param thread: Application Thread, or None checks all Applications
        :return: tuple of applications that are not alive
        """
        not_alive = []
        if not thread:  # pylint: disable=too-many-nested-blocks
            for key in self.applications:
                if not key.running():
                    error = key.exception()
                    if error:
                        tb = traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                        for line in tb:
                            line = line.strip("\r")
                            if line.count("\n") == 0:
                                line = [line]
                            else:
                                line = line.split("\n")
                                if line[len(line) - 1] == "":
                                    del line[-1]
                            for line_detail in line:
                                logger.error("0x%s: %s", id(key), line_detail)
                    else:
                        logger.warning(
                            (
                                "Application at 0x%s "
                                "has stopped running. Terminating",
                                id(key),
                            )
                        )
                    not_alive.append(key)
            return tuple(not_alive)
        return () if thread.running() else (thread,)

    def run(self):
        """
        Start Application Server
        """
        self.__started = True
        try:
            logger.debug("Press Ctrl-C to stop it all")
            while True:
                for application in self.application_check():
                    self.remove_application(application)
                if len(self.applications) == 0:
                    logger.info("No applications running")
                    break
        except KeyboardInterrupt:
            self.shutdown()
            self.thread_pool.shutdown()
        finally:
            self.shutdown()
            self.thread_pool.shutdown()


class Application(ABC):
    """
    Abstract Application Base Class

    Developers should use this class, and add them to
    an instance of ApplicationServer. If the developer
    does not specify an instance of ApplicationServer,
    this class will create a default instance.
    """

    class AppMeta:
        """
        Application Meta Class. This class provides metadata for
        an Application Class.

        This Class prevents incorrect types being assigned to
        attributes in an effort to make sure the data types are
        adhered to so little to no checking needs to be done
        on data types during manipulation.
        """

        def __setattr_function__(self, key: str, value: any):
            if key not in self.__dict__:
                message = f"The attribute '{key}' does not exist in AppMeta"
                raise NameError(message)
            if not isinstance(value, type(self.__dict__[key])):
                raise TypeError(
                    (
                        f"Type mismatch. Expected type {self.__dict__[key]}"
                        f", got {type(value)}"
                    )
                )
            self.__dict__[key] = value

        def __init__(self, **kwargs):
            """
            Application MetaData
            """

            # Default Configuration
            self.__dict__ = {
                "maximised": False,  # Is Application Maximised
                "cascade": False,  # Should application Cascade
                "align": HorizontalAlignment.CENTRE,  # Horizontal Alignment to Container
                "valign": VerticalAlignment.CENTRE,  # Vertical Alignment to Container
                "dimensions": (40, 10),  # Width, Height as a tuple.
            }
            self.__setattr__ = self.__setattr_function__

            for key, value in kwargs.items():
                self.__setattr_function__(key=key, value=value)

        def dict(self):
            """
            Return Application Configuration as a Dictionary
            :return:
            """
            dictionary = {}
            for key, value in self.__dict__.items():
                if not key.startswith("_"):
                    dictionary[key] = value
            return dictionary

        def json(self, **kwargs):
            """
            Return Application Configuration as JSON.

            :param kwargs: Arguments passed to json.dumps(...)
            :return: json.dumps(self)
            """
            return json.dumps(self.dict(), **kwargs)

        def __repr__(self):
            dictionary = {}
            for key, value in self.__dict__.items():
                if not key.startswith("_"):
                    dictionary[key] = value
            return str(dictionary)

    def __repr__(self):
        return f"{self.__class__.__name__} at 0x{id(self)}"

    def __init__(
        self,
        name,
        app_id: UUID = uuid4(),
        app_meta: AppMeta = AppMeta(),
        server: Union[ApplicationServer, None] = None,
    ):
        """
        Application Class.

        The ApplicationClass will attempt to attach itself to the default
        ApplicationServer if one does not exist. If no
        default ApplicationServer exists, the application will
        create one.

        :param name: Cosmetic Name of the Application
        :param app_id: Unique UUID of the Application (Optional)
        :param app_meta: AppData (Optional)
        :param server: Optional Server Instance (Optional)
        """

        # Type Checks
        if not isinstance(app_id, UUID):
            raise TypeError(f"{self.__class__.__name__}(app_id) must be of type UUID")
        if not isinstance(app_meta, self.AppMeta):
            raise TypeError(
                f"{self.__class__.__name__}(startup) must be of type AppMeta"
            )
        # Set Instance Variables
        self.app_name = name
        self.app_id = app_id
        self.running = True
        self.logger = logger
        self.meta = app_meta

        # Import Global Server Instance
        global APP_SERVER_DEFAULT_INSTANCE  # pylint: disable=global-statement

        self.server = (
            server or APP_SERVER_DEFAULT_INSTANCE
        )  # Use default if none provided
        if not self.server:
            # Create default server instance, and start it
            self.server = APP_SERVER_DEFAULT_INSTANCE = ApplicationServer(
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
        """
        Abstract Run Method. Must be implemented before
        adding to the Application Server.

        Requires a loop of: while self.running:

        Otherwise, the application will close automatically
        once the run() function has completed.
        """
        raise NotImplementedError("Run function not implemented")

    def stop(self):
        """
        Stop the Application. Users can do whatever they need
        to do to clean up here.
        """
        logging.info("Application '%s' received stop signal", self.app_name)
        self.running = False
