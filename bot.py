import requests
import time
import re

def send_request(session_data):
    """Sends a request to the specified URL with data from the session_data dictionary."""

    try:
        # Extract data from the dictionary (more efficient way)
        cookies = {
            "XSRF-TOKEN": session_data['xsrf_token'],
            "dogsminer_session": session_data['dogsminer_session']
        }

        headers = {key: value for key, value in session_data.items() if key not in ['xsrf_token', 'dogsminer_session']}

        url = f"{session_data['scheme']}://{session_data['authority']}{session_data['path']}"

        response = requests.request(session_data['method'], url, headers=headers, cookies=cookies)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None


def parse_data_file(filepath):
    """Parses the data.txt file and extracts session data, handling multi-line header values."""
    with open(filepath, 'r') as f:
        data = f.read()

    session_data = {}

    session_data['xsrf_token'] = re.search(r'"XSRF-TOKEN", "([^"]+)"', data).group(1)
    session_data['dogsminer_session'] = re.search(r'"dogsminer_session", "([^"]+)"', data).group(1)

    headers_block = re.search(r'-Headers @\{(.*?)\}', data, re.DOTALL).group(1)
    current_key = None
    current_value = ""

    for line in headers_block.strip().splitlines():
        if '=' in line:
            if current_key:  # Save the previous header if it was multi-line
                session_data[current_key.strip('"')] = current_value.strip('"')
            key, value = map(str.strip, line.split('=', 1))
            current_key = key
            current_value = value
        elif current_key:  # continuation of a multi-line header
            current_value += line.strip()

    if current_key:  # Save the last header
        session_data[current_key.strip('"')] = current_value.strip('"')

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
