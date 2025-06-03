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

from .enumerators import *

_app_server_default_instance = None


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
        self.token_memory = SharedMemory(
            create=True, name="TokenStore", size=64)
        self.applications = {}
        self.__autostart = autostart
        self.__started = False

        # Set this instance as the default application server if one is not
        # setup
        logging.info(
            "ApplicationServer started (%s) instance",
            self.server_name)
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
                "remove_application expected Future, " f"got {type(thread)}"
            )
        logger.debug("Sending stop to Application at 0x%s", id(thread))
        start = time.time()
        logger.debug(f"Waiting for 0x{id(thread)} to terminate...")
        while thread.running():
            self.applications[thread].runtime.running = False
            if time.time() - start >= 3.0:
                logger.warning(
                    (
                        f"Application 0x{id(thread)} is not responding "
                        "to termination signal"
                    )
                )
                logger.info(
                    (
                        "Attempting forceful termination for "
                        f"0x{id(thread)}"
                    )
                )
                exception = thread.exception(2)
                if exception:
                    logger.error(
                        (
                            f"Application at 0x{id(thread)} threw exception"
                            f": {exception}"
                        )
                    )
        logger.info(
            "Application 0x%s (%s) Terminated",
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
            logger.info(
                "Terminating Application at 0x%s",
                id(application_thread))
            self.remove_application(application_thread)

    def application_check(
        self, thread: Union[concurrent.futures._base.Future, None] = None
    ) -> tuple:
        not_alive = []
        if not thread:
            for key in self.applications.keys():
                if not key.running():
                    error = key.exception()
                    if error:
                        logger.error(
                            (
                                f"Application at 0x{id(key)} "
                                "has thrown unhandled error"
                            )
                        )
                        tb = traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                        for line in tb:
                            line = line.strip("\r")
                            if line.count("\n") == 0:
                                line = [line]
                            else:
                                line = line.split("\n")
                            for line_detail in line:
                                logger.error(f"0x{id(key)}: {line_detail}")
                    else:
                        logger.warning(
                            (
                                f"Application at 0x{id(key)} "
                                "has stopped running. Terminating"
                            )
                        )
                    not_alive.append(key)
            return tuple(not_alive)
        return () if thread.running() else (thread,)

    def run(self):
        self.__started = True
        try:
            logger.debug("Press Ctrl-C to shit it all")
            while True:
                for application in self.application_check():
                    self.remove_application(application)
                if len(self.applications) == 0:
                    logger.info(f"No applications running")
                    break
        except KeyboardInterrupt:
            self.shutdown()
            self.thread_pool.shutdown()
        finally:
            self.shutdown()
            self.thread_pool.shutdown()


class Application(ABC):
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
            if key not in self.__dict__.keys():
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
            dictionary = {}
            for key, value in self.__dict__.items():
                if not key.startswith("_"):
                    dictionary[key] = value
            return dictionary

        def json(self, **kwargs):
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
            raise TypeError(
                f"{self.__class__.__name__}(app_id) must be of type UUID")
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
