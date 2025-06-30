Feature: Automated Test Case Generation and JIRA Integration

  Scenario: Fetch user story description from JIRA
    Given a valid JIRA issue key is provided
    When the system fetches the user story from JIRA
    Then the user story description should be retrieved successfully

  Scenario: Generate test cases in mock mode
    Given a user story description is available
    When the system generates test cases in mock mode
    Then the system should return a predefined set of test cases

  Scenario: Generate test cases in real mode using OpenAI
    Given a user story description is available
    When the system generates test cases in real mode
    Then the system should use the OpenAI API to generate Gherkin-style test cases

  Scenario: Add generated test cases as a comment to the JIRA issue
    Given test cases have been generated
    When the system adds them as a comment to the JIRA issue
    Then the comment should be successfully added and the user should be notified

  Scenario: Handle invalid or missing JIRA issue key
    Given an invalid or missing JIRA issue key is provided
    When the system attempts to fetch the user story
    Then the system should return an error indicating the issue key is invalid or not found 