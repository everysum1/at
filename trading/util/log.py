import os
import sys
import traceback


class Logger(object):
    logging_message = '[{level}] {message} {data}'
    logging_message_no_data = '[{level}] message: {message}'
    log_level = os.environ.get('LOG_LEVEL', 'INFO')

    def info(self, message, data=''):
        log_level = 'INFO'
        if data is not '':
            print(self.logging_message.format(level=log_level, message=message, data=data))
        else:
            print(self.logging_message_no_data.format(level=log_level, message=message))

    def error(self, message, data=''):
        log_level = 'ERROR'

        print(self.logging_message.format(level=log_level, message=message, data=data))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

    def debug(self, message, data=''):
        log_level = 'DEBUG'

        if self.log_level != log_level:
            return

        if data is not '':
            print(self.logging_message.format(level=log_level, message=message, data=data))
        else:
            print(self.logging_message_no_data.format(level=log_level, message=message))
