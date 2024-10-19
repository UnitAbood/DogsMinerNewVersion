import requests
import time
import re

def send_request(session_data):
    """Sends a request to the specified URL with data from the session_data dictionary."""

    try:
        # Extract data from the dictionary
        xsrf_token = session_data['xsrf_token']
        dogsminer_session = session_data['dogsminer_session']
        authority = session_data['authority']
        method = session_data['method']
        path = session_data['path']
        scheme = session_data['scheme']
        accept = session_data['accept']
        accept_encoding = session_data['accept-encoding']
        accept_language = session_data['accept-language']
        priority = session_data['priority']
        referer = session_data['referer']
        sec_fetch_dest = session_data['sec-fetch-dest']
        sec_fetch_mode = session_data['sec-fetch-mode']
        sec_fetch_site = session_data['sec-fetch-site']
        sec_gpc = session_data['sec-gpc']
        x_csrf_token = session_data['x-csrf-token']
        x_requested_with = session_data['x-requested-with']


        cookies = {
            "XSRF-TOKEN": xsrf_token,
            "dogsminer_session": dogsminer_session
        }

        headers = {
            "authority": authority,
            "method": method,
            "path": path,
            "scheme": scheme,
            "accept": accept,
            "accept-encoding": accept_encoding,
            "accept-language": accept_language,
            "priority": priority,
            "referer": referer,
            "sec-fetch-dest": sec_fetch_dest,
            "sec-fetch-mode": sec_fetch_mode,
            "sec-fetch-site": sec_fetch_site,
            "sec-gpc": sec_gpc,
            "x-csrf-token": x_csrf_token,
            "x-requested-with": x_requested_with,

        }

        url = f"{scheme}://{authority}{path}"

        response = requests.request("GET", url, headers=headers, cookies=cookies)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None


def parse_data_file(filepath):
    """Parses the data.txt file and extracts session data, handling multi-line values."""

    with open(filepath, 'r') as f:
        data = f.read()

    session_data = {}

    session_data['xsrf_token'] = re.search(r'"XSRF-TOKEN", "([^"]+)"', data).group(1)
    session_data['dogsminer_session'] = re.search(r'"dogsminer_session", "([^"]+)"', data).group(1)


    headers_block = re.search(r'-Headers @\{(.*?)\}', data, re.DOTALL).group(1)
    for line in headers_block.strip().splitlines():
        if '=' in line:  # Check if the line contains a key-value pair
            key, value = map(str.strip, line.split('=', 1))
            session_data[key.strip('"')] = value.strip('"')

    return session_data


if __name__ == "__main__":
    filepath = "data.txt"
    session_data = parse_data_file(filepath)

    while True:
        response = send_request(session_data)
        if response:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")

        time.sleep(1)
