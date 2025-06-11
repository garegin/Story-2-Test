MOCK_RESPONSE = '''{
  "Scenarios": [
    {
      "Given": "a user is on the login page",
      "When": "the user clicks on 'Forgot Password' and enters their registered phone number",
      "Then": "an SMS with a reset link is sent to the user's phone"
    },
    {
      "Given": "a user has received an SMS with a reset link",
      "When": "the user clicks on the reset link within 10 minutes",
      "Then": "the link is valid and the user is redirected to the password reset page"
    },
    {
      "Given": "a user has received an SMS with a reset link",
      "When": "the user clicks on the reset link after 10 minutes",
      "Then": "the link is invalid and the user is shown an error message"
    },
    {
      "Given": "a user is on the password reset page with a valid link",
      "When": "the user enters a new password and confirms it",
      "Then": "the password is successfully updated and the user is notified"
    },
    {
      "Given": "a user is on the password reset page with a valid link",
      "When": "the user enters a new password that does not meet the security criteria",
      "Then": "the user is shown an error message indicating the password requirements"
    },
    {
      "Given": "a user is on the password reset page with a valid link",
      "When": "the user enters mismatched passwords in the new password and confirm password fields",
      "Then": "the user is shown an error message indicating the passwords do not match"
    }
  ]
}'''
