import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.string import StrOutputParser

def format_data_for_openai(diffs, linked_issues):

    # Combine the changes into a string with clear delineation.

    combined_diffs = "\n".join([
        f"File: {file['filename']}\nDiff: \n{file['patch']}\n"
        for file in diffs
    ])+"\n\n"

    # Combine all linked issues
    combined_linked_issues = "\n".join(linked_issues)+"\n\n"

    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Check the provided code changes against the requirements in the issues.\n"
        "Provide your feedback in Markdown format. Your feedback should include the following sections:\n"
        "## Overview of the changes\n"
        "In this section, you summarize the changes using no more than 3 sentences.\n"
        "## Core changes\n"
        "In this section, you explain the core part of the changes with references to the issues that might be closed by the code changes (if there are such issues). Use no more than 3 sentences.\n"
        "## How the changes address the issues\n"
        "In this section, for each issues which might be closed by the code changes, explain how the changes address that issue. Keep the text concise and straight to the point. If there is only 1 issue which might be closed by the code changes, do not mention or link to that issue.\n"
        "## Grading\n"
        "In this section, you give a score from 0 to 10 for the code changes. 10 means the changes have fulfilled all requirements, and the code is good. 0 means the changes are absolute garbage.\n"
        "-------------------------------------------------------------------------------------\n"
        "Code changes:\n"
        f"{combined_diffs}\n"
        "-------------------------------------------------------------------------------------\n"
        "Issues which might be closed by the code changes:\n"
        f"{combined_linked_issues}\n"
        "-------------------------------------------------------------------------------------\n"
    )
    return prompt

def construct_improvement_prompt(diffs):

    # Combine the changes into a string with clear delineation.

    combined_diffs = "\n".join([
        f"File: {file['filename']}\nDiff: \n{file['patch']}\n"
        for file in diffs
    ])+"\n\n"

    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Check the provided code changes suggest how they can be improved.\n"
        "Provide your feedback in Markdown format. Your feedback should include the following sections:\n"
        "## Improvement suggestions\n"
        "In this section, you suggest a few ideas to improve the quality of the code.\n"
        "-------------------------------------------------------------------------------------\n"
        "Code changes:\n"
        f"{combined_diffs}\n"
    )
    return prompt

def call_openai(prompt):
    client = ChatOpenAI(api_key = os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo")
    messages = [
        {"role": "system", "content": "You are a developer trained in updating README files from pull request messages"},
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.invoke(input=messages)
        parser = StrOutputParser()
        content = parser.invoke(input=response)
        return content
    except Exception as e:
        return f"An error occurred: {e}"
