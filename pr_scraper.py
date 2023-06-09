import requests as req2
from playwright.sync_api import Playwright, sync_playwright
from urllib.parse import urlparse
import os
import json
import time
from bs4 import BeautifulSoup
import random
import pandas as pd
import sys

# Helper function to parse the request and click file
def parse_request_file(file):
    with open(file,'r') as rFile:
        lines = rFile.readlines()
    k = [json.loads(line) for line in lines]
    return k

def handle_console_message(console_message):
    print(f'[{console_message.type}] {console_message.text}')

def choose_random_webpage(homepage):
    response = req2.get(homepage)
    html_content = response.text

    # parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # get all the links on the page
    links = soup.find_all('a')

    # filter the links to only include those on the same site as the current page
    domain_name = urlparse(homepage).netloc
    subpages = [link['href'] for link in links if urlparse(link['href']).netloc == domain_name]

    subpages_long = []
    for subpage in subpages:
        path = subpage.split(domain_name)[1]
        if len(path) > 39:
            subpages_long.append(subpage)

    if len(subpages_long) > 0:
        return random.choice(subpages_long)
    else:
        return random.choice(subpages)

def capture_dom_snapshot(cdp_session):
    # Enable the DOMSnapshot domain
    cdp_session.send('DOMSnapshot.enable')

    # Capture the DOM snapshot
    result = cdp_session.send('DOMSnapshot.captureSnapshot', {
        'includePaintOrder': True,
        'computedStyles': []
    })

    return result

def get_node_id_to_name_mapping(cdp_session):
    cdp_session.send('DOM.enable')
    document_response = cdp_session.send('DOM.getDocument')

    root_node = document_response['root']
    node_id_to_name_mapping = {}

    def process_node(node):
        node_id_to_name_mapping[node['nodeId']] = node['nodeName']

        if 'children' in node:
            for child_node in node['children']:
                process_node(child_node)

    process_node(root_node)

    return node_id_to_name_mapping

def save_snapshot_to_file(snapshot_data, file_path):
    with open(file_path, 'w') as file:
        json.dump(snapshot_data, file)


