Feature: Homepage
    Enable the user to click on any one post title and navigate to a page dedicated to that single post.

Scenario: Click an entry title 
    Given I want to have a permalink for each journal entry
    When I click each journal entry title
    Then I am directed to a detail page for only that entry

Scenario: Click on the edit button
    Given I want to edit my entry
    When I click on the edit button
    Then I can update or fix my entry

Scenario: View entries with formatted markdown
    Given I want to display my entries
    And use Markdown to decorate entry text
    When I load my entries
    Then I can view them formatted nicely

Scenario: View code block entries with syntax highlighting
    Given I want to see colorized code samples in my entries
    When I have entered code samples
    Then I can more easily understand them
