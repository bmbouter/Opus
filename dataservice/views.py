from auth import user_tools
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from vdi.log import log

try: 
  from xml.etree import ElementTree
except ImportError:  
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom

@user_tools.login_required
def meta_feed(request):
    gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    gd_client.email = 'opusdataservices@gmail.com'
    gd_client.password = 'NEXTpassw0rd'
    gd_client.source = 'exampleCo-exampleApp-1'
    gd_client.ProgrammaticLogin()
    feed = gd_client.GetSpreadsheetsFeed()
    PrintFeed(feed)
    return render_to_response('dataservice.html')

def PrintFeed(feed):
  for i, entry in enumerate(feed.entry):
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
      log.debug('%s %s\n' % (entry.title.text, entry.content.text))
    elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
      log.debug('%s %s %s' % (i, entry.title.text, entry.content.text))
      # Print this row's value for each column (the custom dictionary is
      # built from the gsx: elements in the entry.) See the description of
      # gsx elements in the protocol guide.
      log.debug('Contents:')
      for key in entry.custom:
        log.debug('  %s: %s' % (key, entry.custom[key].text))
      log.debug('\n'),
    else:
      log.debug('%s %s\n' % (i, entry.title.text))
