Feature: As a site user,
  I want to access my site

Scenario: Access the site
    Given Frank is alive
    When I visit the site
    Then I should see "It's alive!"

Scenario: Access the database
    Given Frank is alive
    When I select the answer from the database
    Then I should get back '42'
