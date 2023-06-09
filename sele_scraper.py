from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import shutil
import pandas as pd
import requests
import os
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Helper function to parse the request and click file
def parseReqFile(file):
    with open(file,'r') as rFile:
        lines = rFile.readlines()
    k = [json.loads(line) for line in lines]
    return k


# selenium to visit website and get logs
def visitWebsite(URL):
    # Params
    ext_file = "extension"
    domain = urlparse(URL).netloc
    directory = "crawl/v3/{}".format(domain)
    do_JS = True
    if not os.path.exists(directory):
        os.mkdir(directory)
        os.mkdir("{}/scripts".format(directory))
    num_rows = 5
    num_cols = 5

    # Setup Selenium
    opt = webdriver.ChromeOptions()
    opt.add_argument("--auto-open-devtools-for-tabs")
    opt.add_argument("load-extension=" + ext_file)
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")

    # Start Driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
    driver.maximize_window()
    driver.get(URL)
    print("Waiting.....")
    time.sleep(60)
    print("Done waiting....")

    # Clicking
    reference_element = driver.find_element(By.TAG_NAME, "body")
    window_size = driver.get_window_size()
    window_width = window_size['width']
    window_height = window_size['height']

    print("Height = {}".format(window_height))
    print("Width = {}".format(window_width))

    print("Top Left = {}, {}".format(reference_element.location['x'],
                                        reference_element.location['y']))

    # Calculate the width and height of each grid
    grid_width = window_width // num_cols
    grid_height = window_height // num_rows

    # Top left
    top_left_x = (-1*window_width)//2
    top_left_y = (-1*window_height)//2

    # Find all text box elements
    text_boxes = driver.find_elements(By.XPATH, "//input[@type='text']")
    print("{} Text Boxes found".format(len(text_boxes)))

    print("Clicking body")
    driver.execute_script('arguments[0].click()', reference_element)


    # Perform a click action on each text box
    print("Clicking Text Boxes")
    for element in text_boxes:
        wait = WebDriverWait(driver, 10)
        clickable_element = wait.until(EC.element_to_be_clickable((By.ID, element.get_attribute("id"))))
        clickable_element.click()


    '''
    for row in range(num_rows):
        for col in range(num_cols):

            # Move cursor
            #ActionChains(driver).move_to_element(reference_element).perform()
            #ActionChains(driver).move_to_element_with_offset(reference_element, top_left_x, top_left_y).perform()
            time.sleep(2)

            # Calculate the coordinates of the center of the grid
            x = col * grid_width
            y = row * grid_height
            print("Clicking: {}, {}".format(x, y))

            # Perform the click action at the center of the grid
            #ActionChains(driver).move_by_offset(reference_element.location['x'] + x,
                                                #reference_element.location['y'] + y).click().perform()


            # Use Selenium to perform a click at the current mouse position
            pyautogui.moveTo(x,y)
            actions = webdriver.ActionChains(driver)
            actions.click().perform()

            print("Clicked: {}, {}".format(x, y))

    '''


    # Read the clicks file and clear it
    with open('server/output/click.json', 'r') as clickFile:
        clicks = clickFile.read()
    open('server/output/click.json', 'w').close()

    # Save it for persistent storage
    with open("{}/clicks.json".format(directory), "w+") as clickFile:
        clickFile.write(clicks)

    # Do the same with requests
    requests_json = parseReqFile("server/output/request.json".format(directory))
    with open('server/output/request.json', 'r') as requestFile:
        requests = requestFile.read()
    open('server/output/request.json', 'w').close()

    # Also save to directory!
    with open("{}/requests.json".format(directory), "w+") as requestFile:
        requestFile.write(requests)

    # Collect the Script URLs
    if do_JS:
        scripts = []
        for id_req, req in enumerate(requests_json):
            stack = req['call_stack']
            if 'stack' in stack.keys():
                stack = stack['stack']
                if 'callFrames' in stack:
                    for cf in stack['callFrames']:
                        scripts.append(cf['url'])

        # For each 3P script, request the JS and save it
        for idscript, script in enumerate(list(set(scripts))):
            if 'chrome-extension' not in script:
                code_ = req2.get(script)
                code = code_.content
                script_name = script.replace('/','_')
                if len(script_name) > 100:
                    script_name = "long_name_script_{}".format(idscript)
                if '.js' not in script_name:
                    script_name = script_name + '.js'
                with open("{}/scripts/{}".format(directory, script_name), 'w+') as script_file:
                    script_file.write(str(code))

    driver.quit()

URL = "https://hindilinks4u.lat/kisi-ka-bhai-kisi-ki-jaan-2023-Watch-online/"
visitWebsite(URL)
