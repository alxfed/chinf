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
from .utils import start_batch_query, batch_query, default_batch_model


def start_batch(batch=None, **kwargs):
    """ All parameters should be in kwargs, but they are optional
    """
    # Define the payload # /v4/ai/batch/start
    payload = {
        "requests": [
            {
                "id": "request_1",
                "type": "text",
                "modelId": kwargs.get("model", default_batch_model),
                "options": {
                    "prompt": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Say Hi!"}
                            ]
                        }
                    ],
                    "maxOutputTokens": 256
                }
            }
        ]
    }

    # payload = {
    #     batch
    # }

    result = start_batch_query(payload, **kwargs)
    batchId = result

    return batchId

def batch_status(batchid):
    result = batch_query(batchId=batchid, url_suffix='/status')

def cancel_batch(batchid):
    ...

def batch_result(batchid):
    ...


if __name__ == "__main__":
    ...
