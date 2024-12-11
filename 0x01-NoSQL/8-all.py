#!/usr/bin/env python3
""" 8-all.py """


def list_all(mongo_collection):
    """ lists all documents in a collection """
    if mongo_collection is not None:
        return mongo_collection.find()
