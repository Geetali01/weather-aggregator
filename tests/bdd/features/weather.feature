Feature: Weather aggregation
  As a user of the Weather Aggregator
  I want to fetch and review weather readings for cities
  So that I can track conditions over time

  Background:
    Given the weather aggregator app is running with a stubbed weather provider

  Scenario: Fetching weather for a known city stores a reading
    Given Open-Meteo has current weather data for "Timisoara"
    When I request the current weather for "Timisoara"
    Then the response should be successful
    And the stored reading should show the city "Timisoara"

  Scenario: Viewing history after multiple fetches
    Given Open-Meteo has current weather data for "Cluj"
    And I have already fetched the weather for "Cluj" once
    When I request the current weather for "Cluj" again
    And I view the weather history for "Cluj"
    Then the history should contain 2 readings

  Scenario: Fetching weather for an unknown city fails gracefully
    Given Open-Meteo has no data for "Atlantis"
    When I request the current weather for "Atlantis"
    Then the response should indicate the city was not found