def main(playwright: Playwright, idURL, URL) -> None:

    # Setup
    ext_file = "extension"
    extension_dir = "/Users/rajvardhan/Documents/GitHub/WebCheck/"
    #context_dir = "{}/contexts".format(directory)
    log = True
    do_JS = True
    do_Headless = False
    wait_time = 1000

    stopHere = True


    # Create storage directories
    domain = urlparse(URL).netloc
    directory = "crawl/v3/{}".format(domain)
    if not os.path.exists(directory):
        os.mkdir(directory)
        os.mkdir("{}/scripts".format(directory))

    context_dir = "{}/context".format(directory)
    if not os.path.exists(context_dir):
        os.mkdir(context_dir)

    # Set up the browser context
    if do_Headless:
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
                 ],
        )
    else:
        context = playwright.chromium.launch_persistent_context(
            headless=False,
            user_data_dir = context_dir,
            devtools = True,
            record_har_path = "{}/pw_harfile.har".format(directory),
            args=[
                    "--disable-extensions-except={}".format(ext_file),
                    "--load-extension={}".format(ext_file),
                    "--ignore-ssl-errors=yes",
                    "--ignore-certificate-errors",
                 ],
        )


    # Navigate to the webpage
    page = context.new_page()
    page.goto(URL)
    if log: print("Waiting for Page Load")

    # DOM Download
    all_dom = page.content()
    with open("{}/dom.html".format(directory), "w+", encoding = "utf-8") as domFile:
        domFile.write(all_dom)

    page.evaluate('window.open("https://example.com", "_blank")')
    page.wait_for_timeout(1000)
    if stopHere:
        sys.exit()

    cdp_session = context.new_cdp_session(page)
    snapshot = capture_dom_snapshot(cdp_session)
    save_snapshot_to_file(snapshot, '{}/dom_snapshot.json'.format(directory))
    node_map = get_node_id_to_name_mapping(cdp_session)
    save_snapshot_to_file(node_map, '{}/node_map.json'.format(directory))

    print("DOM Saved")

    ##### GRID CLICKING #####

    # Define the number of rows and columns in the grid
    num_rows = 5
    num_cols = 5


    # Find the dimensions of the grid
    grid_width = page.evaluate("() => document.documentElement.scrollWidth")
    grid_height = page.evaluate("() => document.documentElement.scrollHeight")

    # Calculate the width and height of each cell in the grid
    cell_width = grid_width // num_cols
    cell_height = grid_height // num_rows

    # Loop through each cell in the grid
    if log: print("Start Clicking!")
    for row in range(num_rows):
        for col in range(num_cols):
            # Calculate the coordinates of the cell
            x = col * cell_width
            y = row * cell_height

            # Move the mouse to the cell and click it
            page.mouse.move(x, y)
            page.mouse.click(x, y)

            if log:
                print("[--{}--] Clicked {}, {}".format(idURL, x, y))

            page.wait_for_timeout(wait_time)


    print("Closing pages....")
    for p in context.background_pages:
        p.close()
    print("Closed Pages")
    print("Closing Context....")
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
    requests_json = parse_request_file("server/output/request.json")
    with open('server/output/request.json', 'r') as requestFile:
        requests = requestFile.read()
    open('server/output/request.json', 'w').close()
    # Also save to directory!
    with open("{}/requests.json".format(directory), "w+") as requestFile:
        requestFile.write(requests)

    # Page Events
    with open('server/output/PageEvents.json', 'r') as pageEventFile:
        pageEvents = pageEventFile.read()
    open('server/output/PageEvents.json', 'w').close()
    # Also save to directory!
    with open("{}/PageEvents.json".format(directory), "w+") as pageEventFile:
        pageEventFile.write(pageEvents)

    # Collect the Script URLs
    if do_JS:
        scripts = []
        script_map = {}
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
                try:
                    code_ = req2.get(script)
                    code = code_.content
                    script_name = script.replace('/','_')
                    if len(script_name) > 100:
                        script_name = "long_name_script_{}".format(idscript)
                        script_name[script_name] = script
                    if '.js' not in script_name:
                        script_name = script_name + '.js'
                    with open("{}/scripts/{}".format(directory, script_name), 'w+') as script_file:
                        script_file.write(str(code))
                except:
                    print("Error getting JS")

        # Save the script map file
        with open("{}/scripts/script_name_map.json".format(directory), "w+") as scriptMapFile:
            json.dump(script_map, scriptMapFile)



# Execute
with sync_playwright() as playwright:
    URL_LIST2 = ["https://hindilinks4u.lat/kisi-ka-bhai-kisi-ki-jaan-2023-Watch-online/",
                "https://hindilinks4u.kim/ant-man-and-the-wasp-quantumania-2023-hindi-dubbed-Watch-online/",
                "https://ww2.5movierulz.mx/dobaaraa-2022-hdrip-hindi-full-movie-watch-online-free/",
                "https://gosexporn.com/de/xxxvideo/lolly-helps-her-accomplice",
                "https://lookmovie2.to/movies/view/3256226-io-2019",
                "https://yomovies.hair/corona-papers-2023-hindi-dubbed-Watch-online-full-movie/",
                "https://moviehax.me/movies/outer-banks-2023-hindi-dubbed-season-3-complete-netflix-movie-watch-online-hd/",
                "https://kapilsharmashows.net",
                "https://www.hindimoviestv.com/shehzada-2023/",
                "https://fmoviesf.co/movie/bel-air-season-2-2022-052664/"
                ]

    #URL = "https://moviehax.me/movies/outer-banks-2023-hindi-dubbed-season-3-complete-netflix-movie-watch-online-hd/"
    URL = "https://www.google.com"
    main(playwright, 1, URL)

    '''
    visited_sites = []
    for idURL, URL in enumerate(URL_LIST):
        try:
            singleton = "/Users/rajvardhan/Documents/GitHub/WebCheck/SingletonLock"
            if os.path.exists(singleton):
                os.remove(singleton)

            URL = "https://www." + URL
            URL2 = choose_random_webpage(URL)
            print(URL2)
            visited_sites.append(URL2)
            visited_sites.append('\n')
            main(playwright, idURL, URL2)
            time.sleep(30)
        except Exception as e:
            print("Error in {}".format(URL))
            print(e)
            continue


    with open("crawl/v3/visited_sites.txt", "w+") as visitedFile:
        visitedFile.writelines(visited_sites)
    '''
