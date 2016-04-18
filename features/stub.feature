Feature: As a site user,
  I want to access my site

Scenario: Access the site
    Given Frank is alive
    When I visit the site
    Then I should see "It's alive!"
