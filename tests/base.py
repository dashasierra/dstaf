"""
Perform Unit Tests
"""

from dstaf import Application, ApplicationServer

default_application_server = ApplicationServer(autostart=False)

class TestApp(Application):
    def run(self):
        pass

test_application = TestApp(name="Test Application",
                           server=default_application_server)

def test_application_server_default_name():
    """
    Ensures the Application Server Default Name has not changed
    """
    assert default_application_server.server_name == "DS Application Server"

def test_application_server_application_check():
    """
    The default application server should have only one application
    """
    assert len(default_application_server.application_check()) == 1

def test_application_server_remove_application():
    default_application_server.remove_application(
        thread=default_application_server.application_check()[0]
    )
    assert default_application_server.application_check() == ()

def test_application_creation():
    """
    Add an application, and check it is reported as running
    """
    assert test_application.running == True
    assert test_application.app_name == "Test Application"
    assert test_application.server == default_application_server

