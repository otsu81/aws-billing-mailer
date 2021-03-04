# AWS Cost reporter

AWS does not send out a copy of the monthly billing to child accounts under an AWS Organization, even if you specify a Billing responsible under alternate contacts. This is probably to avoid confusion for the child account holders, but does mean that it can be difficult for a distributed setup to remember that they've got resources running and costing money.

This Lambda function will run based on a schedule and e-mail a set of recipients a very short summary of the account's total spend and data transfer out costs, like this:

>## Monthly report, account 123456789012 for October 2020
>
>Account total spend, excl VAT: USD 80.00
>
>Total VAT: USD 20.00 \
>Total incl VAT: USD 100.00
>
>Account total over past 3 months, with VAT: 300.00
>
>For details, see the cost explorer for the account (must be logged on to the console to see):
>https://console.aws.amazon.com/cost-management/
>
>For a copy of the monthly billing statement, see the billing console (must be logged in):
>https://console.aws.amazon.com/billing/>For details, see the cost explorer for the account


## Requirements
* AWS SAM
* An AWS account with an SES domain configured
* IAM role in the SES domain account which can be assumed by the Lambda function's role

## Deployment

```
sam build
sam deploy --guided
```

When deploying with the `--guided` flag you'll be asked to provide the necessary information. The default `cron` expression is to run on the 3rd every month - AWS doesn't always complete the adjustments for the billing in time for the 3rd, but most of the time they do. If you have very high requirements for exact down-to-the-cent reporting it's recommended to increase to a later date.