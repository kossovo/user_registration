import json

from locust import HttpUser, task

from backend.core.configs import settings
from backend.tests.utils.utils import random_email, random_lower_string


class LocustLoadTesting(HttpUser):
    """
    load test of our user's registration entrypoint
    """

    @task
    def make_registration_load_testing(self):
        data = {
            "email": random_email(),
            "password": random_lower_string(),
        }
        self.client.post(f"{settings.API_V1_STR}/users/register", json.dumps(data))
