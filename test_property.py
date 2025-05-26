
# Simple test code to debug the tooltip
class SimpleTest:
    current_language = 'es'
    
    @property
    def logout_tooltip(self):
        return f'Tooltip for {self.current_language}'

test = SimpleTest()
print(f'Initial: {test.logout_tooltip}')
test.current_language = 'en'
print(f'After change: {test.logout_tooltip}')
