Feature: As a SLab staff-person
  I want to be able to track consultations that are on my calendar
  So that I can be more aware of my work

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
    And I visit the invitation's page
    Then I should see <userid> as an attendee

  Examples: User IDs
      | userid |
      | bmw9t  |

  Scenario: Doesn't confuse the sender as an attendee
    Given Frank is alive
    When I send him a meeting invitation as err8n
    And I visit the invitation's page
    Then I should not see err8n as an attendee
    And I should see err8n as the meeting owner

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

  Scenario Outline: Identifies recurring meetings
    Given Frank is alive
    When I send him an invitation for a meeting that meets <recurring> at <start_time> for <duration>, starting <start_date>
    And I visit the invitation's page
    Then I should see it marked as recurring

  Examples: Recurring
      | recurring                          | start_time | duration   | start_date |
      | every Friday                       | 4:00 PM    | 30 minutes | 4/29/2016  |
      | every day                          | 2:00 PM    | 30 minutes | 5/10/2016  |
      | every month on day 10 of the month | 2:30 PM    | 30 minutes | 5/10/2016  |
      | every May 10                       | 3:00 PM    | 60 minutes | 5/10/2016  |

# TODO: recurring appointments
# TODO: a job that creates meetings for the previous day
# TODO: a button that creates meetings on demand
