"""
Emergency fix for Railway deployment issue.

This script creates a simplified version of the app to debug the deployment issue.
"""

import reflex as rx
import sys, os, datetime
from typing import Dict, List, Optional, Set, Union, Any

# Simple state class with just what we need for testing
class FixedAppState(rx.State):
    # Basic state variables
    is_logged_in: bool = False
    username_input: str = ""
    password_input: str = ""
    error_message: str = ""
    
    def login(self):
        """Simple login method for testing."""
        if self.username_input == "test" and self.password_input == "test":
            self.is_logged_in = True
            self.error_message = ""
        else:
            self.error_message = "Invalid credentials. Use test/test to login."

    def logout(self):
        """Simple logout method."""
        self.is_logged_in = False
        self.username_input = ""
        self.password_input = ""

# Simple login page component
def login_page():
    """Simplified login page."""
    return rx.box(
        rx.vstack(
            rx.heading("SMART STUDENT", size="8"),
            rx.text("Please login to continue"),
            rx.input(
                placeholder="Username",
                on_change=FixedAppState.set_username_input,
                value=FixedAppState.username_input,
            ),
            rx.input(
                placeholder="Password",
                type_="password",
                on_change=FixedAppState.set_password_input,
                value=FixedAppState.password_input,
            ),
            rx.button("Login", on_click=FixedAppState.login),
            rx.text(FixedAppState.error_message, color="red"),
            spacing="4",
            width="300px",
            padding="2em",
        ),
        display="flex",
        justify_content="center",
        align_items="center",
        height="100vh",
    )

# Simple dashboard page component
def main_dashboard():
    """Simplified dashboard page."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("SMART STUDENT Dashboard"),
                rx.spacer(),
                rx.button("Logout", on_click=FixedAppState.logout),
                width="100%",
            ),
            rx.text("Welcome to the dashboard!"),
            rx.text("This is a simplified version to test Railway deployment."),
            width="100%",
            padding="2em",
        ),
        width="100%",
        height="100vh",
    )

# Define the app
app = rx.App()

@app.add_page
def index():
    """Root page that conditionally renders login or dashboard."""
    # IMPORTANT: Call the component functions with parentheses here for current Reflex versions
    return rx.fragment(
        rx.cond(FixedAppState.is_logged_in, main_dashboard(), login_page()),
    )

# For local testing
if __name__ == "__main__":
    from reflex.utils.exec import run_dev
    run_dev(app, mode="dev")
