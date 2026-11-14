# Deliberately unsafe example used to verify the CI security gate.
# This file is never imported or executed by the application.

def evaluate_expression(user_input: str):
    return eval(user_input)
