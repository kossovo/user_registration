import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict

import six

from core.configs import settings

mail_config = {
    "username": settings.MAIL_USERNAME,
    "password": settings.MAIL_PASSWORD,
    "from": settings.MAIL_FROM,
    "port": settings.MAIL_PORT,
    "host": settings.MAIL_SERVER,
    "from_name": settings.MAIL_FROM_NAME,
    "ssl": settings.MAIL_SSL,
    "tls": settings.MAIL_TLS,
    "credentials": settings.USE_CREDENTIALS,
}


def _string_or_list(obj):
    """
    If obj is a string, it's converted to a single element list, otherwise
    it's just returned as-is under the assumption that it's already a list. No
    further type checking is performed.
    """

    if isinstance(obj, six.string_types):
        return [obj]
    else:
        return obj


def sendmail(
    mailto: str = None,
    subject: str = None,
    message: str = None,
    subtype: str = "html",
    charset: str = "utf-8",
    smtpconfig: Dict = mail_config,
    attachments: Dict = {},
    use_starttls: bool = False,
    **headers
):

    # TODO: write me
    """
    Send an email to the given address. Additional SMTP headers may be specified
    as keyword arguments.

    Args:
        mailto (str or ): _description_
        subject (_type_): _description_
        message (_type_): _description_
        subtype (str, optional): _description_. Defaults to 'html'.
        charset (str, optional): _description_. Defaults to 'utf-8'.
        smtpconfig (str, optional): _description_. Defaults to "smtp".
        attachments (dict, optional): _description_. Defaults to {}.
        use_starttls (bool, optional): _description_. Defaults to False.
    """

    # mailto arg is explicit to ensure that it's always set, but it's processed
    # mostly the same way as all other headers
    headers["To"] = _string_or_list(mailto)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    for key, value in six.iteritems(headers):
        for val in _string_or_list(value):
            msg.add_header(key, val)

    text = MIMEText(message, subtype, charset)
    msg.attach(text)

    # Add attachments
    for file_name, file_payload in attachments.items():
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file_payload.encode(charset))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", 'attachment; filename="%s"' % file_name)
        msg.attach(part)

    if not "From" in msg:
        msg["From"] = smtpconfig.get("from")
    mailfrom = msg["From"]
    assert isinstance(mailfrom, six.string_types)

    recipients = []
    for toheader in ("To", "CC", "BCC"):
        recipients += msg.get_all(toheader, [])
    if "BCC" in msg:
        del msg["BCC"]

    smtp = smtplib.SMTP(smtpconfig.get("host"), smtpconfig.get("port"))
    if (
        smtpconfig.get("username", None) is not None
        and smtpconfig.get("password", None) is not None
    ):
        if use_starttls:
            smtp.elho()
            smtp.starttls()
            smtp.elho()
        smtp.login(smtpconfig.get("username"), smtpconfig.get("password"))
    smtp.sendmail(mailfrom, recipients, msg.as_string())
    smtp.quit()
    logging.info("Sent email to %s (Subject: %s)", recipients, subject)
