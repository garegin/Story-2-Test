import json
from json_cleaner import clean_json_string, parse_test_cases

RAW = '''Here are the test cases for the User Story and acceptance criteria:

{
 "title": "TC1: Valid To Card Transfer",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter transaction amount within allowed range (1000-2000000 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 0,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Fill in recipient's card number (16 digits) and select AMD account as source.",
 "expected": "Transaction form is displayed with valid data."
 },
 {
 "content": "Enter transaction amount within allowed range (1000-2000000 AMD).",
 "expected": "Transaction amount is validated to be within the allowed range."
 },
 {
 "content": "Confirm transaction details and proceed with transfer.",
 "expected": "Transfer is executed successfully, and a success message is displayed."
 }
 ]
}

{
 "title": "TC2: Invalid Card Number",
 "custom_steps": "Fill in invalid recipient's card number (less than 16 digits or not numeric), select AMD account as source, enter transaction amount within allowed range (1000-2000000 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 1,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <invalid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Fill in invalid recipient's card number (less than 16 digits or not numeric).",
 "expected": "Error message is displayed indicating an invalid card number."
 }
 ]
}

{
 "title": "TC3: Transaction Amount Less Than Minimum Allowed",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter transaction amount less than minimum allowed (999 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 1,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Enter transaction amount less than minimum allowed (999 AMD).",
 "expected": "Error message is displayed indicating a transaction amount that is less than the minimum allowed."
 }
 ]
}

{
 "title": "TC4: Transaction Amount More Than Maximum Allowed",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter transaction amount more than maximum allowed (2000001 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 1,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Enter transaction amount more than maximum allowed (2000001 AMD).",
 "expected": "Error message is displayed indicating a transaction amount that is more than the maximum allowed."
 }
 ]
}

{
 "title": "TC5: Inactive Card Source",
 "custom_steps": "Fill in recipient's card number, select inactive card as source, enter transaction amount within allowed range (1000-2000000 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 1,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Select inactive card as source.",
 "expected": "Error message is displayed indicating that the source card is inactive."
 }
 ]
}

{
 "title": "TC6: Recipient Card Number Inactive",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter transaction amount within allowed range (1000-2000000 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 1,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Fill in recipient's card number that is inactive.",
 "expected": "Error message is displayed indicating that the recipient's card number is inactive."
 }
 ]
}

{
 "title": "TC7: Valid To Card Transfer with Conversion",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter transaction amount within allowed range (1000-2000000 AMD) for a different currency, convert to AMD using Central Bank official exchange rate, confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 0,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Fill in recipient's card number and select AMD account as source.",
 "expected": "Transaction form is displayed with valid data."
 },
 {
 "content": "Enter transaction amount within allowed range (1000-2000000 AMD) for a different currency, convert to AMD using Central Bank official exchange rate.",
 "expected": "Transaction amount is validated to be within the allowed range after conversion."
 },
 {
 "content": "Confirm transaction details and proceed with transfer.",
 "expected": "Transfer is executed successfully, and a success message is displayed."
 }
 ]
}

{
 "title": "TC8: Error Handling",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter invalid transaction data (e.g. negative amount), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 1,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Enter invalid transaction data (e.g. negative amount).",
 "expected": "Error message is displayed indicating an invalid transaction."
 }
 ]
}

{
 "title": "TC9: Successful To Card Transfer",
 "custom_steps": "Fill in recipient's card number, select AMD account as source, enter transaction amount within allowed range (1000-2000000 AMD), confirm transaction details, and proceed with transfer.",
 "custom_ispositive": 0,
 "custom_automation_type": 0,
 "type_id": 12,
 "custom_preconds": "Base URL: /mobile-banking/api/v1/transactions, Endpoint: /to-card-transfers, Method: POST, Authorization: Bearer <valid_token>",
 "priority_id": 2,
 "custom_steps_separated": [
 {
 "content": "Fill in recipient's card number and select AMD account as source.",
 "expected": "Transaction form is displayed with valid data."
 },
 {
 "content": "Enter transaction amount within allowed range (1000-2000000 AMD).",
 "expected": "Transaction amount is validated to be within the allowed range."
 },
 {
 "content": "Confirm transaction details and proceed with transfer.",
 "expected": "Transfer is executed successfully, and a success message is displayed."
 }
 ]
}
'''


def test_clean_json_string_produces_valid_json():
    cleaned = clean_json_string(RAW)
    data = json.loads(cleaned)
    assert isinstance(data, list)
    assert len(data) == 9
    assert data[0]['title'] == 'TC1: Valid To Card Transfer'


def test_parse_test_cases_returns_list_of_dicts():
    cases = parse_test_cases(RAW)
    assert isinstance(cases, list)
    assert cases[-1]['title'] == 'TC9: Successful To Card Transfer'
    assert cases[1]['custom_ispositive'] == 1
