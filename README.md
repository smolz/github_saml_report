# Github_SAML_Query
Python script that will query the GitHub GraphQL API and pull the GitHub username and SAML account.
This script will build a simple HTML page that will display a table showing the usernames and email addresses.

This script relies on a config.ini file.  Rename the sample_config.ini to config.ini and replace the values with your own.

## config.ini variables:

- github_api_token = This is a personal access token with read access to the admin:org scope.
- github_org = Your GitHub organization, typically what is after the github.com in the url (e.g. https://github.com/MyAwesomeOrg) <--MyAwesomeOrg in this case.
- HTML_HEADER = Just what is displayed on above the table, can be anything you want