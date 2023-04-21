import requests as req2
from playwright.sync_api import Playwright, sync_playwright
from urllib.parse import urlparse
import os
import json

# Helper function to parse the request and click file
def parseReqFile(file):
    with open(file,'r') as rFile:
        lines = rFile.readlines()
    k = [json.loads(line) for line in lines]
    return k

def main(playwright: Playwright) -> None:

    ext_file = "extension"
    extension_dir = "/Users/rajvardhan/Documents/GitHub/WebCheck/"
    log = True

    # Change the URL here
    URL = "https://hindilinks4u.kim/ant-man-and-the-wasp-quantumania-2023-hindi-dubbed-Watch-online/"

    # Create storage directories
    domain = urlparse(URL).netloc
    directory = "crawl/{}".format(domain)
    if not os.path.exists(directory):
        os.mkdir(directory)
        os.mkdir("{}/scripts".format(directory))

    # Set up the browser context
    context = playwright.chromium.launch_persistent_context(
        headless=False,
        user_data_dir = extension_dir,
        devtools = True,
        record_har_path = "{}/harfile.har".format(directory),
        #record_video_dir = "{}/video".format(directory),
        args=[
            "--disable-extensions-except={}".format(ext_file),
            "--load-extension={}".format(ext_file),
             ],
    )

    # Navigate to the webpage
    page = context.new_page()
    page.goto(URL)

    # Define the number of rows and columns in the grid
    num_rows = 3
    num_cols = 3

    # Find the dimensions of the grid
    grid_width = page.evaluate("() => document.documentElement.scrollWidth")
    grid_height = page.evaluate("() => document.documentElement.scrollHeight")

    # Calculate the width and height of each cell in the grid
    cell_width = grid_width // num_cols
    cell_height = grid_height // num_rows

    # Loop through each cell in the grid
    for row in range(num_rows):
        for col in range(num_cols):
            # Calculate the coordinates of the cell
            x = col * cell_width
            y = row * cell_height

            # Move the mouse to the cell and click it
            page.mouse.move(x, y)
            page.mouse.click(x, y)

            if log:
                print("Clicked {}, {}".format(x,y))

            # Wait for a short period of time
            page.wait_for_timeout(1000)
            print("Done Waiting!")

    # Clean up
    print("Closing context....")
    context.close()
    print("Closed context.....")

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
    scripts = []
    for id_req, req in enumerate(requests_json):
        stack = req['call_stack']
        if 'stack' in stack.keys():
            stack = stack['stack']
            if 'callFrames' in stack:
                for cf in stack['callFrames']:
                    scripts.append(cf['url'])

    # For each 3P script, request the JS and save it
    for script in list(set(scripts)):
        if 'chrome-extension' not in script:
            code_ = req2.get(script)
            code = code_.content
            script_name = script.replace('/','_')
            if '.js' not in script_name:
                script_name = script_name + '.js'
            with open("{}/scripts/{}".format(directory, script_name), 'w+') as script_file:
                script_file.write(str(code))


# Execute
with sync_playwright() as playwright:
    main(playwright)
