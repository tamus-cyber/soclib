"""File for ElasticHandler class"""
from logging import Handler  # pylint: disable=missing-module-docstring
import elasticsearch
import ecs_logging

class ElasticHandler(Handler):
    """Subclass of logging.Handler used to send logs to Elastic in ECS format
    """
    def __init__(self, elastic_client: elasticsearch.Elasticsearch, index_name: str, **kwargs):
        super().__init__(**kwargs)
        self.elastic_client = elastic_client
        self.index_name = index_name
        # this is the formatter provided by Elastic to format python logs into ECS format
        self.formatter = ecs_logging.StdlibFormatter()

    def emit(self, record):
        # format the record into ECS format
        record = self.format(record)
        # send the record to Elastic
        self.elastic_client.index(index=self.index_name, body=record)
