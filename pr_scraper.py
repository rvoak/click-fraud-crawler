import requests as req2
from playwright.sync_api import Playwright, sync_playwright
from urllib.parse import urlparse
import os
import json
import browsermobproxy as BMP
from browsermobproxy import Server
import time
from bs4 import BeautifulSoup
import random
import pandas as pd

# Helper function to parse the request and click file
def parseReqFile(file):
    with open(file,'r') as rFile:
        lines = rFile.readlines()
    k = [json.loads(line) for line in lines]
    return k

def intercept_add_event_listener(page):
    #browser = playwright.chromium.launch()
    #page = browser.new_page()

    # Define a custom implementation of addEventListener() that logs to the console
    page.evaluate('''() => {
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            const scripts = Array.from(document.scripts);
            const script = scripts.find(script => {
                const lines = script.innerHTML.split("\\n");
                return lines.some(line => line.includes("addEventListener"));
            });
            const scriptUrl = script ? script.src : "inline script";
            console.log(`addEventListener called from ${scriptUrl} with type=${type}, listener=${listener}, options=${options}`);
            return originalAddEventListener.call(this, type, listener, options);
        };
        console.log(`Adding addEventListener patch`);
    }''')

def intercept_window_open(page):
    #browser = playwright.chromium.launch()
    #page = browser.new_page()

    # Define a custom implementation of window.open() that logs to the console
    page.evaluate('''() => {
        const originalWindowOpen = window.open;
        window.open = function(url, target, features, replace) {
            const scripts = Array.from(document.scripts);
            const script = scripts.find(script => {
                const lines = script.innerHTML.split("\\n");
                return lines.some(line => line.includes("window.open"));
            });
            const scriptUrl = script ? script.src : "inline script";
            console.log(`window.open() called from ${scriptUrl} with url=${url}, target=${target}, features=${features}, replace=${replace}`);
            return originalWindowOpen.call(this, url, target, features, replace);
        };
        console.log(`Adding window.open() patch`);
    }''')

def console_msg(msg):
    if "addEventListener" in msg.text or "Page.windowOpen" in msg.text:
        print("CONSOLE: {}".format(msg.text))

def handle_new_tab(new_page):
    print("New Tab Opened")

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

    #print(subpages)
    subpages_long = []
    for subpage in subpages:
        path = subpage.split(domain_name)[1]
        if len(path) > 39:
            subpages_long.append(subpage)

    if len(subpages_long) > 0:
        return random.choice(subpages_long)
    else:
        return random.choice(subpages)

def main(playwright: Playwright, idURL, URL) -> None:

    # Setup
    ext_file = "extension"
    extension_dir = "/Users/rajvardhan/Documents/GitHub/WebCheck/"
    #context_dir = "{}/contexts".format(directory)
    log = True
    do_JS = True
    do_BMP = False
    do_Shadow = False
    wait_time = 1000


    # Create storage directories
    domain = urlparse(URL).netloc
    directory = "crawl/v3/{}".format(domain)
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
             ],
    )

    # Navigate to the webpage
    page = context.new_page()
    page.on("console", lambda msg: console_msg(msg))
    #intercept_add_event_listener(page)
    #intercept_window_open(page)
    page.goto(URL)
    if log: print("Waiting for Page Load")

    # DOM Download
    all_dom = page.content()
    with open("{}/dom.html".format(directory), "w+", encoding = "utf-8") as domFile:
        domFile.write(all_dom)

    # Shadow DOM Download
    if do_Shadow:
        try:
            shadow_root_selector = find_shadow_root_selector(page)
            if shadow_root_selector:
                shadow_root = page.evaluate_handle(f'document.querySelector("{shadow_root_selector}").shadowRoot')
                shadow_content = shadow_root.evaluate('document.body.innerHTML')
                with open("{}/shadow_dom.html".format(directory), "w+", encoding = "utf-8") as shadowDOMFile:
                    shadowDOMFile.write(shadow_content)
        except:
            print("Shadow DOM Error")

    ##### GRID CLICKING #####

    # Define the number of rows and columns in the grid
    num_rows = 10
    num_cols = 10

    # Find the dimensions of the grid
    grid_width = page.evaluate("() => document.documentElement.scrollWidth")
    grid_height = page.evaluate("() => document.documentElement.scrollHeight")

    # Calculate the width and height of each cell in the grid
    cell_width = grid_width // num_cols
    cell_height = grid_height // num_rows

    #if log: print("Opening test tab")
    #page.evaluate('window.open("https://www.example.com", "_blank")')
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

            # Wait for a short period of time
            page.wait_for_timeout(wait_time)
            #print("BG Pages: {}".format(len(context.background_pages)))
            #print("Done Waiting!")



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

    # Page Events
    pageEvents_json = parseReqFile("server/output/PageEvents.json".format(directory))
    with open('server/output/PageEvents.json', 'r') as pageEventFile:
        pageEvents = pageEventFile.read()
    open('server/output/PageEvents.json', 'w').close()

    # Also save to directory!
    with open("{}/PageEvents.json".format(directory), "w+") as pageEventFile:
        pageEventFile.write(pageEvents)

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

    #URL_LIST = pd.read_csv("top-1m.csv",names = ["rank", "domain"]).tail(10000)['domain'].values[627:]

    #URL_LIST = ["https://www.hindimoviestv.com/"]
    #URL = "https://www.hindimoviestv.com/shehzada-2023/"
    URL = "https://moviehax.me/movies/outer-banks-2023-hindi-dubbed-season-3-complete-netflix-movie-watch-online-hd/"
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
    '''

    with open("crawl/v3/visited_sites.txt", "w+") as visitedFile:
        visitedFile.writelines(visited_sites)
