Feature: As a SLab staff-person
  I want to be able to track consultations that are on my calendar

  Scenario: Identifies the sender of the invitation
    Given Frank is alive
    When I send him a meeting invitation
    Then he should recognize that I have a consultation

  Scenario: Identifies the duration of the consultation
    Given Frank is alive
    When I send him a meeting invitation
    Then he should scrape the duration of the consultation

  Scenario: Identifies the date of the consultation
    Given Frank is alive
    When I send him a meeting invitation
    Then he should scrape the date of the consultation

  Scenario: Identifies the other attendees
    Given Frank is alive
    When I send him a meeting invitation
    Then he should scrape the other attendees of the consultation

  Scenario Outline: Identifies attendees in the invitation title
    Given Frank is alive
    When I send him a meeting invitation with <userid> in the title
    Then he should scrape <userid> from the title of the invitation

  Examples: User IDs
      | userid |
      | err8n  |

  Scenario Outline: Identifies attendees in the invitation body
    Given Frank is alive
    When I send him a meeting invitation with <userid> in the body
    Then he should scrape <userid> from the body of the invitation

  Examples: User IDs
      | userid |
      | err8n  |

  Scenario: Identifies meetings that have occurred
    Given Frank is alive
    When I send him a meeting invitation for yesterday
    Then he should recognize that the invitation is complete
    And he should create a meeting for the invitation

  Scenario: Identifies meetings that are in the future
    Given Frank is alive
    When I send him a meeting invitation for tomorrow
    Then he should recognize that the invitation is pending
    And he should not create a meeting for the invitation
