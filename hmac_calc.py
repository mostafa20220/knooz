import hashlib
import hmac
import json
from marshal import dumps

from decouple import config


def validate_hmac(payload, received_mac):

    if not received_mac:
        return

    # Step 2: Sort the data by keys lexicographically
    hmac_keys = [
        "amount_cents", "created_at", "currency", "error_occured",
        "has_parent_transaction", "id", "integration_id", "is_3d_secure",
        "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
        "is_voided", "order.id", "owner", "pending", "source_data.pan",
        "source_data.sub_type", "source_data.type", "success"
    ]

    # Extract and sort the relevant keys
    sorted_data = []
    for key in hmac_keys:
        value = get_nested_value(payload, key)
        if value is not None:
            sorted_data.append(value if isinstance(value, str) else json.dumps(value))

    # Step 3: Concatenate the values in the specified order
    concatenated_string = ''.join(sorted_data)
    hmac_secret = config('PAYMOB_HMAC_SECRET')
    computed_hmac = hmac.new(hmac_secret.encode(), concatenated_string.encode(), hashlib.sha512).hexdigest()

    # Step 5: Compare the HMAC values
    if not hmac.compare_digest(computed_hmac, received_mac):
        print(f"Invalid HMAC signature. Received: {received_mac}, Computed: {computed_hmac}")
        return
    # Step 6: Process the callback if HMAC validation passes
    print("HMAC validation succeeded. Processing callback.")



