import argparse
import os
import sys

from django.shortcuts import render
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from .utils import ClientConfigBuilder

# Create your views here.

def generate_refresh_token(request):
  # Your OAuth2 Client ID and Secret. If you do not have an ID and Secret yet,
  # please go to https://console.developers.google.com and create a set.
  client_id = os.getenv('CLIENT_ID', None)
  client_secret = os.getenv('CLIENT_SECRET', None)

  # The AdWords API OAuth2 scope.
  SCOPE = u'https://www.googleapis.com/auth/adwords'

  # The redirect URI set for the given Client ID. The redirect URI for Client ID
  # generated for an installed application will always have this value.
  redirect_uri = os.getenv('REDIRECT_URI', 'urn:ietf:wg:oauth:2.0:oob')

  if not client_id or not client_secret:
    raise AttributeError('No client_id or client_secret specified.')

  """Retrieve and display the access and refresh token."""
  client_config = ClientConfigBuilder(
      client_type=ClientConfigBuilder.CLIENT_TYPE_WEB, client_id=client_id,
      client_secret=client_secret)

  flow = InstalledAppFlow.from_client_config(
      client_config.Build(), scopes=[SCOPE])
  # Note that from_client_config will not produce a flow with the
  # redirect_uris (if any) set in the client_config. This must be set
  # separately.
  flow.redirect_uri = redirect_uri

  auth_url, _ = flow.authorization_url(prompt='consent')

  ctx = {
    'auth_url': auth_url
  }

  code = request.GET.get('code', None)
  
  if code:
    try:
      flow.fetch_token(code=code)
      ctx.update({
        'refresh_token': flow.credentials.refresh_token
      })
    except InvalidGrantError as ex:
      print('Authentication has failed: %s' % ex)
      sys.exit(1)

  return render(request, 'generate_refresh_token.html', ctx)