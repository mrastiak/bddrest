import cgi
import functools
import json
import tempfile
import unittest

from bddrest.authoring import given, when, then, composer, response, and_
from bddrest.exceptions import InvalidUrlParametersError, CallVerifyError
from bddrest.specification import Call, When
from bddrest.story import Story


def wsgi_application(environ, start_response):
    form = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=environ,
        strict_parsing=False,
        keep_blank_values=True
    )

    try:
        code = int(form['activationCode'].value) ^ 1234
    except ValueError:
        start_response('400 Bad Request', [('Content-Type', 'text/plain;utf-8')])
        return

    start_response('200 OK', [
        ('Content-Type', 'application/json;charset=utf-8'),
        ('X-Pagination-Count', '10')
    ])
    result = json.dumps(dict(
        secret='ABCDEF',
        code=code,
        query=environ['QUERY_STRING']
    ))
    yield result.encode()


class AssertionTestCase(unittest.TestCase):

    def test_equality(self):

        call = dict(
            title='Binding and registering the device after verifying the activation code',
            description=\
                'As a new visitor I have to bind my device with activation code and phone number',
            url='/apiv1/devices/name: SM-12345678',
            verb='POST',
            as_='visitor',
            query=dict(
                a=1,
                b=2
            ),
            form=dict(
                activationCode='746727',
                phone='+9897654321'
            )
        )
        with given(wsgi_application, **call):
            then(
                response.status == '200 OK',
                response.status_code == 200
            )
            when(
                'Trying invalid code',
                form=dict(
                    activationCode='badCode'
                )
            )

            then(response.status_code == 400)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
