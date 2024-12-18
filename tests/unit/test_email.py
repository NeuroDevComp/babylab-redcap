"""Test email functions
"""

import pytest
from babylab import email


def test_validation():
    """Validate email addresses."""
    try:
        email.check_email_domain("iodsf@sjd.es")
    except (email.MailDomainException, email.MailAddressException) as e:
        pytest.fail(str(e))
    with pytest.raises(email.MailDomainException):
        email.check_email_domain("iodsf@sjd.com")
    with pytest.raises(email.MailAddressException):
        email.check_email_address("iodsf@opdofsn.com")
