# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from .utils import (query,
                    default_model,
                    llm_soup_to_text)


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
        "reasoning_effort": kwargs.get("reasoning_effort", "low"),
    }

    result = query(payload, '/chat/completions')
    message = result['choices'][0]['message']
    reasoning = message.get('reasoning', '')
    if reasoning:
        thoughts = llm_soup_to_text(reasoning)
    else:
        reasoning_content = message.get('reasoning_content', '')
        if reasoning_content:
            thoughts = llm_soup_to_text(reasoning_content)
        else:
            thoughts = ''
    text = message['content']

    return thoughts, text


if __name__ == "__main__":
    ...
