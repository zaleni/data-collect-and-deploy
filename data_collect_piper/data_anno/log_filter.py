import logging 

class PngFilePathFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        
    def filter(self, record: logging.LogRecord) -> bool:
        if len(record.args) >= 3:
            path = record.args[2]
            if path.endswith('png'):
                return False
        return True
    
