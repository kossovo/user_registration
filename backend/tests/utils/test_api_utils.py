import pytest
from fastapi import Response
from jose import jwt
from mock import patch

from backend.api.utils import (
    create_token,
    generate_code_verification_token,
    generate_random_code,
    send_email,
    send_verification_email,
)
from backend.core.configs import settings
from backend.core.security import decode_jwt
from backend.tests.utils.utils import get_token_from_link, random_email


def test_generate_random_code():
    res1 = generate_random_code()
    assert len(res1) == 4

    res2 = generate_random_code(size=14)
    assert len(res2) == 14


def test_create_token_with_fastapi_response():
    email = random_email()
    data = {"email": email, "sub": "login"}
    fa_response = Response(status_code=200)

    result = create_token(data=data, response=fa_response, expire_minute=5)
    assert result.token_type == "bearer"
    assert isinstance(result.access_token, str)


def test_generate_code_verification_token():
    code = generate_random_code()
    email = random_email()
    result = generate_code_verification_token(code=code, email=email)

    assert isinstance(result, str)
    assert len(result.split(".")) == 3  # JWT token format


@patch("emails.Message")
def test_send_mail_emails_not_enabled(mock_sendmail):
    """
    If environment variable EMAILS ENABLED is false, the validation mail should not be send to the user
    """
    email = random_email()
    subject = "Test mail Email Not Enabled"
    html = "<html>TEST MAIL K.O </html>"

    settings.EMAILS_ENABLED = False
    settings.SMTP_HOST = "localhost"
    settings.SMTP_USERNAME = "testuser"
    settings.SMTP_PASSWORD = "TestUserp_W"

    assert not settings.EMAILS_ENABLED

    instance = mock_sendmail.return_value
    instance.send.side_effect = NotImplementedError({})

    # Check raises and exception when sending the message
    with pytest.raises(NotImplementedError) as errmsg:
        send_email(
            email_to=email,
            html_template=html,
            subject_template=subject,
            environment={},
        )
    assert "no provided configuration" in str(errmsg.value)


@patch("emails.Message")
def test_send_mail_emails_enabled_without_smtp_server(mock_sendmail):
    """
    Case we enable sending email, but don't set SMTP server config. Here we only check the server host
    """

    email = random_email()
    subject = "Test mail Email Enabled Without SMTP serveur host"
    html = "<html>TEST MAIL K.O </html>"

    settings.EMAILS_ENABLED = True
    settings.SMTP_HOST = ""

    assert settings.EMAILS_ENABLED

    instance = mock_sendmail.return_value
    instance.send.side_effect = ValueError({})

    # Check raises and exception when sending the message
    with pytest.raises(ValueError) as errmsg:
        send_email(
            email_to=email,
            html_template=html,
            subject_template=subject,
            environment={},
        )
    assert "Invalid SMTP" in str(errmsg.value)


@patch("emails.Message")
def test_send_mail_emails_enabled(mock_sendmail):
    email = random_email()
    subject = "Test mail Email Enabled"
    html = "<html>TEST MAIL OK</html>"

    settings.EMAILS_ENABLED = True
    settings.SMTP_HOST = "localhost"
    settings.SMTP_USERNAME = "testuser"
    settings.SMTP_PASSWORD = "TestUserp_W"

    assert settings.EMAILS_ENABLED

    send_email(
        email_to=email,
        html_template=html,
        subject_template=subject,
        environment={},  # Set default value of test_smtp server
    )
    instance = mock_sendmail.return_value

    assert instance.send.called
    assert instance.send.call_count == 1


@patch("emails.Message")
def test_send_verification_email(mock_sendmail):

    settings.EMAILS_ENABLED = True
    settings.SMTP_HOST = "localhost"
    settings.SMTP_USERNAME = "testuser"
    settings.SMTP_PASSWORD = "TestUserp_W"

    assert settings.EMAILS_ENABLED

    verif_code = generate_random_code()
    email = random_email()

    result = send_verification_email(email_to=email, verification_code=verif_code)
    instance = mock_sendmail.return_value

    assert instance.send.called
    assert instance.send.call_count == 1
    # Return a JWT
    assert isinstance(result, str)
    assert len(result.split(".")) == 3


@patch("emails.Message")
def test_check_verify_code_token(mock_sendmail):
    """
    In this test, we will send a verification email which a JWT,
    and then, used the function check_verify_mode_token to ensure that
    the given token is equal to the verify code
    """

    settings.EMAILS_ENABLED = True
    settings.SMTP_HOST = "localhost"
    settings.SMTP_USERNAME = "testuser"
    settings.SMTP_PASSWORD = "TestUserp_W"

    assert settings.EMAILS_ENABLED

    verif_code = generate_random_code()
    email = random_email()

    result_link = send_verification_email(email_to=email, verification_code=verif_code)
    instance = mock_sendmail.return_value

    assert instance.send.called
    assert isinstance(result_link, str)

    token_from_link = get_token_from_link(result_link)
    assert len(token_from_link.split(".")) == 3

    token_data = decode_jwt(token_from_link)

    assert token_data.get("sub") == verif_code


@pytest.mark.skip
@patch("emails.Message")
def test_check_verify_code_token_expired(mock_sendmail):  # FIXME

    settings.EMAILS_ENABLED = True
    settings.SMTP_HOST = "localhost"
    settings.SMTP_USERNAME = "testuser"
    settings.SMTP_PASSWORD = "TestUserp_W"
    settings.JWT_EMAIL_TOKEN_EXPIRE_MINUTES = 0.1

    assert settings.EMAILS_ENABLED

    verif_code = generate_random_code()
    email = random_email()

    result_link = send_verification_email(email_to=email, verification_code=verif_code)
    instance = mock_sendmail.return_value

    assert instance.send.called
    assert isinstance(result_link, str)

    # Check raises and exception when sending the message

    instance = mock_sendmail.return_value
    instance.send.side_effect = jwt.JWTError({})

    token_from_link = get_token_from_link(result_link)
    assert len(token_from_link.split(".")) == 3

    with pytest.raises(jwt.JWTError) as errmsg:
        decode_jwt(token_from_link)

    assert "Signature has expired" in str(errmsg.value)


@patch("emails.Message")
def test_check_verify_code_token_bad_token(mock_sendmail):

    fake_token = jwt.encode({"test": "dailymotion"}, "secret", algorithm="HS256")
    instance = mock_sendmail.return_value
    instance.send.side_effect = jwt.ExpiredSignatureError({})

    with pytest.raises(jwt.JWTError) as errmsg:
        decode_jwt(fake_token)

    assert "Signature verification failed" in str(errmsg.value)
