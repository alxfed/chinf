# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import urllib.request
import urllib.error
from os import environ
import re
import html


# The configuration.
api_key = environ.get("CHINF_API_KEY", '')
default_model = environ.get("CHINF_DEFAULT_MODEL", 'gpt-5.6-luna')
api_base = environ.get("CHINF_API_BASE", "https://api.cheaperinference.com/v1")
# Batch configuration.
default_batch_model = environ.get("CHINF_DEFAULT_BATCH_MODEL", 'claude-haiku-4.5-batch')
batch_api_base = environ.get("CHINF_BATCH_API_BASE", "https://api.cheaperinference.com/v4/ai/batch")

# Set the mandatory headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "X-Api-Key": api_key,
    "X-CI-Model-Lock": True,
    "Anthropic-Version": "2023-06-01",
    "User-Agent": "chinf"
}

# Set the batch headers
batch_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "chinf_batch"
}


def get_function(func_name):
    # Look up tool by name in globals
    func = globals().get(func_name)
    # Look up in the caller frames
    if not func:
        import inspect
        frame = inspect.currentframe().f_back
        while frame:
            if func_name in frame.f_globals:
                func = frame.f_globals[func_name]
                break
            frame = frame.f_back

    return func


def get_func_args(func_args_str):
    try:
        if isinstance(func_args_str, str):
            func_args = json.loads(func_args_str)
        else:
            func_args = func_args_str
    except Exception as e:
        func_args = {}
        print(f"Error parsing tool arguments: {e}")

    return func_args


def call_function(func, func_args):
    if func and callable(func):
        try:
            tool_result = func(**func_args)
            if isinstance(tool_result, (dict, list)):
                result = json.dumps(tool_result)
            else:
                result = str(tool_result)
        except Exception as e:
            result = f"Error executing tool: {str(e)}"
            print(result)
    else:
        result = f"Error: Tool function not callable."
        print(result)

    return result


def query(payload, url_suffix, base_url=api_base):
    # Convert data dictionary to JSON and encode it to bytes
    data_bytes = json.dumps(payload).encode('utf-8')
    # Create the Request object
    req = urllib.request.Request(
        f'{base_url}{url_suffix}',
        data=data_bytes,
        headers=headers,
        method="POST")
    # Try to query
    try:
        # Execute the request
        with urllib.request.urlopen(req, timeout=3000) as response:
            response_data = response.read().decode('utf-8')
            output = json.loads(response_data)
        return output

    except urllib.error.HTTPError as e:
        # Handle HTTP errors (e.g., 401 Unauthorized, 400 Bad Request)
        error_info = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Error Details: {error_info}")
        return {}

    except urllib.error.URLError as e:
        # Handle network/connection errors
        print(f"Failed to reach the server: {e.reason}")
        return {}


def start_batch_query(payload, **kwargs):
    """ Start batch processing by a query.
    """
    # Read model from kwargs or substitute the default into the header and on.
    model = kwargs.get("model", default_batch_model),
    batch_headers["ai-model-id"] = model

    # Convert data dictionary to JSON and encode it to bytes
    data_bytes = json.dumps(payload).encode('utf-8')
    # Create the Request object
    req = urllib.request.Request(
        f'{batch_api_base}/start',
        data=data_bytes,
        headers=batch_headers,
        method="POST")
    # Try to query
    try:
        # Execute the request
        with urllib.request.urlopen(req, timeout=3000) as response:
            headers = dict(response.headers)
            response_data = response.read().decode('utf-8')
            output = json.loads(response_data)
        return output

    except urllib.error.HTTPError as e:
        # Handle HTTP errors
        error_info = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Error Details: {error_info}")
        return {}

    except urllib.error.URLError as e:
        # Handle network/connection errors
        print(f"Failed to reach the server: {e.reason}")
        return {}


def batch_query(batchId, url_suffix='/status', **kwargs):
    """"""
    payload = {
        "batchId": batchId
    }
    # Convert data dictionary to JSON and encode it to bytes
    data_bytes = json.dumps(payload).encode('utf-8')
    # Create the Request object
    req = urllib.request.Request(
        f'{batch_api_base}{url_suffix}',
        data=data_bytes,
        headers=batch_headers,
        method="POST")
    # Try to query
    try:
        # Execute the request
        with urllib.request.urlopen(req, timeout=3000) as response:
            headers = dict(response.headers)
            response_data = response.read().decode('utf-8')
            output = json.loads(response_data)
        return output

    except urllib.error.HTTPError as e:
        # Handle HTTP errors (e.g., 401 Unauthorized, 400 Bad Request)
        error_info = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Error Details: {error_info}")
        return {}

    except urllib.error.URLError as e:
        # Handle network/connection errors
        print(f"Failed to reach the server: {e.reason}")
        return {}


