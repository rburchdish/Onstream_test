import os
import pytest
import time
import subprocess
import shutil
import platform
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from conftest import all_ld, active_service
from UI_Constant import *
import UI_Constant
import logging
import json
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()
browser = os.path.basename(__file__).split("_")[1]
plat = platform.platform().split('-')
device = str(plat[0] + "-" + plat[1])

browser = os.path.basename(__file__).split("_")[1]
plat = platform.platform().split('-')
device = os.path.basename(__file__).split("_")[2]


@pytest.fixture(scope="session", autouse=True)
def client_setup(grafana_ip, grafana_port):
    client = InfluxDBClient(host=grafana_ip, port=grafana_port, database='ONSTREAM')
    return client


@pytest.fixture(scope="session", autouse=True)
def auto_start(request, onstream_version, onstream_url, client_setup):
    try:
        archive_version = os.path.abspath(os.curdir) + os.sep + 'Archived' + os.sep + onstream_version
        os.mkdir(archive_version)
    except FileNotFoundError:
        trd = os.path.abspath(os.curdir) + os.sep + 'Archived'
        os.mkdir(trd)
    except FileExistsError:
        pass

    count = 0
    for i in os.listdir(os.path.abspath(os.curdir) + os.sep + 'Archived' + os.sep + onstream_version):
        if not i.startswith('.'):
            count += 1

    testrun = count + 1
    try:
        archive = os.path.abspath(os.curdir) + os.sep + 'Archived' + os.sep + onstream_version + os.sep + str(browser) + '_' + str(testrun)
        os.mkdir(archive)
    except FileNotFoundError:
        at = os.path.abspath(os.curdir) + os.sep + 'Archived' + os.sep + onstream_version
        os.mkdir(at)
    except FileExistsError:
        pass
    test_start = [
        {
            "measurement": "OnStream",
            "tags": {
                "Software": onstream_version,
                "Test": 1,
                "URL": onstream_url,
                "Browser": "Safari",
                "Device": device,
            },
            "time": time.time_ns(),
            "fields": {
                "events_title": "test start",
                "text": "This is the start of test " + "1" + " on firmware " + onstream_version + " tested on " + onstream_url,
                "tags": "Onstream" + "," + "Safari" + "," + "1" + "," + onstream_version + "," + onstream_url
            }
        }
    ]
    ##client_setup.write_points(test_start)

    def auto_fin():
        test_end = [
            {
                "measurement": "OnStream",
                "tags": {
                    "Software": onstream_version,
                    "Test": 1,
                    "URL": onstream_url,
                    "Browser": "Safari",
                    "Device": device,
                },
                "time": time.time_ns(),
                "fields": {
                    "events_title": "test end",
                    "text": "This is the end of test " + "1" + " on firmware " + onstream_version + " tested on " + onstream_url,
                    "tags": "Onstream" + "," + "Safari" + "," + "1" + "," + onstream_version + "," + onstream_url
                }
            }
        ]
        ##client_setup.write_points(test_end)

        Pictures = os.path.abspath(os.curdir) + os.sep + 'Pictures' + os.sep
        Duration = os.path.abspath(os.curdir) + os.sep + 'Pictures' + os.sep

        dest = os.path.abspath(os.curdir) + os.sep + 'Archived' + os.sep + onstream_version + os.sep + str(browser) + '_' + str(testrun)

        try:
            PicturesFile = os.listdir(Pictures)
            for f in PicturesFile:
                if not f.startswith('.'):
                    shutil.move(Pictures + f, dest)
        except FileNotFoundError:
            print("File Not Found at " + Pictures)
            pass

        try:
            DurationFile = os.listdir(Duration)
            for f in DurationFile:
                if not f.startswith('.'):
                    shutil.move(Duration + f, dest)
        except FileNotFoundError:
            print("File Not Found at " + Duration)
            pass
        subprocess.run(['python3', 'ClearFolders.py'])

    request.addfinalizer(auto_fin)


@pytest.fixture(scope="class")
def directory(request):
    name = os.environ.get('PYTEST_CURRENT_TEST')
    direct = os.path.abspath(os.curdir) + os.sep + 'Pictures' + os.sep
    request.cls.direct = direct
    request.cls.name = name
    yield


@pytest.fixture(scope="class")
def current_time(request):
    t1 = datetime.now() + timedelta(hours=1)
    t2 = datetime.now() + timedelta(hours=2)
    t3 = datetime.now() + timedelta(hours=3)

    if datetime.now().strftime('%M') < str(30):
        m = str("{0:0>2}".format(0))
    elif datetime.now().strftime('%M') >= str(30):
        m = str(30)
    now = datetime.now().strftime('%-I:' + m)
    now1 = t1.strftime('%-I:' + m)
    now2 = t2.strftime('%-I:' + m)
    now3 = t3.strftime('%-I:' + m)
    request.cls.now = now
    request.cls.now1 = now1
    request.cls.now2 = now2
    request.cls.now3 = now3
    yield


