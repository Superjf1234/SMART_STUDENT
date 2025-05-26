import reflex as rx

def test_app_methods():
    """Print out available methods in rx.App class."""
    app = rx.App()
    methods = [method for method in dir(app) if not method.startswith('_')]
    special_methods = [method for method in dir(app) if method.startswith('_') and not method.startswith('__')]
    
    print("Regular methods:")
    for method in methods:
        print(f"- {method}")
        
    print("\nSpecial methods:")
    for method in special_methods:
        print(f"- {method}")
        
    # Test for the specific compile method
    if hasattr(app, 'compile'):
        print("\napp.compile exists!")
    elif hasattr(app, '_compile'):
        print("\napp._compile exists!")
    else:
        print("\nNeither compile nor _compile exists")

if __name__ == "__main__":
    test_app_methods()
