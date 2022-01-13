import json
import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser

CLIENT_SECRETS_FILE = "client_secret.json"

API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_PATH = 'cred.json'

app = flask.Flask(__name__)
api = Api(app)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME'


@app.route('/')
def index():
    return print_index_table()


@app.route('/test')
def test_api_request():
    if not os.path.isfile('./'+CREDENTIALS_PATH):
        return flask.redirect('authorize')

    # Load credentials from the session.
    with open(CREDENTIALS_PATH, 'r') as file:
        credentials_json = json.load(file)
    credentials = google.oauth2.credentials.Credentials(
        # **flask.session['credentials'])
        **credentials_json)
    #
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    calendars_result = service.calendarList().list().execute()

    calendars = calendars_result.get('items', [])
    events = []
    if not calendars:
        events.append('No calendars found.')
    for calendar in calendars:
        summary = calendar['summary']
        id = calendar['id']
        primary = "Primary" if calendar.get('primary') else ""
        events.append("%s\t%s\t%s" % (summary, id, primary))

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    # flask.session['credentials'] = credentials_to_dict(credentials)
    with open(CREDENTIALS_PATH, 'w') as file:
        json.dump(credentials_to_dict(credentials), file)


    return flask.jsonify(*events)


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    # flask.session['credentials'] = credentials_to_dict(credentials)
    with open(CREDENTIALS_PATH, 'w') as file:
        json.dump(credentials_to_dict(credentials), file)

    return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
    # if 'credentials' not in flask.session:
    #     return ('You need to <a href="/authorize">authorize</a> before ' +
    #             'testing the code to revoke credentials.')
    with open(CREDENTIALS_PATH, 'r') as file:
        credentials_json = json.load(file)
    credentials = google.oauth2.credentials.Credentials(
        # **flask.session['credentials']
        **credentials_json
    )

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return ('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    # if 'credentials' in flask.session:
    #     del flask.session['credentials']
    if os.path.isfile('./'+CREDENTIALS_PATH):
        os.remove(CREDENTIALS_PATH)
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


event_parser = RequestParser()
event_parser.add_argument('title')
event_parser.add_argument('date')


class CreateEvent(Resource):
    def post(self):
        if os.path.isfile('./' + CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, 'r') as file:
                credentials_json = json.load(file)
            credentials = google.oauth2.credentials.Credentials(
                **credentials_json)

            service = googleapiclient.discovery.build(
                API_SERVICE_NAME, API_VERSION, credentials=credentials)
            args = event_parser.parse_args()
            service.events().insert(
                calendarId='primary',
                body={
                    'summary': args['title'],
                    'description': args['title'],
                    'start': {'date': args['date']},
                    'end': {'date': args['date']},
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 24 * 60},
                        ],
                    },
                },
                sendUpdates='all'
            ).execute()
            return {'status': 'OK'}
        return {'status': 'Fail'}, 503


api.add_resource(CreateEvent, '/create_event')


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored locally. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run('localhost', 8080, debug=True)