@pytest.fixture(scope="class")
def setup(request, onstream_url, custom_logo):
    ##appium_service = AppiumService()
    ##appium_service.start()
    dishtv = onstream_url
    desired_caps = {
                    'xcodeSigningId': '68L4N8AYD4',
                    'platformName': 'iOS',
                    'deviceName': 'Commercials iPad2',
                    'automationName': 'XCUITest',
                    'platformVersion': '12.4.9',
                    'browserName': 'Safari',
                    'udid': '3d031e763e5fdb1edcf50a72cb00a21f0d25537c',
                    'showXcodeLog': True,
                    'updatedWDABundleId': 'com.DishNetwork.onstream',
                    'nativeWebTap': True,
                    'safariAllowPopups': True,
                    'safariOpenLinksInBackground': True}
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    driver.get(dishtv)
    request.cls.driver = driver
    logo = custom_logo  # Big logo on home screen
    request.cls.logo = logo
    request.cls.dishtv = dishtv
    yield
    driver.delete_all_cookies()
    driver.quit()

@pytest.fixture(scope="class")
def current_time(request):
    t1 = datetime.now() + timedelta(hours=1)
    t2 = datetime.now() + timedelta(hours=2)
    t3 = datetime.now() + timedelta(hours=3)
    t4 = datetime.now() + timedelta(hours=4)

    if datetime.now().strftime('%M') < str(30):
        m = str("{0:0>2}".format(0))
    elif datetime.now().strftime('%M') >= str(30):
        m = str(30)
    now = datetime.now().strftime('%-I:' + m)
    now1 = t1.strftime('%-I:' + m)
    now2 = t2.strftime('%-I:' + m)
    now3 = t3.strftime('%-I:' + m)
    now4 = t4.strftime('%-I:' + m)
    request.cls.now = now
    request.cls.now1 = now1
    request.cls.now2 = now2
    request.cls.now3 = now3
    request.cls.now4 = now4
    yield


