class StringBuilder(list):
    def build(self):
        return str(self)

    def __str__(self):
    	return ''.join(self)