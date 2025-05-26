class Test:
    def __init__(self):
        self.lang = "es"
    
    @property
    def tooltip(self):
        return f"Tooltip: {self.lang}"

t = Test()
print(f"Initial: {t.tooltip}")
t.lang = "en"
print(f"After change: {t.tooltip}")
