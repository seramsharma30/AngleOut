import googleapiclient.discovery
import google.oauth2.credentials
from app.routes.gsc_api_auth import API_SERVICE_NAME, API_VERSION




def get_site_urls(search_console_service):
    

    # Retrieve the list of properties from Google Search Console
    site_list = search_console_service.sites().list().execute()
    try:
        site_list = site_list["siteEntry"]
    except Exception as e:
        return "<h1>Please add Projects to your search console.</h1>"
    
    site_list_sorted = [site["siteUrl"] for site in site_list  if site['permissionLevel'] != 'siteUnverifiedUser']
    site_list_sorted = sorted(site_list_sorted)

    return site_list_sorted

