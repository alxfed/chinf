# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
from .utils import (query,
                    default_model,
                    get_function,
                    get_func_args,
                    call_function,
                    llm_soup_to_text)


def get_weather(location):
    print(f"Executing weather tool for location: {location}")
    return {"temperature": "72F", "condition": "Sunny"}


def chat_complete(messages=None, instructions=None, tools=None, **kwargs):
    """ All parameters should be in kwargs, but they are optional
    """
    # Receive the instruction
    instruction = kwargs.get('system_instruction', instructions)
    first_message = [dict(role='system', content=instruction)] if instruction else []

    # add contents and user text to the first (instruction) message
    first_message.extend(messages)
    instruction_and_contents = first_message

    # Define the initial payload
    payload = {
        "model":            kwargs.get("model", default_model),
        "messages":         instruction_and_contents,
        "max_tokens":       kwargs.get("max_tokens", 132000),
        "reasoning_effort": "max",
    }
    # Tools if there are some
    if tools:
        payload['tools'] = tools
        payload['tool_choice'] = 'auto'

    while True:
        # Query the API
        result = query(payload, '/chat/completions')
        message = result['choices'][0]['message']
        instruction_and_contents.append(message)
        thoughts = llm_soup_to_text(message['reasoning'])
        text = message['content']
        function_calls = message.get('tool_calls', [])

        if function_calls:
            for function_call in function_calls:
                call_id = function_call.get('id')
                func = function_call.get('function')
                func_name = func.get('name')
                func_args_str = func.get('arguments', '{}')

                try:
                    if isinstance(func_args_str, str):
                        func_args = json.loads(func_args_str)
                    else:
                        func_args = func_args_str
                except Exception as e:
                    func_args = {}
                    print(f"Error parsing tool arguments for {func_name}: {e}")

                # Look up tool by name in globals and caller frames
                func = globals().get(func_name)
                if not func:
                    import inspect
                    frame = inspect.currentframe().f_back
                    while frame:
                        if func_name in frame.f_globals:
                            func = frame.f_globals[func_name]
                            break
                        frame = frame.f_back

                if func and callable(func):
                    try:
                        tool_result = func(**func_args)
                        if isinstance(tool_result, (dict, list)):
                            result = json.dumps(tool_result)
                        else:
                            result = str(tool_result)
                    except Exception as e:
                        result = f"Error executing tool {func_name}: {str(e)}"
                        print(result)
                else:
                    result = f"Error: Tool function {func_name} not found."
                    print(result)

                tool_message = {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": result
                }
                # Add the response
                instruction_and_contents.append(tool_message)
        else:
            break
    return thoughts, text


if __name__ == "__main__":
    ...
