import requests as req2
from playwright.sync_api import Playwright, sync_playwright
from urllib.parse import urlparse
import os
import json
import browsermobproxy as BMP
from browsermobproxy import Server
import time

# Helper function to parse the request and click file
def parseReqFile(file):
    with open(file,'r') as rFile:
        lines = rFile.readlines()
    k = [json.loads(line) for line in lines]
    return k

def handle_new_tab(new_page):
    print("New Tab Opened")


def main(playwright: Playwright, URL) -> None:

    ext_file = "extension"
    extension_dir = "/Users/rajvardhan/Documents/GitHub/WebCheck/"
    #context_dir = "{}/contexts".format(directory)
    log = True
    do_JS = True
    do_HAR = False
    do_BMP = False



    # Change the URL here
    #URL = "https://www.google.com"
    #URL = "https://hindilinks4u.kim/ant-man-and-the-wasp-quantumania-2023-hindi-dubbed-Watch-online/"
    #URL = "https://hindilinks4u.lat/kisi-ka-bhai-kisi-ki-jaan-2023-Watch-online/"

    # Create storage directories
    domain = urlparse(URL).netloc
    directory = "crawl/v2/{}".format(domain)
    if not os.path.exists(directory):
        os.mkdir(directory)
        os.mkdir("{}/scripts".format(directory))

    context_dir = "{}/context".format(directory)
    if not os.path.exists(context_dir):
        os.mkdir(context_dir)


    # Start Server
    if do_BMP:
        server = Server("/Users/rajvardhan/Desktop/browsermob-proxy-2.1.4/bin/browsermob-proxy")
        server.start()
        proxy = server.create_proxy()
        proxy.new_har("newhar")
        ###


    # Set up the browser context
    context = playwright.chromium.launch_persistent_context(
        headless=True,
        user_data_dir = context_dir,
        devtools = True,
        record_har_path = "{}/pw_harfile.har".format(directory),
        args=[
                "--headless=new",
                "--disable-extensions-except={}".format(ext_file),
                "--load-extension={}".format(ext_file),
                "--ignore-ssl-errors=yes",
                "--ignore-certificate-errors",
                #"--proxy-server={}".format(proxy.proxy)
             ],
    )

    # Navigate to the webpage
    page = context.new_page()
    page.goto(URL)

    if log: print("Waiting for Page Load")

    #page.wait_for_timeout(20000)
    # Define the number of rows and columns in the grid
    num_rows = 10
    num_cols = 10

    # Find the dimensions of the grid
    grid_width = page.evaluate("() => document.documentElement.scrollWidth")
    grid_height = page.evaluate("() => document.documentElement.scrollHeight")

    # Calculate the width and height of each cell in the grid
    cell_width = grid_width // num_cols
    cell_height = grid_height // num_rows

    wait_time = 1000
    if log: print("Start Clicking!")
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
            page.wait_for_timeout(wait_time)
            print("Done Waiting!")

    # Clean up
    print("Closing pages....")
    for p in context.background_pages:
        p.close()
    print("Closed Pages")
    print("Closing Context....")
    context.close()
    print("Closed context.....")

    if do_BMP:
        har = proxy.har
        with open("{}/harfile.har".format(directory), "w+") as f:
            f.write(json.dumps(har))
        #proxy.stop()
        server.stop()

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


# Execute
with sync_playwright() as playwright:
    URL_LIST = [#"https://hindilinks4u.lat/kisi-ka-bhai-kisi-ki-jaan-2023-Watch-online/",
                #"https://hindilinks4u.kim/ant-man-and-the-wasp-quantumania-2023-hindi-dubbed-Watch-online/",
                "https://hindilinks4u.tel/monica-o-my-darling-2022-Watch-online/",
                "https://4kmovies.xyz/en/loading?id=505642&title=Black%20Panther%3A%20Wakanda%20Forever",
                "https://ww2.5movierulz.mx/dobaaraa-2022-hdrip-hindi-full-movie-watch-online-free/",
                "https://gosexporn.com/de/xxxvideo/lolly-helps-her-accomplice",
                "https://gaypornhdfree.com/perfect-match-bart-cuban-and-helmut-huxley-part-1/",
                "https://hotxxxmilf.pro/en/video/Big-Tit-Milf-Suck-And-Fuck-Milf-Blowjob-Nipples-Tits-Videos-ZNQz",
                "https://herogayab.me/the-kapil-sharma-show-season-4-22nd-april-2023-episode-64-video/17706/"]

    for URL in URL_LIST:
        try:
            singleton = "/Users/rajvardhan/Documents/GitHub/WebCheck/SingletonLock"
            if os.path.exists(singleton):
                os.remove(singleton)

            main(playwright, URL)
            time.sleep(30)
        except Exception as e:
            print("Error in {}".format(URL))
            print(e)
            continue