@pytest.mark.usefixtures("setup", "directory")
class TestVersion:
    def test_version(self, onstream_version, onstream_url):
        try:
            WebDriverWait(self.driver, 30).until(ec.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div[2]/div/div[1]/div[2]/span/span[2]/a/span')))  # Wait for the TV Guide Button
            self.driver.find_element(By.XPATH, '//a[@role="button"]').click()  # Click on the Settings Button
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div[2]/div/div[1]/div[3]/span/span/span/a[1]').click()  # Click on Support
            WebDriverWait(self.driver, 30).until(ec.presence_of_element_located((By.XPATH, '//div[@class="_1Z4-o8_T3QF6uOX_L9JVTe"]')))  # Wait for the page to load
            v = self.driver.find_element(By.XPATH, '//p[@class="F0aslfbXZ_xrEWCBq2tyc"]')  # Find the Application Version text
            v = v.text.split(':')[1].strip()
            assert onstream_version == v
        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            client_setup.write_points(body)
            assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                       '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"


@pytest.mark.usefixtures("setup", "directory")
class TestHomeScreen:
    def test_hero_screen(self, onstream_version, onstream_url, client_setup):
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            time.sleep(5)
            '''WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[1]/button'))).click()  # 1st button click
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[2]/button').click()  # Second button click
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[3]/button').click()  # Third button click
            time.sleep(5)
            self.driver.find_element(By.XPATH,'//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[4]/button').click()  # Fourth button click
            time.sleep(15)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[1]/button'))).click()  # 1st button click
            time.sleep(15)
            self.driver.find_element(By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/div/button').click()  # springs pledge learn more
            time.sleep(10)
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/div/button'))).click()  # springs pledge learn more
            ##self.driver.execute_script('arguments[0].scrollIntoView(true);', mif)  # Scroll Down to the Bottom
            ##time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div[2]/button'))).click()  # more info button
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            time.sleep(3)
            ##self.driver.fullscreen_window()
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[2]/button'))).click()  # second button click
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[3]/div/div/div/div/div/button'))).click()  # watch live
            time.sleep(10)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # Close  Live  Click
            time.sleep(10)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located( (By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[3]/button'))).click()  # third button click
            time.sleep(10)
            self.driver.find_element(By.XPATH,'//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[4]/div/div/div/div/div/button').click()  # watch live
            time.sleep(10)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # Close  Live  Click
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/ul/li[4]/button'))).click()  # fourth button click
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[5]/div/div/div/div/div/div/button'))).click()  # resident services learn more click
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div[2]/button').click()  # Resident Services learn more  click
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            time.sleep(4)
            ##self.driver.fullscreen_window()
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HEADER_CONTAINER"]/div[1]/img').is_displayed()  # Springs Apartments logo is displayed
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/div[1]/span').is_displayed()  # Live Button
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/h3').is_displayed()  # hero screen title
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]').is_displayed()  # hero screen description
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/div[2]/div[1]/img').is_displayed()  # hero screen logo
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HERO_CAROUSEL_CONTAINER"]/div/div/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]').is_displayed()  # rating,movie,time left'''
            self.driver.find_element(By.XPATH, '//*[@id="HOME_HERO"]/div/div[1]').click()  # Springs pledge click
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div[2]/button').click()  # Springs pledge learn more click
            time.sleep(5)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            time.sleep(3)
            ##self.driver.fullscreen_window()
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div/div').click()  # weather
            time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/img').click()  # close  weather
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div[1]/div[2]/div/div[2]/div/div[1]').click()  # advert
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/button').click()  # advert more info
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            time.sleep(3)
            ##self.driver.fullscreen_window()
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div[1]/div[2]/div/div[3]/div').click()  # sports
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div').click()  # right arrow
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div').click()  # left arrow
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_1"]/div').click()  # MLB
            time.sleep(3)

        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            client_setup.write_points(body)
            assert False,"Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                       '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"

    def test_news_and_weather(self, onstream_version, onstream_url, client_setup):
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            time.sleep(3)
            '''self.driver.find_element(By.XPATH,'//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div').click()  # right arrow
            time.sleep(5)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div'))).click()  # left arrow
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located( (By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div/button/img'))).click()  # 1st box
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img'))).click()  # volume bar
            ##time.sleep(5)
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'///*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img'))).click()  # caption click missing because captions button is missing
            ##time.sleep(5)
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="subtitle-popper"]/div/ul/div[4]'))).click()  # english
            ##time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  # fullscreen
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # third x
            time.sleep(2)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_1"]/div/button/img'))).click()  # second button click play
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # 2nd box x
            time.sleep(4)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_2"]/div/button/img'))).click()  # third button click play
            time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # third x
            time.sleep(4)
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_2"]/div/button/img').click()  # frouth button click play
            time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # fourth button  x
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div').click()  # right arrow
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_4"]/div/button/img').click()  # fifth button click play
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # fifth button  x
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div/div/div/div/div[2]/h2[1]').is_displayed()  # Words News and Weather displayed
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div/div[1]').is_displayed()  # square box
            self.driver.find_element(By.XPATH, '// *[@ id = "ITEM_SWIMLANE_INNER_CONTAINER_0_0"] / div / div[1]').is_displayed()  # box background image
            self.driver.find_element(By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div/div[3]/div[2]').is_displayed()  # check logo on each box
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div/div[3]/div[3]/h2[1]').is_displayed()  ## check title
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div/div[3]/div[3]/h2[2]').is_displayed()  # check LIVE written and time remaining
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div/div[2]/span').is_displayed()  # live button'''
            self.driver.find_element(By.XPATH, '//*[@id="0"]/div[1]/div').click()  # right arrow
            time.sleep(5)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="0"]/div[1]/div'))).click()  # left arrow
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_0_0"]/div/button/img'))).click()  # 1st box
            time.sleep(10)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img'))).click()  # volume bar
            time.sleep(5)
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'///*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img'))).click()  # caption click missing because captions button is missing
            ##time.sleep(5)
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="subtitle-popper"]/div/ul/div[4]'))).click()  # english
            ##time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  # fullscreen
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # first x
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_0_1"]/div/button/img'))).click()  # second button click play
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # 2nd box x
            time.sleep(4)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_0_2"]/div/button/img'))).click()  # third button click play
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # third x
            time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="0"]/div[1]/div').click()  # right arrow
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="ITEM_0_3"]/div/button/img').click()  # frouth button click play
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # fourth button  x
            time.sleep(3)

        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            ##client_setup.write_points(body)
        ## assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                       '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"

    def test_community_information(self, onstream_version, onstream_url, client_setup):
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            time.sleep(5)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div/div[1]'))).click()  #Community information Refer a Friend
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div/button').click()  # More Info Button
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            ##self.driver.fullscreen_window()
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located( (By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_1"]/div/div[2]/div[2]/p'))).click() # Community perks click 2
            time.sleep(3)
            mif = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div[2]/button')
            self.driver.execute_script('arguments[0].scrollIntoView(true);', mif)  # Scroll Down to the Bottom
            time.sleep(5)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div[2]/button').click()  # More Info Button
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            ##self.driver.fullscreen_window()
            time.sleep(5)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located( (By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_2"]/div/div[1]'))).click()  #resident services
            mif = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div[2]/button')
            self.driver.execute_script('arguments[0].scrollIntoView(true);', mif)  # Scroll Down to the Bottom
            time.sleep(5)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div[2]/button').click()  # More Info Button
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            time.sleep(3)
            ##self.driver.fullscreen_window()
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="SWIMLANE_INNER_CONTAINER_1"]/div[1]/div').click()  # right button
            time.sleep(4)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located( (By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_3"]/div/div[2]/div[2]/p'))).click()  # springs pledge
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div[2]/button').click()  # More Info Button
            time.sleep(3)
            mif = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div[2]/button')
            self.driver.execute_script('arguments[0].scrollIntoView(true);', mif)  # Scroll Down to the Bottom
            time.sleep(5)
            ##self.driver.fullscreen_window()
            time.sleep(15)
            wea = self.driver.find_element(By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_0"]/div/div')
            time.sleep(10)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div/div/div/div/div[2]/h2[2]').is_displayed()  # Words community information shown
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div').is_displayed()  # square box
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div/div[1]').is_displayed()  # box background image
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div/div[3]/div[1]/img').is_displayed()  # check words AD on first box
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div/div[3]/div[2]/h2').is_displayed()  ## check title
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div/div[3]/div[2]/p').is_displayed()  # description



        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            client_setup.write_points(body)
        ## assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                       '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"
    def test_for_you(self, onstream_version, onstream_url, client_setup):
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            '''time.sleep(10)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_0"]/div/div'))).click()  # weather
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/img').click()  # close weather
            time.sleep(10)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_2"]/div/div/div[2]'))).click() # pet friendly
            time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_2_MODAL_BUTTON"]').click()  # more info pet friendly
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            ##self.driver.fullscreen_window()
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="SWIMLANE_INNER_CONTAINER_2"]/div[1]/div').click()  # right button
            time.sleep(4)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_3"]/div/div/div[2]'))).click()  # youre home blog click
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_3_MODAL_BUTTON"]').click()  # more info youre home block click
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            ##self.driver.fullscreen_window()
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div/div/div/div/div[2]/h2[3]').is_displayed()  # Words for you shown
            self.driver.find_element(By.XPATH,'//*[@id="SWIMLANE_INNER_CONTAINER_2"]/div/div/div/div[1]').is_displayed()  # square box
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_0"]/div/div').is_displayed()  # cloud image
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_1"]/div/img').is_displayed()  # sports image (football)
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_2"]/div/div/div[1]/div[2]').is_displayed()  ## check title
            self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_2"]/div/div/div[1]/div[1]').is_displayed()  # check mini photo'''
            time.sleep(10)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_1_0"]/div'))).click()  # weather
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/img').click()  # close weather
            time.sleep(10)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_1_1"]/div'))).click()  # sports
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div'))).click()  # right arrow
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div'))).click()  # left arrow
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_1"]/div'))).click()  # mlb click
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/img'))).click()  # mlb click close
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[1]'))).click()  # home
            time.sleep(3)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_1_2"]/div/div/div[2]'))).click()  # pet friendly
            time.sleep(4)
            self.driver.find_element(By.XPATH, '//*[@id="ITEM_1_2_MODAL_BUTTON"]').click()  # more info pet friendly
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            ##self.driver.fullscreen_window()
            time.sleep(5)
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="1"]/div[1]/div'))).click()  # right arrow
            WebDriverWait(self.driver, 80).until(ec.presence_of_element_located((By.XPATH, '//*[@id="ITEM_1_3"]/div/div/div[2]'))).click()  # youre home blog click
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="ITEM_1_3_MODAL_BUTTON"]').click()  # more info youre home block click
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switch to previous tab
            self.driver.fullscreen_window()
            ##self.driver.fullscreen_window()


        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            client_setup.write_points(body)
        ## assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                 '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"

    def test_sports_buttons(self, onstream_version, onstream_url, client_setup):
            try:
                WebDriverWait(self.driver, 60).until(  ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))
                time.sleep(3)
                arrow = self.driver.find_element(By.XPATH,'//*[@alt="Arrow"]')  # Right arrow button on small widgets
                #time.sleep(10)
                actions = ActionChains(self.driver)
                actions.move_to_element(arrow).click().perform() # click on the right arrow on small widgets
                time.sleep(3)
                arrow = self.driver.find_element(By.XPATH, '//*[@alt="Arrow"]')
                actions.move_to_element(arrow).click().perform() #click on the left arrow on small widgets
                WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, '//*[@alt="sports"]'))).click() # click of sports
                time.sleep(3)
                time.sleep(3)
                self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_0_0"]/div').click()  #MLB Click
                time.sleep(3)
                self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[1]').click()  # Close X box
                time.sleep(1)
                self.driver.find_element(By.XPATH, '//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div').click()  # Right arrow on MLB
                time.sleep(2)
                self.driver.find_element(By.XPATH,  '//*[@id="SWIMLANE_INNER_CONTAINER_0"]/div[1]/div').click()  # left arrow on MLB
                time.sleep(3)
                self.driver.find_element(By.XPATH,  '//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_1_0"]/div/div[1]').click()  # NHL Click
                time.sleep(2)
                ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]').click()  # Close X box
                time.sleep(3)
                nba = self.driver.find_element(By.XPATH,'//*[@id="ITEM_SWIMLANE_INNER_CONTAINER_2_0"]/div')
                self.driver.execute_script('arguments[0].scrollIntoView(true);',nba)  # Scroll Down to the Bottom
                time.sleep(3)
                nba.click()
                time.sleep(2)
                self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]').click()  # Close X  box
                time.sleep(2)
                self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[1]').click()  # Home
                time.sleep(10)

            except NoSuchElementException:
                self.driver.save_screenshot(self.direct + self.name + ".png")
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_not_found": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Element was not found"
            except TimeoutException:
                self.driver.save_screenshot(self.direct + self.name + ".png")
                loading_circle = self.driver.find_elements(By.XPATH,
                                                           '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
                no_streaming = self.driver.find_elements(By.XPATH,
                                                         '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
                error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
                loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
                went_wrong = self.driver.find_elements(By.XPATH,
                                                       '//h2[contains(text(), "Something went wrong with the stream.")]')
                if len(loading_circle) > 0:
                    body = [
                        {
                            "measurement": "OnStream",
                            "tags": {
                                "Software": onstream_version,
                                "Test": 1,
                                "Pytest": self.name,
                                "URL": onstream_url,
                                "Browser": "Chrome",
                                "Device": device,
                            },
                            "time": time.time_ns(),
                            "fields": {
                                "loading_circle": 1,
                            }
                        }
                    ]
                    client_setup.write_points(body)
                    assert False, "Stuck on loading screen"
                elif len(no_streaming) > 0:
                    body = [
                        {
                            "measurement": "OnStream",
                            "tags": {
                                "Software": onstream_version,
                                "Test": 1,
                                "Pytest": self.name,
                                "URL": onstream_url,
                                "Browser": "Chrome",
                                "Device": device,
                            },
                            "time": time.time_ns(),
                            "fields": {
                                "unable_to_connect": 1,
                            }
                        }
                    ]
                    client_setup.write_points(body)
                    assert False, "It appears that you are not able to connect to Streaming Services at this time."
                elif len(error_404) > 0:
                    body = [
                        {
                            "measurement": "OnStream",
                            "tags": {
                                "Software": onstream_version,
                                "Test": 1,
                                "Pytest": self.name,
                                "URL": onstream_url,
                                "Browser": "Chrome",
                                "Device": device,
                            },
                            "time": time.time_ns(),
                            "fields": {
                                "error_404": 1,
                            }
                        }
                    ]
                    client_setup.write_points(body)
                    assert False, "404 error"
                elif len(loading_element):
                    body = [
                        {
                            "measurement": "OnStream",
                            "tags": {
                                "Software": onstream_version,
                                "Test": 1,
                                "Pytest": self.name,
                                "URL": onstream_url,
                                "Browser": "Chrome",
                                "Device": device,
                            },
                            "time": time.time_ns(),
                            "fields": {
                                "element_loading": 1,
                            }
                        }
                    ]
                    client_setup.write_points(body)
                    assert False, "Stuck loading an element"
                elif len(went_wrong):
                    body = [
                        {
                            "measurement": "OnStream",
                            "tags": {
                                "Software": onstream_version,
                                "Test": 1,
                                "Pytest": self.name,
                                "URL": onstream_url,
                                "Browser": "Chrome",
                                "Device": device,
                            },
                            "time": time.time_ns(),
                            "fields": {
                                "went_wrong": 1,
                            }
                        }
                    ]
                    client_setup.write_points(body)
                    assert False, "Something went wrong"
                else:
                    body = [
                        {
                            "measurement": "OnStream",
                            "tags": {
                                "Software": onstream_version,
                                "Test": 1,
                                "Pytest": self.name,
                                "URL": onstream_url,
                                "Browser": "Chrome",
                                "Device": device,
                            },
                            "time": time.time_ns(),
                            "fields": {
                                "timeout_exception": 1,
                            }
                        }
                    ]
                    client_setup.write_points(body)
                    assert False, "timeout error"



@pytest.mark.usefixtures("setup", "directory")
class TestLiveTv:
    def test_modern_guide(self, onstream_version, onstream_url, client_setup):
        try:
            '''WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            ##self.driver.find_element(By.XPATH,UI_Constant.settings_button).click()  #Settings button
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.guide_choice))).click() #change guide style
            time.sleep(3)
            WebDriverWait(self.driver, 60).until( ec.presence_of_element_located((By.XPATH, UI_Constant.modern_guide))).click() #modern guide
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.tv_guide))).click()  # tv guide
            time.sleep(10)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div').click()  # channel right arrow
            ##time.sleep(5)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[4]/div').click()  # channel left arrow
            ##time.sleep(5)
            self.driver.find_element(By.XPATH,'//*[@class="_1TjpZPuLnjCBGtAtPLv7bb"]').click() #play video
            time.sleep(3)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div/button').click()   # watch now
            ##object=self.driver.switch_to.alert
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.watch_now_button))).click()
            time.sleep(15)
            self.driver.find_element(By.XPATH, '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img').click()  # Click volume button
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img').click()  # Click CC button
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="subtitle-popper"]/div/ul/div[4]').click()  #CC English  button
            time.sleep(8)
            self.driver.find_element(By.XPATH,'//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  #fullscreen
            self.driver.find_element(By.XPATH, '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[3]/button/img').click()  # mini tv guide
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.up_arrow))).click() #up arrow
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.down_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.right_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.left_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.play_live_tvguide))).click()
            time.sleep(3)
            WebDriverWait(self.driver,60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.close_live_video))).click()
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/div/span[1]').is_displayed()  # title
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/div/span[1]').is_displayed()  # description
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/span').is_displayed()  # time and time left
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[1]/img').is_displayed()  # image
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[1]').is_displayed()  #box
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]').is_displayed()  # 1 inch of space inbetween next show
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[1]').is_displayed() # logo'''
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))
            time.sleep(3)
            ##self.driver.find_element(By.XPATH,UI_Constant.settings_button).click()  #Settings button
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.XPATH, UI_Constant.guide_choice))).click()  # change guide style
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.XPATH, UI_Constant.modern_guide))).click()  # modern guide
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.XPATH, UI_Constant.tv_guide))).click()  # tv guide
            time.sleep(10)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[2]/div').click()  # channel right arrow
            ##time.sleep(10)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[1]/div[4]/div').click()  # channel left arrow
            ##time.sleep(15)
            play_buttons = self.driver.find_elements(By.XPATH, '//*[@class="_1TjpZPuLnjCBGtAtPLv7bb"]')  # play video
            mylogger.info(play_buttons)
            time.sleep(3)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div/button').click()   # watch now
            ##object=self.driver.switch_to.alert
            for i in range(len(play_buttons)):
                WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                    (By.XPATH,
                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[1]')))  # wait for the guide to populate
                self.driver.find_elements(By.XPATH, '//*[@class="_1TjpZPuLnjCBGtAtPLv7bb"]')[i].click()
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.watch_now_button))).click()
                time.sleep(15)
                self.driver.find_element(By.XPATH,
                                         '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img').click()  # Click volume button
                time.sleep(3)
                self.driver.find_element(By.XPATH,
                                         '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img').click()  # Click CC button
                time.sleep(3)
                self.driver.find_element(By.XPATH,
                                         '//*[@id="subtitle-popper"]/div/ul/div[4]').click()  # CC English  button
                time.sleep(8)
                self.driver.find_element(By.XPATH, '//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  # fullscreen
                self.driver.find_element(By.XPATH,
                                         '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[3]/button/img').click()  # mini tv guide
                time.sleep(5)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.up_arrow))).click()  # up arrow
                time.sleep(3)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.down_arrow))).click()
                time.sleep(3)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.right_arrow))).click()
                time.sleep(3)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.left_arrow))).click()
                time.sleep(5)
                close = self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img')  # close video
                time.sleep(3)
                actions = ActionChains(self.driver)
                actions.move_to_element(close).click().perform()
                time.sleep(3)
                close.click()
                time.sleep(15)
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.play_live_tvguide))).click()
            ##time.sleep(3)
            ##WebDriverWait(self.driver,60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.close_live_video))).click()
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/div/span[1]').is_displayed()  # title
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/div/span[1]').is_displayed()  # description
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/span').is_displayed()  # time and time left
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[1]/img').is_displayed()  # image
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div/div[1]/div/div/div[1]').is_displayed()  # box
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]').is_displayed()  # 1 inch of space inbetween next show
            self.driver.find_element(By.XPATH,
                                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[1]').is_displayed()  # logo
            å
        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            ##client_setup.write_points(body)
            assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,'//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"

    def test_classic_guide(self, onstream_version, onstream_url, client_setup):
        try:
            '''WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))
            time.sleep(3)
            ##self.driver.find_element(By.XPATH, UI_Constant.settings_button).click()  # Settings button
            self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.guide_choice))).click()  # change guide style
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.classic_guide))).click()  # classic
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.tv_guide))).click()  # tv guide
            time.sleep(15)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[2]/div/div/div[2]/div[1]').click()  # click on programming
            time.sleep(6)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div/button').click()  # Click "watch now" button
            time.sleep(15)
            self.driver.find_element(By.XPATH,'//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # X button close
            time.sleep(15)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[1]/div/div').click()  # play video
            time.sleep(15)
            self.driver.find_element(By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img').click()  # Click volume button
            time.sleep(8)
            self.driver.find_element(By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img').click()  # Click CC button
            self.driver.find_element(By.XPATH,'//*[@id="subtitle-popper"]/div/ul/div[4]').click()  # english cc
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  # fullscreen
            self.driver.find_element(By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[3]/button/img').click()  # mini tv guide
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.up_arrow))).click()  # up arrow
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.down_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.right_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.left_arrow))).click()
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[4]/div/div/div/div[1]').is_displayed()  # time
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[2]/div[1]').is_displayed()  # title
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[2]/div[2]').is_displayed()  # description
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div[2]/div/div[1]/div/img').is_displayed()  # logo'''
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))
            time.sleep(3)
            ##self.driver.find_element(By.XPATH, UI_Constant.settings_button).click()  # Settings button
            self.driver.find_element(By.XPATH,
                                     '//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.XPATH, UI_Constant.guide_choice))).click()  # change guide style
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.XPATH, UI_Constant.classic_guide))).click()  # classic
            WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((By.XPATH, UI_Constant.tv_guide))).click()  # tv guide
            time.sleep(15)
            play_buttons = self.driver.find_elements(By.XPATH, '//*[@class="RzTD41B7AU81NA-7nU2w0"]')  # play video
            time.sleep(5)
            mylogger.info(play_buttons)
            time.sleep(3)
            ##self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div/button').click()   # watch now
            ##object=self.driver.switch_to.alert
            for i in range(len(play_buttons)):
                WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                    (By.XPATH,
                     '//*[@id="root"]/div/div/div[1]/div[2]/div/div[1]/div[1]')))  # wait for the guide to populate
                self.driver.find_elements(By.XPATH, '//*[@class="RzTD41B7AU81NA-7nU2w0"]')[i].click()
                ##WebDriverWait(self.driver, 60).until(
                ##ec.presence_of_element_located((By.XPATH, UI_Constant.watch_now_button))).click()
                time.sleep(10)
                self.driver.find_element(By.XPATH,
                                         '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img').click()  # Click volume button
                time.sleep(3)
                self.driver.find_element(By.XPATH,
                                         '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img').click()  # Click CC button
                time.sleep(3)
                self.driver.find_element(By.XPATH,
                                         '//*[@id="subtitle-popper"]/div/ul/div[4]').click()  # CC English  button
                time.sleep(8)
                self.driver.find_element(By.XPATH, '//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  # fullscreen
                self.driver.find_element(By.XPATH,
                                         '//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[3]/button/img').click()  # mini tv guide
                time.sleep(5)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.up_arrow))).click()  # up arrow
                time.sleep(3)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.down_arrow))).click()
                time.sleep(3)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.right_arrow))).click()
                time.sleep(3)
                WebDriverWait(self.driver, 60).until(
                    ec.presence_of_element_located((By.XPATH, UI_Constant.left_arrow))).click()
                time.sleep(5)
                close = self.driver.find_element(By.XPATH, '//*[@id="PLAYER_CLOSE_BTN"]/img')  # close video
                time.sleep(3)
                actions = ActionChains(self.driver)
                actions.move_to_element(close).click().perform()
                time.sleep(3)
                close.click()
                time.sleep(15)
            '''##self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[2]/div[2]').click()  # click on programming
            ##time.sleep(10)
            ##self.driver.find_element(By.XPATH,'//*[@id="root"]/div[2]/div/div[2]/div/div[2]/div/button').click()  # Click "watch now" button
            ##time.sleep(15)
            ##self.driver.find_element(By.XPATH,'//*[@id="PLAYER_CLOSE_BTN"]/img').click()  # X button close
            ##time.sleep(15)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[1]/div/div').click()  # play video
            time.sleep(15)
            self.driver.find_element(By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[1]/button/img').click()  # Click volume button
            time.sleep(8)
            self.driver.find_element(By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[2]/button/img').click()  # Click CC button
            self.driver.find_element(By.XPATH,'//*[@id="subtitle-popper"]/div/ul/div[4]').click()  # english cc
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="TOGGLE_FULLSCREEN_BTN"]/img').click()  # fullscreen
            self.driver.find_element(By.XPATH,'//*[@id="dish-bitmovin-player"]/div[4]/div/div[2]/div[3]/button/img').click()  # mini tv guide
            time.sleep(5)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.up_arrow))).click()  # up arrow
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.down_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.right_arrow))).click()
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.left_arrow))).click()
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[4]/div/div/div/div[1]').is_displayed()  # time
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[2]/div[1]').is_displayed()  # title
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[2]/div[2]').is_displayed()  # description
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div[2]/div/div[1]/div/img').is_displayed()  # logo'''

            logos = self.driver.find_elements(By.XPATH, '//*[@class="_3f53WAdXRRgvavG8gcvjRb"]')  # Channel Logos
            guide_uid = []
            guide_images = []
            for i in range(
                    len(logos)):  # A for loop that collects certain information from the OnStream guide which will be validated against the JSON information
                guide_uid.append(logos[i].get_attribute("alt"))
                guide_images.append(logos[i].get_attribute('src'))
            all_guide_uid = list(dict.fromkeys(guide_uid))
            all_guide_images = list(dict.fromkeys(guide_images))
            '''if len(logos) == len(active_service):
                assert True  # Number of Logos is the same as the number of channels
            else:
                assert False'''
            all_logos =[]
            for subdir, dirs, files in os.walk(os.path.abspath(
                    os.curdir + os.sep + 'logos' + os.sep)):  # A for loop which goes through the logos folder and collects the necessary data for future parsing
                files = [f for f in files if not f[0] == '.']
                dirs[:] = [d for d in dirs if not d[0] == '.']
                for file in files:
                    filepath = subdir + os.sep + file
                    all_logos.append(filepath)


            for js in all_logos:  # Take the JSON data from the above for loop and delete un-needed information and create a new list
                with open(js) as json_file:
                    ld = json.load(json_file)
                    del ld['is_hd']
                    del ld['service_type']
                    all_ld.append(ld)
            mylogger.info(all_guide_uid)
            for gu in all_guide_uid:  # A for loop which compares the list of JSON data with the list of Guide Data in OnStream
                for temp_id in all_ld:
                    if str(temp_id['suid']) in str(gu):
                        mylogger.info(temp_id)
                        mylogger.info(gu)
                        break
                break

        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            client_setup.write_points(body)
            assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                       '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"


