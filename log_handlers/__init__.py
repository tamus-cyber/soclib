"""Custom logging plugins intended to be used with Loguru.

Right now, this module contains two plugins:

- ElasticHandler: A plugin that sends logs to Elasticsearch.
- SlackHandler: A plugin that sends logs to Slack.
"""
from .elastic_handler import ElasticHandler
from .slack_handler import SlackHandler
