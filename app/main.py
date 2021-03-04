import boto3
import dotenv
import os
import json
import logging
from datetime import datetime
from dateutil import relativedelta
from boto_factory import BotoFactory
from cost_ops import CostOps

dotenv.load_dotenv()
log = logging.getLogger()
log.setLevel(level=logging.ERROR)


def send_email(params, recipients):
    with open('email_template.html') as f:
        email_body = f.read()

    ses = BotoFactory().get_capability(
        boto3.client, boto3.Session(), 'ses',
        account_id=os.environ.get('SES_ACCOUNT'),
        region=os.environ.get('SES_REGION'),
        rolename=os.environ.get('SES_ROLE')
    )

    response = ses.send_email(
        Source=os.environ.get('FROM_EMAIL'),
        Destination={
            'ToAddresses': recipients
        },
        ReplyToAddresses=[
            # 'carlf@axis.com'
            os.environ.get('REPLY_TO_EMAIL')
        ],
        Message={
            'Subject': {
                    'Data': f"AWS account {params.get('ACCOUNT_ID')} cost report",
                    'Charset': 'utf-8'
                },
            'Body': {
                'Html': {
                    'Data': email_body % params,
                    'Charset': 'utf-8'
                }
            }
        },
        Tags=[
            {
                'Name': 'Origin',
                'Value': 'CostReporterLambda'
            }
        ]
    )
    log.info(json.dumps(response, indent=4, default=str))
    return response


def handler(event, context):
    if not event.get('EmailRecipients'):
        raise ValueError("event missing EmailRecipient")

    ce = boto3.client('ce')
    co = CostOps(ce)

    last_3_bills = co.get_total_cost_for_past_months(3)

    tax = float(os.environ.get('TAX'))
    account_total_w_tax = last_3_bills[2]
    account_total_wo_tax = account_total_w_tax/(1+tax)
    vat = account_total_w_tax - account_total_wo_tax
    sum_bills = 0
    for b in last_3_bills:
        sum_bills += b

    last_month = datetime.now() + relativedelta.relativedelta(months=-1)
    first_day_last_month = last_month.replace(day=1)

    params = {
        'ACCOUNT_ID': boto3.client('sts').get_caller_identity().get('Account'),
        'MONTH': first_day_last_month.strftime('%B %Y'),
        'TOTAL': round(account_total_wo_tax, 2),
        'VAT': round(vat, 2),
        'TOTAL_W_VAT': round(account_total_w_tax, 2),
        'TOTAL_3_MO_W_VAT': round(sum_bills, 2)
    }

    # print(params)

    result = send_email(params, event['EmailRecipients'])
    return result


if __name__ == '__main__':
    event = {
        'EmailRecipients': ['carlf@axis.com']
    }
    handler(event, None)
