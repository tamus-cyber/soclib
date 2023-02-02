"""File for ElasticHandler class"""
# pylint: disable=too-many-arguments
from logging import Handler
from elasticsearch import Elasticsearch
import ecs_logging

class ElasticHandler(Handler):
    """Subclass of logging.Handler used to send logs to Elastic in ECS format"""

    def __init__(self, index_name: str, elastic_client: Elasticsearch = None,
                    username: str = None, password: str = None, verify_certs: bool = True,
                    host: str = None, cloud_id: str = None):
        """Initialize ElasticHandler class

        To initialize, provide index_name and one of the following:
            - An Elasticsearch client object
            - A cloud_id, username, and password
            - A host, username, and password

        Args:
            index_name (str): Name of the index to send logs to
            elastic_client (Elasticsearch, optional): Elasticsearch client to use
            username (str, optional): Username to use for authentication
            password (str, optional): Password to use for authentication
            verify_certs (bool, optional): If True, verify SSL certificates
            host (str, optional): Host to connect to
            cloud_id (str, optional): Cloud ID to connect to

        """
        super().__init__()

        # If an elastic_client is provided, use it. We don't need to make a new client
        if elastic_client:
            self.elastic_client = elastic_client
        # If cloud_id is set, use it to make a new client
        elif cloud_id:
            self.client = Elasticsearch(
                http_auth=(username, password),
                cloud_id=cloud_id
            )
        # Otherwise, use host to make a new client
        else:
            self.client = Elasticsearch(
                basic_auth=(username, password),
                verify_certs=verify_certs,
                hosts=[host]
            )

        # store the name of the index to send logs to
        self.index_name = index_name
        # this is the formatter provided by Elastic to format python logs into ECS format
        self.formatter = ecs_logging.StdlibFormatter()

    def emit(self, record):
        # format the record into ECS format
        record = self.format(record)
        # send the record to Elastic
        self.elastic_client.index(index=self.index_name, body=record)
