import pytest
import requests
from requests.auth import HTTPBasicAuth

active_service = []  # A list of SMARTBOX services which are active
all_logos = []  # For storing all the JSON files of the logos
in_use_logos = []  # Create a list of the the logos in the OnStream guide
guide_uid = []  # A list of the OnStream UID's from the guide
guide_images = []  # A list of the OnStream image URLs from the guide
all_ld = []  # A list of the JSON files that are in-use


def pytest_addoption(parser):
    parser.addoption("--onstream_url", dest="onstream_url", action="store", default="https://dh9glwxm3y630.cloudfront.net/", help="The URL for the OnStream instance you wish to test")
    parser.addoption("--smartbox_ip", dest="smartbox_ip", action="store", default="https://10.11.46.166", help="The IP of the SMARTBOX which has the channel lineup for the Onstream instance you are testing with")  #Changed IP to because of Gen2
    parser.addoption("--onstream_version", dest="onstream_version", action="store", default="1.2.32", help="The OnStream version you will be testing")
    parser.addoption("--channel_loop", dest="channel_loop", action="store", default="40", help="The number of channels you wish to flip through in OnStream")
    parser.addoption("--grafana_ip", dest="grafana_ip", action="store", default="10.11.46.179", help="The IP of the Grafana instance")
    parser.addoption("--grafana_port", dest="grafana_port", action="store", default="8086", help="The IP of the Grafana instance")
    parser.addoption("--custom_logo", dest="custom_logo", action="store", default="Infio Whites", help="The Custom Logo which appears in the middle of the main page for OnStream")  #Changed the custom logo
    parser.addoption("--mobile_device_id", dest="mobile_device_id", action="store",default="",help="Give the mobile device id. you will get it from adb device command")
    parser.addoption("--mobile_platform", dest="mobile_platform", action="store",default="Android",
                     help="Give the mobile Platform ")

@pytest.fixture(scope="session")
def onstream_url(request):
    return request.config.getoption("--onstream_url")


@pytest.fixture(scope="session")
def smartbox_ip(request):
    return request.config.getoption("--smartbox_ip")

@pytest.fixture(scope="session")
def mobile_device_id(request):
    return request.config.getoption("--mobile_device_id")
@pytest.fixture(scope="session")
def mobile_platform(request):
    return request.config.getoption("--mobile_platform")

@pytest.fixture(scope="session")
def onstream_version(request):
    return request.config.getoption("--onstream_version")


@pytest.fixture(scope="session")
def channel_loop(request):
    return request.config.getoption("--channel_loop")


@pytest.fixture(scope="session")
def grafana_ip(request):
    return request.config.getoption("--grafana_ip")


@pytest.fixture(scope="session")
def grafana_port(request):
    return request.config.getoption("--grafana_port")


@pytest.fixture(scope="session")
def custom_logo(request):
    return request.config.getoption("--custom_logo")


@pytest.fixture(scope="session", autouse=True)
def smartbox_setup(request, smartbox_ip):
    
    url = smartbox_ip + "/web/analytics/streaminfo"
    response = requests.get(url,
                            auth=HTTPBasicAuth('username', 'password'), verify=False,
                            headers={'User-Agent': 'Custom'})

    # print(response)
    out_json = response.json()
    data = out_json['data']['services']
    info = {}
    for services in data:
        temp_list = [services['serviceId']]
        temp_list.append(services['overallState']['color'])
        info[services['serviceName']] = temp_list
    for key, value in info.items():
        if value[1] == 'OK':
            kv = key, value
            active_service.append(kv)
    return active_service

