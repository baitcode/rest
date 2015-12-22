import logging

logger = logging.getLogger(__name__)


class UserDefinedApiException(Exception):
    def __init__(self, response, *args, **kwargs):
        super(UserDefinedApiException, self).__init__(*args, **kwargs)
        self.response = response
