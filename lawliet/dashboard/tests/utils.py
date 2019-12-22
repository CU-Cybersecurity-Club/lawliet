"""
Various utilities for testing purposes
"""

from uuid import UUID

# Methods for randomly generating fields for User instances
random_uuid = lambda rd: UUID(int=rd.getrandbits(128)).hex
random_username = lambda rd: f"meepy-{random_uuid(rd)[:10]}"
random_email = lambda rd: f"meepy-{random_uuid(rd)[:10]}@colorado.edu"
random_password = lambda rd: random_uuid(rd)
random_docker_image = (
    lambda rd: "https://hub.docker.com/r/meepy/{random_uuid(rd)[:10]}:{random_uuid(rd)[:10]}"
)

# Generate all of the data for a new user, consisting of a username,
# an email, and a password.
def create_random_user(rd):
    username = random_username(rd)
    email = random_email(rd)
    password = random_password(rd)
    return username, email, password


# Create the data required by a POST request to /signup for signing up a
# new user
def signup_form_data(username, email, password):
    return {
        "username": username,
        "email": email,
        "password": password,
        "repassword": password,
    }


# Create the data required by a POST request to /login to log into a
# service.
def login_form_data(username, email, password):
    return {"username": username, "password": password}


# Create a random user and put their data into a dictionary to be given
# in a POST request to /signup.
def random_signup_form(rd):
    return signup_form_data(*create_random_user(rd))


# Create a random user and put their data into a dictionary to be given
# in a POST request to /login.
def random_login_form(rd):
    return login_form_data(*create_random_user(rd))
