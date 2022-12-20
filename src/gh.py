""" github class
"""

import logging
from github import Github
from .utils import singleton


@singleton
class GH:
    """_summary_
    """
    def __init__(self, access_token: str):
        self.access_token = access_token

    def verify(self):
        try:
            self.g = Github(login_or_token=self.access_token)
            user_name = self.g.get_user().login
            logging.info(f"Login as github user: {user_name}")
            return True
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False