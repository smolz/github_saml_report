# GitHub SAML Query Tool

A Python script that queries the GitHub GraphQL API to retrieve GitHub usernames and their associated SAML email addresses for organizations using SAML SSO authentication.

## Features

- 📊 **Dual Output Formats**: Generates both HTML and CSV reports
- 🔄 **Sortable HTML Table**: Click column headers to sort data
- 🏢 **Multi-Organization Support**: Query multiple GitHub organizations in a single run
- 📱 **Responsive Design**: HTML output works on desktop and mobile devices
- ⚡ **Error Handling**: Comprehensive error messages and validation
- 📁 **Organized Output**: Reports saved to `Reports/` subdirectory with timestamps
- 📅 **Historical Tracking**: Timestamped filenames preserve report history

## Prerequisites

- Python 3.6 or higher
- GitHub organization with SAML SSO enabled
- GitHub Personal Access Token with appropriate permissions

### Required Python Packages

```bash
pip install requests arrow
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Setup

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/Github_SAML_Query.git
cd Github_SAML_Query
```

### 2. Create Configuration File

Rename `sample_config.ini` to `config.ini`:

```bash
cp sample_config.ini config.ini
```

### 3. Configure Settings

Edit `config.ini` with your specific values:

```ini
[configuration]
github_api_token = ghp_your_token_here
github_org = MyOrg1,MyOrg2
HTML_HEADER = GitHub Accounts in
```

#### Configuration Parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `github_api_token` | Personal Access Token with `read:org` and `admin:org` scopes | `ghp_xxxxxxxxxxxx` |
| `github_org` | GitHub organization name(s). For multiple orgs, separate with commas | `MyOrg` or `MyOrg1,MyOrg2,MyOrg3` |
| `HTML_HEADER` | Text displayed at the top of the HTML report | `GitHub Accounts in` |

### 4. Create a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "SAML Query Script")
4. Select the following scopes:
   - `read:org` - Read org and team membership
   - `admin:org` - Full control of orgs (needed for SAML data)
5. Click "Generate token"
6. Copy the token immediately and paste it into your `config.ini` file

**Note**: The token will only be shown once. Store it securely.

## Usage

Run the script:

```bash
python saml_query.py
```

### Output Files

The script generates two timestamped files in the `Reports/` subdirectory:

1. **`Reports/saml_users_YYYY-MM-DD_HHmmss.html`** - Interactive HTML table with:
   - Sortable columns (click headers to sort)
   - Organization, username, and email data
   - Timestamp of when data was retrieved
   - User count statistics
   - Responsive design for mobile and desktop

2. **`Reports/saml_users_YYYY-MM-DD_HHmmss.csv`** - CSV file with three columns:
   - Organization
   - Username
   - Email Address

**Example filenames:**
- `Reports/saml_users_2025-09-29_143025.html`
- `Reports/saml_users_2025-09-29_143025.csv`

**Note:** The `Reports/` directory is automatically created if it doesn't exist. Each run creates new timestamped files, preserving previous reports for historical tracking.

### Example Output

```
Querying 2 organization(s)...

Fetching users from MyOrg1...
  Found 45 users
Fetching users from MyOrg2...
  Found 23 users

68 total users found

✓ Reports directory ready: Reports/
✓ CSV file created: Reports/saml_users_2025-09-29_143025.csv (68 users)
✓ HTML file created: Reports/saml_users_2025-09-29_143025.html

✓ All files generated successfully!
```

## Project Structure

```
Github_SAML_Query/
├── saml_query.py           # Main script
├── config.ini              # Your configuration (not committed)
├── sample_config.ini       # Configuration template
├── README.md               # This file
├── .gitignore             # Git ignore rules
└── Reports/               # Output directory (auto-created, not committed)
    ├── saml_users_2025-09-29_143025.html
    ├── saml_users_2025-09-29_143025.csv
    └── [previous timestamped reports...]
```

## Troubleshooting

### "No users found" Error

Check the following:
- Verify your API token has the correct permissions (`read:org` and `admin:org`)
- Ensure the organization names are spelled correctly
- Confirm that SAML SSO is enabled for your organization(s)
- Test your token has access to the organization

### "Config file not found" Error

- Ensure `config.ini` exists in the same directory as the script
- Verify the file is named exactly `config.ini` (not `config.ini.txt`)

### API Rate Limiting

GitHub's GraphQL API has rate limits. If you hit the limit:
- Wait for the rate limit to reset (typically one hour)
- Use a token with higher rate limits
- Reduce the number of organizations queried at once

### "Does the organization have SAML enabled?" Error

This error occurs when:
- The organization doesn't have SAML SSO configured
- Your token doesn't have access to the organization
- The organization name is incorrect

## Limitations

- Currently retrieves the first 100 users per organization (GitHub API limit)
- Requires SAML SSO to be enabled on the organization
- Token must have admin-level organization access
- Reports are saved locally; consider implementing automated backup/archival for production use

## Managing Report History

The script creates timestamped reports in the `Reports/` directory. Over time, this can accumulate many files. Consider:

**Manual Cleanup:**
```bash
# View reports sorted by date
ls -lt Reports/

# Remove reports older than 30 days (Linux/macOS)
find Reports/ -name "saml_users_*.html" -mtime +30 -delete
find Reports/ -name "saml_users_*.csv" -mtime +30 -delete
```

**Automated Archival:**
```bash
# Create monthly archives
tar -czf Reports/archive_$(date +%Y-%m).tar.gz Reports/saml_users_*.html Reports/saml_users_*.csv
```

## Security Notes

- **Never commit `config.ini`** to version control (it's included in `.gitignore`)
- Store your Personal Access Token securely
- Rotate tokens periodically
- Use tokens with minimum required permissions
- Consider using GitHub App authentication for production use

## Author

Chris Smolen - 3820601+smolz@users.noreply.github.com

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

This means you are free to:
- Use this software for any purpose
- Change the software to suit your needs
- Share the software with your friends and neighbors
- Share the changes you make

Under the following terms:
- If you modify and distribute this software, you must make your source code available
- If you run a modified version on a server and let others interact with it, you must share your modifications
- You must include the license and copyright notice with the software
- You must state significant changes made to the software

See the [LICENSE](LICENSE) file for the full license text, or visit [https://www.gnu.org/licenses/agpl-3.0.en.html](https://www.gnu.org/licenses/agpl-3.0.en.html) for more details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.