def read_batch_result(batchId, **kwargs):
    """"""
    payload = {
        "batchId": batchId
    }
    # Convert data dictionary to JSON and encode it to bytes
    data_bytes = json.dumps(payload).encode('utf-8')
    # Create the Request object
    req = urllib.request.Request(
        f'{batch_api_base}/results',
        data=data_bytes,
        headers=batch_headers,
        method="POST")
    # Try to query
    try:
        # Execute the request
        with urllib.request.urlopen(req, timeout=3000) as response:
            headers = dict(response.headers)
            response_data = response.read().decode('utf-8')
            output = json.loads(response_data)
        return output

    except urllib.error.HTTPError as e:
        # Handle HTTP errors (e.g., 401 Unauthorized, 400 Bad Request)
        error_info = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Error Details: {error_info}")
        return {}

    except urllib.error.URLError as e:
        # Handle network/connection errors
        print(f"Failed to reach the server: {e.reason}")
        return {}


def decode_output(output):
    # Parse the result
    text = ''; thoughts = ''
    for part in output:
        part_type = part.get('type', None)
        if part_type == 'message':
            text = " ".join([chunk['text'] for chunk in part['content'] if chunk['type'] == 'output_text'])
        elif part_type == 'reasoning':
            thoughts = " ".join([chunk['text'] for chunk in part['summary'] if chunk['type'] == 'summary_text'])
    function_calls = [part for part in output if part['type'] == 'function_call']
    return thoughts, text, function_calls


def decode(output):
    text = ''
    thoughts = ''
    for chunk in output:
        chunk_type = chunk.get('type', '')
        if chunk_type == 'text':
            addition = chunk.get('text', '')
            if addition not in ('\n\n', '\n'):
                text += addition

        elif chunk_type == 'thinking':
            thoughts += chunk.get('thinking', '')
    function_calls = [part for part in output if part['type'] == 'tool_use']

    return thoughts, text, function_calls

def llm_soup_to_text(llm_response):
    """
    Cleans and transforms text from Large Language Models (LLMs) by:
    - Removing all Markdown formatting (bold, italics, headers, lists, code blocks, links, etc.).
    - Consolidating multiple newlines into a consistent paragraph separator (`\n\t`).
    - Removing extraneous tabs and multiple spaces.
    - Trimming leading/trailing whitespace.
    """
    if not isinstance(llm_response, str):
        return ""

    text = llm_response

    # --- Step 0: Unescape HTML Entities First ---
    text = html.unescape(text)

    # --- Step 1: Normalize Newlines & Initial Cleanup ---
    text = text.replace('\r\n', '\n')

    # --- Step 2: Remove Fenced Code Blocks completely ---
    # Multiline flag allows ^ to match start of lines.
    text = re.sub(r'^```[^\n]*\n([\s\S]*?)\n```', '', text, flags=re.MULTILINE)
    text = re.sub(r'^~~~[^\n]*\n([\s\S]*?)\n~~~', '', text, flags=re.MULTILINE)
    # Catch ones that might not be at start of line or properly closed with newline
    text = re.sub(r'```[^\n]*\n([\s\S]*?)```', '', text)
    text = re.sub(r'~~~[^\n]*\n([\s\S]*?)~~~', '', text)

    # --- Step 3: Remove HTML Comments and Tags ---
    text = re.sub(r'<!--[\s\S]*?-->', '', text)

    # We want <br> to become newline before stripping tags to preserve line breaks
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Strip other HTML tags, keeping inner text
    text = re.sub(r'<[^>]+>', '', text)

    # --- Step 4: Remove Block-Level Markdown Elements ---
    # Horizontal rules
    text = re.sub(r'^\s*(?:-|\*|_){3,}\s*$', '', text, flags=re.MULTILINE)
    # Blockquotes: remove leading >
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)

    # --- Step 5: Remove Headers ---
    # ATX headers (# Header)
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Setext headers (Underlines Header\n===)
    text = re.sub(r'^([^\n]+)\n\s*(?:=|-){2,}\s*$', r'\1', text, flags=re.MULTILINE)

    # --- Step 6: Remove Links and Images ---
    # Images: ![alt](url) -> remove entire image
    text = re.sub(r'!\[.*?\]\([^\)]*\)', '', text)
    # Links: [text](url) -> keep `text`
    text = re.sub(r'\[([^\]]+)\]\([^\)]*\)', r'\1', text)

    # --- Step 7: Remove Inline Markdown Elements ---
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Bold / Italic - ensure we catch both, ordering matters (*** then ** then *)
    text = re.sub(r'\*{3}([^*]+)\*{3}', r'\1', text)
    text = re.sub(r'_{3}([^_]+)_{3}', r'\1', text)
    text = re.sub(r'\*{2}([^*]+)\*{2}', r'\1', text)
    text = re.sub(r'_{2}([^_]+)_{2}', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Strikethrough
    text = re.sub(r'~~([^~]+)~~', r'\1', text)

    # --- Step 8: Remove List Markers ---
    text = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '', text, flags=re.MULTILINE)

    # --- Step 9: Final Whitespace & Paragraph Normalization ---
    # Strip spaces from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Convert tabs and multiple spaces to single space
    text = text.replace('\t', ' ')
    text = re.sub(r' {2,}', ' ', text)

    # Consolidate multiple newlines to paragraph separator `\n\t`
    text = re.sub(r'\n{2,}', '\n\t', text)

    # --- Step 10: Final Trimming ---
    text = text.strip()
    text = re.sub(r'^[\n\t]+', '', text)
    text = re.sub(r'[\n\t]+$', '', text)

    return text

