def test_function():
    return (
        rx.card(
            rx.vstack(
                padding="2em",
                spacing="4",
            ),
            variant="surface",
            width="100%",
            max_width="500px",
            margin_top="2em",
        )
    )