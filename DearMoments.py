from dear_moments.input import MessageProcessor
from dear_moments.service import Services


class DearMoments:
    def __init__(self, logger):
        self.logger = logger
        self.message_processor = MessageProcessor(services=None)
