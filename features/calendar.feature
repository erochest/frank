Feature: As a SLab staff-person
  I want to be able to track consultations that are on my calendar

  Scenario: Identifies the sender of the invitation
    Given Frank is alive
    When I send him a meeting invitation
    And I visit the invitation's page
    Then I should see my consultation

  Scenario: Identifies the duration of the consultation
    Given Frank is alive
    When I send him a meeting invitation
    And I visit the invitation's page
    Then I should see the duration of the consultation

  Scenario: Identifies the date of the consultation
    Given Frank is alive
    When I send him a meeting invitation
    And I visit the invitation's page
    Then I should see the date of the consultation

  Scenario: Identifies the other attendees
    Given Frank is alive
    When I send him a meeting invitation
    And I visit the invitation's page
    Then I should see the other attendees of the consultation

  Scenario Outline: Identifies attendees in the invitation title
    Given Frank is alive
    When I send him a meeting invitation with <userid> in the title
    And I visit the invitation's page
    Then I should see <userid> as an attendee

  Examples: User IDs
      | userid |
      | bmw9t  |

  Scenario Outline: Identifies attendees in the invitation body
    Given Frank is alive
    When I send him a meeting invitation with <userid> in the body
    Then I should see <userid> as an attendee

  Examples: User IDs
      | userid |
      | bmw9t  |

  Scenario: Doesn't confuse the sender as an attendee
    Given Frank is alive
    When I send him a meeting invitation as err8n
    Then I should not see err8n as an attendee
    And I should see err8n as the consultant

  Scenario: Identifies meetings that have occurred
    Given Frank is alive
    When I send him a meeting invitation for yesterday
    And I visit the invitation's page
    Then I should see that the invitation is complete
    And I should see a link to a consultation

  Scenario: Identifies meetings that are in the future
    Given Frank is alive
    When I send him a meeting invitation for tomorrow
    And I visit the invitation's page
    Then I should see that the invitation is pending
    And I should not see a link to a consultation
