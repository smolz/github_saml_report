"""
Chris Smolen - csmolen@eplus.com

Python script that will query the GitHub GraphQL API and pull the GitHub username and SAML account.
This script will build a simple HTML page that will display a table showing the usernames and email addresses.
"""


import requests
import configparser
import arrow


utc = arrow.utcnow()
local = utc.to('US/Eastern')

config = configparser.ConfigParser()
config.read("./config.ini")

TOKEN = config.get('configuration', 'github_api_token')
ORGS = config.get('configuration', 'github_org')
ORG = ORGS.split(',')
file = open('saml_users.html', 'w')
file.close()


def get_saml_users(org):
    global TOKEN

    query = 'query {organization(login: \"' + org + '\") {samlIdentityProvider{ssoUrl externalIdentities(first: 100) ' \
            '{edges{node{guid samlIdentity {nameId} user {login}}}}}}}'

    headers = {'Authorization': 'bearer {token}'.format(token=TOKEN)}

    r = requests.post('https://api.github.com/graphql', headers=headers, json={'query': query})

    org_users = r.json()
    return org_users


try:
    for org in ORG:
        users = get_saml_users(org)
        TITLE = config.get('configuration', 'HTML_HEADER') + " {} with SSO account information".format(org)
        with open('saml_users.html', 'a') as s:
            s.write('<HTML>\n')
            s.write('<H2>{}</H2>\n'.format(TITLE))
            s.write('<TABLE border=0>\n')
            s.write('<TR><TD bgcolor="LightGreen">USERNAME</TD><TD bgcolor="LightGreen">EMAIL ADDRESS</TD></TR>\n')
            for edge in users['data']['organization']['samlIdentityProvider']['externalIdentities']['edges']:
                print(edge['node']['user']['login'], edge['node']['samlIdentity']['nameId'])

                s.write('<TR><TD bgcolor=\"#D3D3D3\">' + edge['node']['user']['login'] + '</TD><TD bgcolor=\"#D3D3D3\">' +
                        edge['node']['samlIdentity']['nameId'] + '</TD></TR>\n')
            s.write('</TABLE>')
    with open('saml_users.html', 'a') as s:
        s.write('\n<H2>This information updated: {}</H2>'.format(local.format('MM-DD-YYYY HH:mm:ss')))
        s.write('\n</HTML>')

except TypeError as e:
    print("There was an error fetching the data.  Does the organization have SAML enabled?")

