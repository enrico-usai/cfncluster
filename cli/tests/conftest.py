"""
This module loads pytest fixtures and plugins needed by all tests.

It's very useful for fixtures that need to be shared among all tests.
"""
from __future__ import print_function

import boto3
import pytest
from botocore.stub import Stubber

from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def failed_with_message(capsys):
    """Assert that the command exited with a specific error message."""
    __tracebackhide__ = True

    def _failed_with_message(func, message, *args, **kwargs):
        __tracebackhide__ = True
        with pytest.raises(SystemExit) as error:
            func(*args, **kwargs)
        assert error.type == SystemExit
        assert error.value.code == 1
        if message:
            assert capsys.readouterr().err == message

    return _failed_with_message


@pytest.fixture()
def test_datadir(request, datadir):
    """
    Inject the datadir with resources for the specific test function.

    If the test function is declared in a class then datadir is ClassName/FunctionName
    otherwise it is only FunctionName.
    """
    function_name = request.function.__name__
    if not request.cls:
        return datadir / function_name

    class_name = request.cls.__name__
    return datadir / "{0}/{1}".format(class_name, function_name)


@pytest.fixture()
def convert_to_date_mock(request, mocker):
    """Mock convert_to_date function by enforcing the timezone to UTC."""
    module_under_test = request.module.__name__.replace("test_", "")

    def _convert_to_date_utc(*args, **kwargs):
        from awsbatch.utils import convert_to_date
        from dateutil import tz

        # executes convert_to_date but overrides arguments so that timezone is enforced to utc
        if "timezone" in kwargs:
            del kwargs["timezone"]
        return convert_to_date(timezone=tz.tzutc(), *args, **kwargs)

    return mocker.patch("awsbatch." + module_under_test + ".convert_to_date", wraps=_convert_to_date_utc)


@pytest.fixture()
def awsbatch_boto3_stubber(request, mocker):
    """
    Create a function to easily mock boto3 clients created with Boto3ClientFactory.

    To mock a boto3 service simply pass the name of the service to mock and
    the mocked requests, where mocked_requests is an object containing the method to mock,
    the response to return and the expected params for the boto3 method that gets called.

    The function makes use of botocore.Stubber to mock the boto3 API calls.
    Multiple boto3 services can be mocked as part of the same test.
    """
    __tracebackhide__ = True
    created_stubbers = []
    mocked_clients = {}
    region = "us-east-1"
    # Mock Boto3ClientFactory in the module under test.
    # Use a side_effect to allow mocking multiple clients in the same test function.
    module_under_test = request.module.__name__.replace("test_", "")
    mocked_client_factory = mocker.patch("awsbatch." + module_under_test + ".Boto3ClientFactory", autospec=True)
    mocked_client_factory.return_value.get_client.side_effect = lambda x: mocked_clients[x]
    mocked_client_factory.return_value.region = region

    def _boto3_stubber(service, mocked_requests):
        client = boto3.client(service, region)
        stubber = Stubber(client)
        # Save a ref to the stubber so that we can deactivate it at the end of the test.
        created_stubbers.append(stubber)

        # Attach mocked requests to the Stubber and activate it.
        if not isinstance(mocked_requests, list):
            mocked_requests = [mocked_requests]
        for mocked_request in mocked_requests:
            stubber.add_response(
                mocked_request.method, mocked_request.response, expected_params=mocked_request.expected_params
            )
        stubber.activate()

        # Add stubber to the collection of mocked clients. This allows to mock multiple clients.
        # Mocking twice the same client will replace the previous one.
        mocked_clients[service] = client
        return client

    # yield allows to return the value and then continue the execution when the test is over.
    # Used for resources cleanup.
    yield _boto3_stubber

    # Assert that all mocked requests were consumed and deactivate all stubbers.
    for stubber in created_stubbers:
        stubber.assert_no_pending_responses()
        stubber.deactivate()


DEFAULT_AWSBATCHCLICONFIG_MOCK_CONFIG = {
    "region": "region",
    "proxy": None,
    "aws_access_key_id": "aws_access_key_id",
    "aws_secret_access_key": "aws_secret_access_key",
    "job_queue": "job_queue",
}


@pytest.fixture()
def awsbatchcliconfig_mock(request, mocker):
    """Mock AWSBatchCliConfig object with a default mock."""
    module_under_test = request.module.__name__.replace("test_", "")
    mock = mocker.patch("awsbatch." + module_under_test + ".AWSBatchCliConfig", autospec=True)
    for key, value in DEFAULT_AWSBATCHCLICONFIG_MOCK_CONFIG.items():
        setattr(mock.return_value, key, value)
    return mock


@pytest.fixture()
def boto3_stubber(request, mocker):
    """
    Create a function to easily mock boto3 clients.

    To mock a boto3 service simply pass the name of the service to mock and
    the mocked requests, where mocked_requests is an object containing the method to mock,
    the response to return and the expected params for the boto3 method that gets called.

    The function makes use of botocore.Stubber to mock the boto3 API calls.
    Multiple boto3 services can be mocked as part of the same test.
    """
    __tracebackhide__ = True
    created_stubbers = []
    mocked_clients = {}

    module_under_test = request.module.__name__.replace("test_", "").replace("tests.", "")
    mocked_client_factory = mocker.patch(module_under_test + ".boto3", autospec=True)
    mocked_client_factory.client.side_effect = lambda x: mocked_clients[x]

    def _boto3_stubber(service, mocked_requests):
        client = boto3.client(service)
        stubber = Stubber(client)
        # Save a ref to the stubber so that we can deactivate it at the end of the test.
        created_stubbers.append(stubber)

        # Attach mocked requests to the Stubber and activate it.
        if not isinstance(mocked_requests, list):
            mocked_requests = [mocked_requests]
        for mocked_request in mocked_requests:
            stubber.add_response(
                mocked_request.method, mocked_request.response, expected_params=mocked_request.expected_params
            )
        stubber.activate()

        # Add stubber to the collection of mocked clients. This allows to mock multiple clients.
        # Mocking twice the same client will replace the previous one.
        mocked_clients[service] = client
        return client

    # yield allows to return the value and then continue the execution when the test is over.
    # Used for resources cleanup.
    yield _boto3_stubber

    # Assert that all mocked requests were consumed and deactivate all stubbers.
    for stubber in created_stubbers:
        stubber.assert_no_pending_responses()
        stubber.deactivate()


@pytest.fixture()
def pcluster_config_reader(test_datadir):
    """
    Define a fixture to render pcluster config templates associated to the running test.

    The config for a given test is a pcluster.config.ini file stored in the configs_datadir folder.
    The config can be written by using Jinja2 template engine.
    The current renderer already replaces placeholders for current keys:
        {{ region }}, {{ os }}, {{ instance }}, {{ scheduler}}, {{ key_name }},
        {{ vpc_id }}, {{ public_subnet_id }}, {{ private_subnet_id }}
    The current renderer injects options for custom templates and packages in case these
    are passed to the cli and not present already in the cluster config.
    Also sanity_check is set to true by default unless explicitly set in config.

    :return: a _config_renderer(**kwargs) function which gets as input a dictionary of values to replace in the template
    """
    config_file = "pcluster.config.ini"

    def _config_renderer(**kwargs):
        config_file_path = test_datadir / config_file
        # default_values = _get_default_template_values(vpc_stacks, region, request)
        file_loader = FileSystemLoader(str(test_datadir))
        env = Environment(loader=file_loader)
        rendered_template = env.get_template(config_file).render(**kwargs)
        config_file_path.write_text(rendered_template)
        return config_file_path

    return _config_renderer