@pytest.mark.usefixtures("setup", "directory")
class TestSettings:
    def test_settings(self, onstream_version, onstream_url, client_setup):
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            time.sleep(10)
            ##self.driver.find_element(By.XPATH, UI_Constant.settings_button).click()  # Settings button
            self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[3]/button[2]/div[2]/div/label/div').click()  # Enable large font size
            time.sleep(3)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.tv_guide))).click()  # tv guide
            time.sleep(3)
            ##self.driver.find_element(By.XPATH, UI_Constant.settings_button).click()  # settings button
            self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[5]/button[1]').click()  # Time Format
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[3]/button[2]').click()  # 24 hour
            time.sleep(10)
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.tv_guide))).click()  # tv guide
            time.sleep(10)
            self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            ##self.driver.find_element(By.XPATH, UI_Constant.settings_button).click()  # settings button
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[5]/button[2]/div[1]/span[2]').click()  # temperature format
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[3]/button[2]').click()  # C degrees
            time.sleep(3)
            self.driver.find_element(By.XPATH,'//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[1]').click()  # home
            ##WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, UI_Constant.home_button)))  # Wait for the Home Page to Load
            ##time.sleep(10) ( removed due to xpath inactive )
            ##self.driver.execute_script('arguments[0].scrollIntoView(true)')  # Scroll Down to the Bottom
            time.sleep(10)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div/div').click()  # weather
            time.sleep(10)
            self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[1]/img').click()  # close weather
            time.sleep(10)
            ##self.driver.find_element(By.XPATH, UI_Constant.settings_button).click()  # settings button
            self.driver.find_element(By.XPATH, '//*[@id="HEADER_CONTAINER"]/div[2]/nav/div/button[6]').click()  # settings new
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="FAQS"]').click()  # FAQ
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="LEGAL"]').click()  # legal and about
            time.sleep(5)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[3]/button[1]/div[2]/img').click()  # Terms of Service
            time.sleep(10)
            self.driver.find_element(By.XPATH, '//*[@id="LEGAL"]').click()  # legal and about
            time.sleep(10)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[3]/button[2]/div[2]/img').click()  # Privacy Policy
            time.sleep(10)
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[2]/h2').is_displayed()  # tv guide word
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[4]/h2').is_displayed()  # format options word
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[2]/h2').is_displayed()  # legal word
            self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[4]/h2').is_displayed()  # about word

        except NoSuchElementException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            body = [
                {
                    "measurement": "OnStream",
                    "tags": {
                        "Software": onstream_version,
                        "Test": 1,
                        "Pytest": self.name,
                        "URL": onstream_url,
                        "Browser": "Chrome",
                        "Device": device,
                    },
                    "time": time.time_ns(),
                    "fields": {
                        "element_not_found": 1,
                    }
                }
            ]
            ##client_setup.write_points(body)
            ##assert False, "Element was not found"
        except TimeoutException:
            self.driver.save_screenshot(self.direct + self.name + ".png")
            loading_circle = self.driver.find_elements(By.XPATH,
                                                       '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')
            no_streaming = self.driver.find_elements(By.XPATH,
                                                     '//h1[contains(text(), "It appears that you are not able to connect to Streaming Services at this time.")]')
            error_404 = self.driver.find_elements(By.XPATH, '//h1[contains(text(), "Oops! Error 404")]')
            loading_element = self.driver.find_elements(By.XPATH, '//span[contains(text(), "Loading...")]')
            went_wrong = self.driver.find_elements(By.XPATH,
                                                   '//h2[contains(text(), "Something went wrong with the stream.")]')
            if len(loading_circle) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "loading_circle": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck on loading screen"
            elif len(no_streaming) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "unable_to_connect": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "It appears that you are not able to connect to Streaming Services at this time."
            elif len(error_404) > 0:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "error_404": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "404 error"
            elif len(loading_element):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "element_loading": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Stuck loading an element"
            elif len(went_wrong):
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "went_wrong": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "Something went wrong"
            else:
                body = [
                    {
                        "measurement": "OnStream",
                        "tags": {
                            "Software": onstream_version,
                            "Test": 1,
                            "Pytest": self.name,
                            "URL": onstream_url,
                            "Browser": "Chrome",
                            "Device": device,
                        },
                        "time": time.time_ns(),
                        "fields": {
                            "timeout_exception": 1,
                        }
                    }
                ]
                client_setup.write_points(body)
                assert False, "timeout error"


