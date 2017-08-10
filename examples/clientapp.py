# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016, 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


r"""Minimal client application to register.

SPHINX-START

Install and run the application server (see `app.py` for the instructions).

Open the admin page to register the application:

.. code-block:: console

    $ open http://localhost:5000/account/settings/applications/clients/new/

Login with the following credentials:

    email = clientapp@inveniosoftware.org
    password = 123456

Insert the following data:

    Name = My example app
    Description = The description you want
    Website URL = http://localhost:5001/
    Redirect URIs = http://localhost:5001/login/authorized
    Client Type = Confidential

After the application is successfully created, you will have available the
following information: ClientID and Client Secret.

Logout from the server with:

    $ open http://localhost:5000/logout

Open a new console and export the following variable in the console:

    $ cd examples
    $ export CLIENTAPP_CONSUMER_KEY=TheGeneratedClientID
    $ export CLIENTAPP_CONSUMER_SECRET=TheGeneratedClientSecret
    $ export FLASK_APP=clientapp.py

Run the client application with:

    $ OAUTHLIB_INSECURE_TRANSPORT=1 flask run -p 5001 --with-threads

Open the homepage:

    $ open http://localhost:5001/

You will be redirected to redirected to login:

    email = reader@inveniosoftware.org
    password = 123456

And then, you can authorize you application.

After the registration is terminated, you can open the admin page to see
the list of application authorized and have the possibility to revoke
permissions:

    $ open http://localhost:5000/account/settings/applications/

SPHINX-END
"""

import os

from flask import Flask, jsonify, redirect, request, session, url_for
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

myapp = oauth.remote_app(
    'clientapp',
    consumer_key=os.environ.get('CLIENTAPP_CONSUMER_KEY'),
    consumer_secret=os.environ.get('CLIENTAPP_CONSUMER_SECRET'),
    request_token_params={'scope': 'test:scope'},
    base_url='http://localhost:5000/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='http://localhost:5000/oauth/token',
    authorize_url='http://localhost:5000/oauth/authorize',
)


@app.route('/')
def index():
    """Index page."""
    if 'myapp_token' in session:
        me = myapp.get('oauth/info')
        return jsonify(me.data)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Login."""
    return myapp.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    """Logout."""
    session.pop('myapp_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    """Authorize application."""
    resp = myapp.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['myapp_token'] = (resp['access_token'], '')
    return jsonify(resp)


@myapp.tokengetter
def get_my_oauth_token():
    """Get my token."""
    return session.get('myapp_token')


if __name__ == '__main__':
    app.run()
