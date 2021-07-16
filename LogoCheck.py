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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from conftest import all_ld, active_service


@pytest.mark.usefixtures("setup", "directory", "current_time")
class TestLiveTV:

 def test_images_displayed(self, onstream_url, onstream_version, first_channel, call_letters, client_setup):
    try:
        WebDriverWait(self.driver, 30).until(ec.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="root"]/div/div/div/div[2]/div/div[1]/div[2]/span/span[2]/a/span'))).click()  # Click on the Guide Button
        WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
            (By.XPATH, '//img[@alt="%s"]' % first_channel)))  # Wait For the Guide to Populate
        channel = self.driver.find_elements(By.XPATH,
                                            '//div[@class="_3oY1sebpEJCA1_vGf8PEBX"]')  # Get a List of all the Current Programs Play Buttons
        FP = open("test.txt", "w")
        # FP.write(channel)
        for i in range(100):  # Go through that list of Programs and Select the Play button for them
            try:
                # FP.write(str(channel[i]) + i +"\n" + i)
                channel[i].click()

                if WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(
                        (By.XPATH, '//img[@alt="%s"]' % call_letters))):  # wait for first channel image to appear
                    break  # Break the Loop if the Program selected is the correct one
                else:  # If the Program was not the correct one, continue the for loop
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(
                        (By.XPATH, '//span[contains(text(), "FULL TV GUIDE")]'))).click()  # click back button
                    WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                        (By.XPATH, '//img[@alt="%s"]' % first_channel)))  # wait for the guide to populate
                    pass
            except TimeoutException:
                button = self.driver.find_elements(By.XPATH,
                                                   '//div[@class="JuHZzfNzpm4bD3481WYQW jEGIqrEa7SjV1rD7HxHBc"]')
                if len(button) == 1:  # see if exit button is there
                    WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                        (By.XPATH, '//button[@class="_1Xyb-h8ETwWmEllf3HIy58"]'))).click()  # click exit button
                    WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                        (By.XPATH, '//img[@alt="%s"]' % first_channel)))  # wait for the guide to populate
                    pass
                elif len(button) == 0:  # see if exit button is there
                    pass
            except NoSuchElementException:
                if not self.driver.find_element(By.XPATH,
                                                '//button[@class="_1Xyb-h8ETwWmEllf3HIy58"]'):  # see if exit button is there
                    pass
                elif self.driver.find_element(By.XPATH,
                                              '//button[@class="_1Xyb-h8ETwWmEllf3HIy58"]'):  # see if exit button is there
                    WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                        (By.XPATH, '//button[@class="_1Xyb-h8ETwWmEllf3HIy58"]'))).click()  # click exit button
                    WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
                        (By.XPATH, '//img[@alt="%s"]' % first_channel)))  # wait for the guide to populate
                    pass
            except ElementClickInterceptedException:
                pass
            except ElementNotInteractableException:
                pass
        WebDriverWait(self.driver, 30).until_not(ec.presence_of_element_located((By.XPATH,
                                                                                 '//div[@class="nvI2gN1AMYiKwYvKEdfIc schema_accent_border-bottom schema_accent_border-right schema_accent_border-left"]')))  # Wait for the loading screen to disappear
        WebDriverWait(self.driver, 30).until(
            ec.visibility_of_element_located((By.XPATH, '//img[@id="bmpui-id-32"]')))  # Wait for the LiveTV to Start
        self.driver.find_element(By.XPATH,
                                 '//span[@class="bmpui-ui-label bmpui-miniEpgToggleLabel"]').click()  # click on the mini guide
        self.driver.find_element(By.XPATH,
                                 '//div[@class="bmpui-container-wrapper"]').is_displayed()  # Channel logo top right
        logos1 = self.driver.find_elements(By.XPATH, '//div[@class="bmpui-ui-image bmpui-channelLogo"]')  # Channel Logos
        FP.write(str(logos1))
        print(logos1)
        FP.close()
        assert False
        self.driver.find_element(By.XPATH,
                                 '//img[@alt="%s"]' % call_letters).is_displayed()  # Channel logo in mini guide
        self.driver.find_element(By.XPATH, '//div[@class="bmpui-ui-container bmpui-divider"]').is_displayed()  # divider
        self.driver.find_element(By.XPATH,
                                 '//div[@class="bmpui-ui-container bmpui-fullTvGuideIcon"]').is_displayed()  # Left Arrow
        self.driver.find_element(By.XPATH,
                                 '//span[@class="bmpui-ui-label bmpui-miniEpgToggleLabel"]').is_displayed()  # Down Arrow
        self.driver.find_element(By.XPATH, '//div[@class="_2ce79Sw43-fKTd_hNeR50P"]').is_displayed()  # Right Arrow
        self.driver.find_element(By.XPATH,
                                 '//div[@class="bmpui-ui-container bmpui-moreInfoIcon"]').is_displayed()  # info emblem
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
