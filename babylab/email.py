"""E-mail composing and sending.
"""

import win32com.client as win32
import pythoncom


class MailDomainException(Exception):
    """If e-mail address does not have SJD domain."""

    def __init__(self, email, domain):
        msg = f"E-mail provided '{email}' does not have domain '{domain}'"
        super().__init__(msg)


class MailAddressException(win32.pywintypes.com_error):  # pylint: disable=no-member
    """If e-mail address is not authorized in local Outlook app."""

    def __init__(self, email):
        msg = f"E-mail provided '{email}' is not authorized in local Outlook app'"
        super().__init__(msg)


def check_email_address(email: str):
    """Check if e-mail address is authorized in local Outlook app.

    Args:
        email (str): Email address to check.
    """  # pylint: disable=line-too-long
    pythoncom.CoInitialize()  # pylint: disable=no-member
    ol_app = win32.Dispatch("Outlook.Application")
    ol_ns = ol_app.GetNameSpace("MAPI")
    mail_item = ol_app.CreateItem(0)
    try:
        mail_item._oleobj_.Invoke(  # pylint: disable=protected-access
            *(64209, 0, 8, 0, ol_ns.Accounts.Item(email))
        )
    except win32.pywintypes.com_error as e:  # pylint: disable=no-member
        raise MailAddressException(email) from e


def check_email_domain(email: str, target_domain: str = "sjd.es"):
    """Assert that provided email has certain domain.

    Args:
        email (str): E-mail address provided.
        target_domain (str, optional): Domain to find. Defaults to "sjd.es".

    Raises:
        MailDomainException: If e-mail address does not have target domain.
    """
    email_domain = email.split("@")[1]
    if email_domain != target_domain:
        raise MailDomainException(email, target_domain)


def compose_email(data: dict) -> dict:
    """Compose e-mail subject and body based on data dictionary

    Args:
        data (dict): Appointment and participant data to fill in the subject and body.

    Returns:
        dict: Dictionary with composed HTML subject and body.
    """  # pylint: disable=line-too-long

    data["subject"] = (
        f"Appointment { data['appointment_id'] } ({ data['status'] }) | { data['study'] } (ID: { data['record_id'] }) - { data['date'] }"  # pylint: disable=line-too-long
    )
    data[
        "body"
    ] = f"""
The appointment { data['appointment_id'] } (ID: { data['record_id'] }) from study { data['study'] } has been created or modified. Here are the details:
<br><br>
<table style="width:50%">
    <tbody>
        <tr>
            <td>
                <b>Appointment ID</b>
            </td>
            <td>
                { data['appointment_id'] }
            </td>
        </tr>
        <tr>
            <td>
                <b>Appointment date</b>
            </td>
            <td>
                { data['date'] }
            </td>
        </tr>
        <tr>
            <td>
                <b>Participant ID</b>
            </td>
            <td>
                { data['record_id'] }
            </td>
        </tr>
        <tr>
            <td>
                <b>Current status</b>
            </td>
            <td>
                { data['status'] }
            </td>
        </tr>
        <tr>
            <td>
                <b>Taxi</b>
            </td>
            <td>
                { data['taxi_address'] }
            </td>
        </tr>
        <tr>
            <td>
                <b>Taxi booked?</b>
            </td>
            <td>
                { data['taxi_isbooked'] }
            </td>
        </tr>
        <tr>
            <td>
                <b>Notes</b>
            </td>
            <td>
                { data['comments'] }
            </td>
        </tr>
    </tbody>
    </table>
"""  # pylint: disable="line-too-long"
    return data


def send_email(
    data: dict, email_from="gonzalo.garcia@sjd.es", email_to="gonzalo.garcia@sjd.es"
):
    """Send e-mail using Outlook.

    Args:
        data (dict): Dictionary with the subject, body, and other properties of the e-mail.
        email_from (str, optional): E-mail address to send the e-mail from. Defaults to "gonzalo.garcia@sjd.es".
        email_to (str, optional): E-mail address to send the e-mail to. . Defaults to "gonzalo.garcia@sjd.es".
    """  # pylint: disable=line-too-long
    check_email_domain(email_from)
    check_email_domain(email_to)
    composed = compose_email(data)
    pythoncom.CoInitialize()  # pylint: disable=no-member

    ol_app = win32.Dispatch("Outlook.Application")
    ol_ns = ol_app.GetNameSpace("MAPI")
    mail_item = ol_app.CreateItem(0)
    mail_item.Subject = composed["subject"]
    mail_item.BodyFormat = 1
    mail_item.HTMLBody = composed["body"]
    mail_item.To = email_to
    mail_item._oleobj_.Invoke(  # pylint: disable=protected-access
        *(64209, 0, 8, 0, ol_ns.Accounts.Item(email_from))
    )
    mail_item.Send()
