"""
Chris Smolen - csmolen@eplus.com

Python script that will query the GitHub GraphQL API and pull the GitHub username and SAML account.
This script will build a simple HTML page that will display a sortable table showing the usernames 
and email addresses, and also export the data to CSV.
"""

import requests
import configparser
import arrow
import csv
import sys
import os
from pathlib import Path
from typing import List, Dict


def load_config(config_path: str = "./config.ini") -> configparser.ConfigParser:
    """Load configuration from INI file."""
    config = configparser.ConfigParser()
    if not config.read(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    return config


def get_saml_users(org: str, token: str) -> Dict:
    """
    Query GitHub GraphQL API for SAML users in an organization.
    
    Args:
        org: GitHub organization name
        token: GitHub API token
        
    Returns:
        Dict containing the API response
        
    Raises:
        requests.RequestException: If API request fails
    """
    query = '''
    query($org: String!) {
        organization(login: $org) {
            samlIdentityProvider {
                ssoUrl
                externalIdentities(first: 100) {
                    edges {
                        node {
                            guid
                            samlIdentity {
                                nameId
                            }
                            user {
                                login
                            }
                        }
                    }
                }
            }
        }
    }
    '''
    
    headers = {'Authorization': f'bearer {token}'}
    variables = {'org': org}
    
    response = requests.post(
        'https://api.github.com/graphql',
        headers=headers,
        json={'query': query, 'variables': variables},
        timeout=30
    )
    response.raise_for_status()
    
    return response.json()


def extract_users(api_response: Dict, org: str) -> List[Dict[str, str]]:
    """
    Extract user information from API response.
    
    Args:
        api_response: GitHub API response
        org: Organization name
        
    Returns:
        List of user dictionaries
    """
    users = []
    
    try:
        edges = api_response['data']['organization']['samlIdentityProvider']['externalIdentities']['edges']
        
        for edge in edges:
            node = edge['node']
            users.append({
                'org': org,
                'username': node['user']['login'],
                'email': node['samlIdentity']['nameId']
            })
    except (KeyError, TypeError) as e:
        print(f"Warning: Could not parse users for {org}. Error: {e}")
    
    return users


def write_csv(users: List[Dict[str, str]], filename: str) -> None:
    """Write user data to CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Organization', 'Username', 'Email Address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for user in users:
            writer.writerow({
                'Organization': user['org'],
                'Username': user['username'],
                'Email Address': user['email']
            })
    
    print(f"✓ CSV file created: {filename} ({len(users)} users)")


def write_html(users: List[Dict[str, str]], title: str, timestamp: str, filename: str) -> None:
    """Write user data to sortable HTML file."""
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .stats {{
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th {{
            background-color: #90EE90;
            padding: 12px;
            text-align: left;
            cursor: pointer;
            user-select: none;
            font-weight: 600;
            position: relative;
        }}
        th:hover {{
            background-color: #7CCD7C;
        }}
        th::after {{
            content: ' ⇅';
            font-size: 0.8em;
            color: #666;
            opacity: 0.5;
        }}
        th.sorted-asc::after {{
            content: ' ▲';
            opacity: 1;
        }}
        th.sorted-desc::after {{
            content: ' ▼';
            opacity: 1;
        }}
        td {{
            background-color: #f9f9f9;
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover td {{
            background-color: #f0f0f0;
        }}
        tr:nth-child(even) td {{
            background-color: #fafafa;
        }}
        tr:nth-child(even):hover td {{
            background-color: #f0f0f0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            body {{
                margin: 10px;
            }}
            .container {{
                padding: 15px;
            }}
            table {{
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>{title}</h2>
        <div class="stats">Total users: {count}</div>
        <table id="userTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Organization</th>
                    <th onclick="sortTable(1)">Username</th>
                    <th onclick="sortTable(2)">Email Address</th>
                </tr>
            </thead>
            <tbody>
{rows}
            </tbody>
        </table>
        <div class="footer">
            <p><strong>Last updated:</strong> {timestamp}</p>
            <p><strong>Report files:</strong> saml_users_{file_timestamp}.csv / saml_users_{file_timestamp}.html</p>
        </div>
    </div>
    
    <script>
        let currentSort = {{ column: -1, direction: 'asc' }};
        
        function sortTable(columnIndex) {{
            const table = document.getElementById("userTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            const headers = table.querySelectorAll("th");
            
            // Determine sort direction
            let direction = 'asc';
            if (currentSort.column === columnIndex && currentSort.direction === 'asc') {{
                direction = 'desc';
            }}
            
            // Sort rows
            rows.sort((a, b) => {{
                const aText = a.cells[columnIndex].textContent.trim().toLowerCase();
                const bText = b.cells[columnIndex].textContent.trim().toLowerCase();
                
                const comparison = aText.localeCompare(bText);
                return direction === 'asc' ? comparison : -comparison;
            }});
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
            
            // Update header classes
            headers.forEach(header => {{
                header.classList.remove('sorted-asc', 'sorted-desc');
            }});
            headers[columnIndex].classList.add(`sorted-${{direction}}`);
            
            // Store current sort
            currentSort = {{ column: columnIndex, direction: direction }};
        }}
    </script>
</body>
</html>
'''
    
    rows_html = '\n'.join(
        f'                <tr><td>{user["org"]}</td><td>{user["username"]}</td><td>{user["email"]}</td></tr>'
        for user in users
    )
    
    # Extract just the filename timestamp for display
    file_timestamp = Path(filename).stem.replace('saml_users_', '')
    
    html_content = html_template.format(
        title=title,
        count=len(users),
        rows=rows_html,
        timestamp=timestamp,
        file_timestamp=file_timestamp
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML file created: {filename}")


def main():
    """Main execution function."""
    try:
        # Load configuration
        config = load_config()
        token = config.get('configuration', 'github_api_token')
        org_string = config.get('configuration', 'github_org')
        html_header = config.get('configuration', 'HTML_HEADER')
        
        organizations = [org.strip() for org in org_string.split(',')]
        
        print(f"Querying {len(organizations)} organization(s)...\n")
        
        # Collect all users
        all_users = []
        for org in organizations:
            print(f"Fetching users from {org}...")
            try:
                response = get_saml_users(org, token)
                users = extract_users(response, org)
                all_users.extend(users)
                print(f"  Found {len(users)} users")
            except requests.RequestException as e:
                print(f"  Error fetching data: {e}")
            except Exception as e:
                print(f"  Unexpected error: {e}")
        
        if not all_users:
            print("\nNo users found. Please check:")
            print("  - API token has correct permissions")
            print("  - Organizations have SAML enabled")
            print("  - Organization names are correct")
            sys.exit(1)
        
        print(f"\n{len(all_users)} total users found\n")
        
        # Create Reports directory if it doesn't exist
        reports_dir = Path("Reports")
        reports_dir.mkdir(exist_ok=True)
        print(f"✓ Reports directory ready: {reports_dir}/\n")
        
        # Generate timestamp for filenames and display
        local_time = arrow.utcnow().to('US/Eastern')
        timestamp_display = local_time.format('MM-DD-YYYY HH:mm:ss')
        timestamp_file = local_time.format('YYYY-MM-DD_HHmmss')
        
        # Create filenames with timestamp
        csv_filename = reports_dir / f"saml_users_{timestamp_file}.csv"
        html_filename = reports_dir / f"saml_users_{timestamp_file}.html"
        
        # Write outputs
        write_csv(all_users, str(csv_filename))
        
        org_names = ', '.join(organizations)
        title = f"{html_header} {org_names} with SSO account information"
        write_html(all_users, title, timestamp_display, str(html_filename))
        
        print("\n✓ All files generated successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except configparser.Error as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()