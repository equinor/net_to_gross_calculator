"""Keep state for users

- pn.state.cache persists state across all sessions as long as the server is
  running
- pn.state.cookies persists state for a given session

Try to persist state for a given user across sessions so that information is not
lost by a simple reload.
"""

# Third party imports
import panel as pn


def get_user_state():
    """Retrieve (a reference to) a dictionary that can persist user state"""
    return pn.state.cookies


def clear_user_state():
    """Clear state for the current user"""
    get_user_state().clear()
