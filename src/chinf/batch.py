# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from .utils import (start_batch_query,
                    batch_query,
                    read_batch_result,
                    default_batch_model)
from time import sleep


def batch_request(batch=None, **kwargs):
    """ Batch query, waiting and cancellation."""
    payload = {
        "requests": batch
    }
    result, hdrs = start_batch_query(payload, **kwargs)
    if result:
        batchId = result['batchId']
        status = result['status']
        rawStatus = result['rawStatus']
        providerMetadata = result['providerMetadata']
    else:
        return '', ''

    while True:
        # Sleep a little bit
        try:
            sleep(10)
            count += 1
        except NameError:
            count = 1
        # Check status
        status, rawStatus = batch_status(batchid=batchId)
        if status == 'ready':
            thoughts, text = read_batch_result(batchId=batchId)
            break
        if count == 60:
            thoughts, text = '', ''
            break

    return thoughts, text

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
    return result['status'], result['rawStatus']

def cancel_batch(batchid):
    result = batch_query(batchId=batchid, url_suffix='/cancel')
    return result['status'], result['rawStatus']

def batch_result(batchid):
    result = read_batch_result(batchid)


if __name__ == "__main__":
    ...
