"""Miscellaneous functions for soclib"""
import os
import requests
from bs4 import BeautifulSoup
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
# Ignore SSL warnings
requests.packages.urllib3.disable_warnings()

def get_website_description(domain: str, timeout=10) -> str:
    """
    Get the description of a website.

    Parameters:
    - domain (str): The domain of the website.
    - timeout (int, optional): The timeout for the request. Defaults to 10.

    Returns:
    - str: The description of the website.
    """

    # Make a request to the website (with a 10 second timeout)
    response = requests.get(f'https://{domain}', timeout=timeout)
    # Parse the HTML content of the website
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the first meta tag with the name "description"
    description_tag = soup.find('meta', {'name': 'description'})

    # Extract the content attribute of the description tag
    description = description_tag['content'] if description_tag else 'No description found'

    return description

def linux_session_check():
    """Check if we're on Wayland or X11 and print a message if we're not

    This function is meant to be called when copy/paste functionality is
    failing on Linux. It will check if we're on Wayland or X11 and print
    a message if we're not. This is meant to be called from a script
    that uses copy/paste functionality.

    Returns:
    - None
    """
    if os.name == "posix":
        # Run echo $XDG_SESSION_TYPE and check if it's wayland
        # If it is, then we're on Wayland
        # If it's not, then we're on X11
        session_manager = os.environ.get("XDG_SESSION_TYPE", "tty")
        # Ignore if using TTY
        if session_manager == "tty":
            return
        if session_manager == "wayland":
            print("Wayland detected. In order to use copy/paste functionality, \
                you must install wl-clipboard.")
        elif session_manager == "x11":
            print("X11 detected. In order to use copy/paste functionality, \
                you must install xclip.")
        else:
            print("Session manager is neither Wayland nor X11. You will have \
                to find a way to use copy/paste functionality manually.")
            return


def _extract_data_from_url(link):
    page = requests.get(link, verify=False) # nosec
    tree = html.fromstring(page.content)
    # Find email and add to list
    # Example: href="mailto:
    email = tree.xpath('//a[contains(@href, "mailto:")]/@href')
    # Find name and add to list
    # Example: <div class="result-listing">
    #          <h2>Harrison, Tyler</h2>
    name = tree.xpath('//div[@class="result-listing"]/h2/text()')
    result = {"name": "", "email": "", "link": link}
    if email:
        try:
            result["email"] = email[0].split(":")[1]
        except IndexError:
            result["email"] = email[0]
        except:
            result["email"] = "(No email found)"
    else:
        result["email"] = "(No email found)"
    if name:
        result["name"] = name[0]
    if result["name"] or result["email"]:
        return result
    else:
        return None


def search_directory(search_term):
    search_term = search_term.lower()
    search_term = search_term.replace(" ", "+")
    url = "https://directory.tamu.edu/?branch=people&cn=" + search_term

    # Get HTML from URL
    page = requests.get(url, verify=False) # nosec
    tree = html.fromstring(page.content)

    # Find all anchor links with the href containing /people/
    raw_links = tree.xpath('//a[contains(@href, "/people/")]/@href')
    links = set(raw_links)

    # Append https://directory.tamu.edu/ to the beginning of each link
    links = set()
    for link in raw_links:
        links.add("https://directory.tamu.edu" + link)

    # Get HTML from each link
    results = []
    threads = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        for link in links:
            threads.append(executor.submit(_extract_data_from_url, link))
        for task in as_completed(threads):
            results.append(task.result())
    return results
