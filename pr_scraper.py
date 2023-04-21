
from playwright.sync_api import Playwright, sync_playwright
from urllib.parse import urlparse
import os

def main(playwright: Playwright) -> None:


    ext_file = "extension"
    extension_dir = "/Users/rajvardhan/Documents/GitHub/WebCheck/"
    log = True

    #URL = "https://www.google.com"
    URL = "https://hindilinks4u.kim/ant-man-and-the-wasp-quantumania-2023-hindi-dubbed-Watch-online/"
    domain = urlparse(URL).netloc
    directory = "crawl/{}".format(domain)
    if not os.path.exists(directory):
        os.mkdir(directory)

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

    # WAIT BEFORE CLICKING!
    # hasUserGesture?

    # Download JS files


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

    with open('server/output/request.json', 'r') as requestFile:
        requests = requestFile.read()
    open('server/output/request.json', 'w').close()

    # Save the click data in a new directory


    # Clicks
    with open("{}/clicks.json".format(directory), "w+") as clickFile:
        clickFile.write(clicks)

    # Requests
    with open("{}/requests.json".format(directory), "w+") as requestFile:
        requestFile.write(requests)


with sync_playwright() as playwright:
    main(playwright)
