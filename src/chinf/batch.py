# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from .utils import (query,
                    default_model,
                    llm_soup_to_text)


def start_batch(batch=None, **kwargs):
    """ All parameters should be in kwargs, but they are optional
    """

    # Define the payload # /v4/ai/batch/start
    payload = {
        "model":            kwargs.get("model", default_model),
        "messages":         instruction_and_contents
    }

    result = query(payload, '/v4/ai/batch/start', base_url='https://api.cheaperinference.com')
    message = result['choices'][0]['message']
    thoughts = llm_soup_to_text(message['reasoning'])
    text = message['content']

    return thoughts, text


if __name__ == "__main__":
    ...
