import os
from github import Github
from utils import *
from constants import *
from fetch_linked_issues import *
from fetch_relevant_documents import *

def main():
    # Initialize GitHub API with token
    g = Github(os.getenv('GITHUB_TOKEN'))

    # Get the repo path and PR number from the environment variables
    repo_path = os.getenv('REPO_PATH')
    pull_request_number = int(os.getenv('PR_NUMBER'))
    
    # Get the repo object
    repo = g.get_repo(repo_path)

    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

    # Get all comments on the pull request
    comments = pull_request.get_issue_comments()

    # Filter comments by the unique string and delete them
    for comment in comments:
        if UNIQUE_STRING in comment.body:
            print(f"Deleting comment {comment.id} containing the unique string")
            comment.delete()

    linked_issues = fetch_linked_issues()

    if len(linked_issues) == 0:
        comment = pull_request.create_issue_comment(f"{UNIQUE_STRING}\nThere are no linked issues. Auto-review can't be done.")
        print("Comment created with ID:", comment.id)
        return

    # Get the diffs of the pull request
    pull_request_diffs = [
        {
            "filename": file.filename,
            "patch": file.patch 
        } 
        for file in pull_request.get_files()
    ]

    # Get the relevant documents
    relevant_documents = fetch_relevant_documents(linked_issues)

    # Format data for OpenAI prompt
    prompt = format_data_for_openai(pull_request_diffs, linked_issues, relevant_documents)

    # Call OpenAI to generate the review
    generated_review = call_openai(prompt)
    
    # Write a comment on the pull request
    comment = pull_request.create_issue_comment(f"{UNIQUE_STRING}\n{generated_review}")
    print("Comment created with ID:", comment.id)

if __name__ == '__main__':
    main()