payload = {
"type": "TRANSACTION",
"obj": {
    "id": 192036465,
    "pending": False,
    "amount_cents": 100000,
    "success": True,
    "is_auth": False,
    "is_capture": False,
    "is_standalone_payment": True,
    "is_voided": False,
    "is_refunded": False,
    "is_3d_secure": True,
    "integration_id": 4097558,
    "profile_id": 164295,
    "has_parent_transaction": False,
    "order": {
        "id": 217503754,
        "created_at": "2024-06-13T11:32:09.628623",
        "delivery_needed": False,
        "merchant": {
            "id": 164295,
            "created_at": "2022-03-24T21:13:47.852384",
            "phones": [
                "+201024710769"
            ],
            "company_emails": [
                "mohamedabdelsttar97@gmail.com"
            ],
            "company_name": "Parmagly",
            "state": "",
            "country": "EGY",
            "city": "Cairo",
            "postal_code": "",
            "street": ""
        },
        "collector": None,
        "amount_cents": 100000,
        "shipping_data": {
            "id": 108010028,
            "first_name": "dumy",
            "last_name": "dumy",
            "street": "dumy",
            "building": "dumy",
            "floor": "dumy",
            "apartment": "sympl",
            "city": "dumy",
            "state": "dumy",
            "country": "EG",
            "email": "dumy@dumy.com",
            "phone_number": "+201125773493",
            "postal_code": "NA",
            "extra_description": "",
            "shipping_method": "UNK",
            "order_id": 217503754,
            "order": 217503754
        },
        "currency": "EGP",
        "is_payment_locked": False,
        "is_return": False,
        "is_cancel": False,
        "is_returned": False,
        "is_canceled": False,
        "merchant_order_id": None,
        "wallet_notification": None,
        "paid_amount_cents": 100000,
        "notify_user_with_email": False,
        "items": [],
        "order_url": "NA",
        "commission_fees": 0,
        "delivery_fees_cents": 0,
        "delivery_vat_cents": 0,
        "payment_method": "tbc",
        "merchant_staff_tag": None,
        "api_source": "OTHER",
        "data": {}
    },
    "created_at": "2024-06-13T11:33:44.592345",
    "transaction_processed_callback_responses": [],
    "currency": "EGP",
    "source_data": {
        "pan": "2346",
        "type": "card",
        "tenure": None,
        "sub_type": "MasterCard"
    },
    "api_source": "IFRAME",
    "terminal_id": None,
    "merchant_commission": 0,
    "installment": None,
    "discount_details": [],
    "is_void": False,
    "is_refund": False,
    "data": {
        "gateway_integration_pk": 4097558,
        "klass": "MigsPayment",
        "created_at": "2024-06-13T08:34:07.076347",
        "amount": 100000.0,
        "currency": "EGP",
        "migs_order": {
            "acceptPartialAmount": False,
            "amount": 1000.0,
            "authenticationStatus": "AUTHENTICATION_SUCCESSFUL",
            "chargeback": {
                "amount": 0,
                "currency": "EGP"
            },
            "creationTime": "2024-06-13T08:34:00.850Z",
            "currency": "EGP",
            "description": "PAYMOB Parmagly",
            "id": "217503754",
            "lastUpdatedTime": "2024-06-13T08:34:06.883Z",
            "merchantAmount": 1000.0,
            "merchantCategoryCode": "7299",
            "merchantCurrency": "EGP",
            "status": "CAPTURED",
            "totalAuthorizedAmount": 1000.0,
            "totalCapturedAmount": 1000.0,
            "totalRefundedAmount": 0.0
        },
        "merchant": "TESTMERCH_C_25P",
        "migs_result": "SUCCESS",
        "migs_transaction": {
            "acquirer": {
                "batch": 20240613,
                "date": "0613",
                "id": "BMNF_S2I",
                "merchantId": "MERCH_C_25P",
                "settlementDate": "2024-06-13",
                "timeZone": "+0200",
                "transactionId": "123456789"
            },
            "amount": 1000.0,
            "authenticationStatus": "AUTHENTICATION_SUCCESSFUL",
            "authorizationCode": "326441",
            "currency": "EGP",
            "id": "192036465",
            "receipt": "416508326441",
            "source": "INTERNET",
            "stan": "326441",
            "terminal": "BMNF0506",
            "type": "PAYMENT"
        },
        "txn_response_code": "APPROVED",
        "acq_response_code": "00",
        "message": "Approved",
        "merchant_txn_ref": "192036465",
        "order_info": "217503754",
        "receipt_no": "416508326441",
        "transaction_no": "123456789",
        "batch_no": 20240613,
        "authorize_id": "326441",
        "card_type": "MASTERCARD",
        "card_num": "512345xxxxxx2346",
        "secure_hash": "",
        "avs_result_code": "",
        "avs_acq_response_code": "00",
        "captured_amount": 1000.0,
        "authorised_amount": 1000.0,
        "refunded_amount": 0.0,
        "acs_eci": "02"
    },
    "is_hidden": False,
    "payment_key_claims": {
        "extra": {},
        "user_id": 302852,
        "currency": "EGP",
        "order_id": 217503754,
        "amount_cents": 100000,
        "billing_data": {
            "city": "dumy",
            "email": "dumy@dumy.com",
            "floor": "dumy",
            "state": "dumy",
            "street": "dumy",
            "country": "EG",
            "building": "dumy",
            "apartment": "sympl",
            "last_name": "dumy",
            "first_name": "dumy",
            "postal_code": "NA",
            "phone_number": "+201125773493",
            "extra_description": "NA"
        },
        "redirect_url": "https://accept.paymob.com/unifiedcheckout/payment-status?payment_token=ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5WDJsa0lqb3pNREk0TlRJc0ltRnRiM1Z1ZEY5alpXNTBjeUk2TVRBd01EQXdMQ0pqZFhKeVpXNWplU0k2SWtWSFVDSXNJbWx1ZEdWbmNtRjBhVzl1WDJsa0lqbzBNRGszTlRVNExDSnZjbVJsY2w5cFpDSTZNakUzTlRBek56VTBMQ0ppYVd4c2FXNW5YMlJoZEdFaU9uc2labWx5YzNSZmJtRnRaU0k2SW1SMWJYa2lMQ0pzWVhOMFgyNWhiV1VpT2lKa2RXMTVJaXdpYzNSeVpXVjBJam9pWkhWdGVTSXNJbUoxYVd4a2FXNW5Jam9pWkhWdGVTSXNJbVpzYjI5eUlqb2laSFZ0ZVNJc0ltRndZWEowYldWdWRDSTZJbk41YlhCc0lpd2lZMmwwZVNJNkltUjFiWGtpTENKemRHRjBaU0k2SW1SMWJYa2lMQ0pqYjNWdWRISjVJam9pUlVjaUxDSmxiV0ZwYkNJNkltUjFiWGxBWkhWdGVTNWpiMjBpTENKd2FHOXVaVjl1ZFcxaVpYSWlPaUlyTWpBeE1USTFOemN6TkRreklpd2ljRzl6ZEdGc1gyTnZaR1VpT2lKT1FTSXNJbVY0ZEhKaFgyUmxjMk55YVhCMGFXOXVJam9pVGtFaWZTd2liRzlqYTE5dmNtUmxjbDkzYUdWdVgzQmhhV1FpT21aaGJITmxMQ0psZUhSeVlTSTZlMzBzSW5OcGJtZHNaVjl3WVhsdFpXNTBYMkYwZEdWdGNIUWlPbVpoYkhObExDSnVaWGgwWDNCaGVXMWxiblJmYVc1MFpXNTBhVzl1SWpvaWNHbGZkR1Z6ZEY5a01EUmtNV0U0TkRrMk1tSTBOemt5T1dJeVpHTXhOalJoTURReU5qaGlZeUo5LkFPc3l2S1A4a3Fob0E5aVFOSEZfQWFaZl9HQi1NcU5kcXhrQmhlZm1feVpIZHJ3ci1xbkUxWklKT2FxekRFMkp5cXhCWXVEdnZ1VVZweGV3bFVGTTlB&trx_id=192036465",
        "integration_id": 4097558,
        "lock_order_when_paid": False,
        "next_payment_intention": "pi_test_d04d1a84962b47929b2dc164a04268bc",
        "single_payment_attempt": False
    },
    "error_occured": False,
    "is_live": False,
    "other_endpoint_reference": None,
    "refunded_amount_cents": 0,
    "source_id": -1,
    "is_captured": False,
    "captured_amount": 0,
    "merchant_staff_tag": None,
    "updated_at": "2024-06-13T11:34:07.272638",
    "is_settled": False,
    "bill_balanced": False,
    "is_bill": False,
    "owner": 302852,
    "parent_transaction": None
},
"issuer_bank": None,
"transaction_processed_callback_responses": ""
}


# Example usage
received_hmac = 'fa8ac0b7f3852e60c50e7fdd4ea5ef0bda96030c19dea1d55df8c76d6c08ab1877774662cbb04981dc84839ad4da560bcc8cb53b8973548657f7e8f8d2e79930'
validate_hmac(payload.get('obj'), received_hmac)
# print("1000002024-06-13T11:33:44.592345EGPfalsefalse1920364654097558truefalsefalsefalsetruefalse217503754302852false2346MasterCardcardtrue")