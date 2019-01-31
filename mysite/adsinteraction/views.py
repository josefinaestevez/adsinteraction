import os
import sys

from django.shortcuts import render
from googleads import adwords, oauth2
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from .utils import ClientConfigBuilder
from .custom_decorators import refresh_token

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
    client_secret=client_secret
  )

  flow = InstalledAppFlow.from_client_config(
    client_config.Build(), scopes=[SCOPE]
  )
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
      refresh_token = flow.credentials.refresh_token
      request.session['refresh_token'] = refresh_token
      ctx = {
        'refresh_token': refresh_token
      }
    except InvalidGrantError as ex:
      print('Authentication has failed: %s' % ex)
      sys.exit(1)

  return render(request, 'generate_refresh_token.html', ctx)


@refresh_token
def customers(request):

  client_id = os.getenv('CLIENT_ID', None)
  client_secret = os.getenv('CLIENT_SECRET', None)
  refresh_token = request.session.get('refresh_token')
  developer_token = os.getenv('DEVELOPER_TOKEN', None)

  oauth2_client = oauth2.GoogleRefreshTokenClient(
    client_id,
    client_secret, 
    refresh_token
  )

  # Initialize the AdWords client.
  adwords_client = adwords.AdWordsClient(
      developer_token,
      oauth2_client,
  )

  customer_service = adwords_client.GetService('CustomerService', version='v201809')

  selector = {
      'fields': ['customerId', 'descriptiveName', 'dateTimeZone'],
  }

  customers = customer_service.getCustomers(selector)

  print(customers)

  ctx = {
    'customers': customers
  }

  return render(request, 'customers.html', ctx)


@refresh_token
def campaigns(request, client_customer_id):

  client_id = os.getenv('CLIENT_ID', None)
  client_secret = os.getenv('CLIENT_SECRET', None)
  refresh_token = request.session.get('refresh_token')
  developer_token = os.getenv('DEVELOPER_TOKEN', None)
  
  oauth2_client = oauth2.GoogleRefreshTokenClient(
    client_id,
    client_secret, 
    refresh_token
  )

  # Initialize the AdWords client.
  adwords_client = adwords.AdWordsClient(
      developer_token,
      oauth2_client,
      client_customer_id=client_customer_id
  )

  PAGE_SIZE = 10
  offset = 0

  campaign_service = adwords_client.GetService('CampaignService', version='v201809')

  selector = {
      'fields': ['Id', 'Name', 'Status'],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }

  campaigns = []

  more_pages = True
  while more_pages:
    page = campaign_service.get(selector)

    # Display results.
    if 'entries' in page:
      for campaign in page['entries']:
        print('Campaign with id "%s", name "%s", and status "%s" was '
       'found.' % (campaign['id'], campaign['name'],
                   campaign['status']))
        c = {
          'id': campaign['id'],
          'name': campaign['name'],
          'status': campaign['status']
        }

        campaigns.append(c)
    else:
      print('No campaigns were found.')

    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

    ctx = {
      'campaigns': campaigns
    }

  return render(request, 'campaigns.html', ctx)