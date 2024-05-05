import requests
import os

def fetch_linked_issues():
  # The GitHub personal access token
  headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}

  # The GraphQL query
  query = """
  query($owner: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
      pullRequest(number: $number) {
        closingIssuesReferences(first: 10) {
          nodes {
            number
            title
            body
            url
          }
        }
      }
    }
  }
  """

  # Variables for the query
  variables = {
      "owner": os.getenv('REPO_OWNER'),
      "name": os.getenv('REPO_NAME'),
      "number": int(os.getenv('PR_NUMBER'))
  }

  # Make the request to the GitHub GraphQL API
  response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)

  # Parse the response
  data = response.json()

  # Extract the linked issues
  linked_issues = data['data']['repository']['pullRequest']['closingIssuesReferences']['nodes']

  results = [
      f"Issue: [{issue['number']}: {issue['title']}]({issue['url']})\nContent: {issue['body']}"
      for issue in linked_issues
  ]
  
  return results
