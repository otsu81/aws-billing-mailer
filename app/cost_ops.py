from datetime import date
from dateutil.relativedelta import relativedelta


class CostOps():

    def __init__(self, cost_explorer_client):
        self.ce = cost_explorer_client

    def get_cost_timespan(self, start, end):
        return self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )['ResultsByTime']

    def get_last_nbr_months_bills(self, months):
        """returns the bills for the past nbr_months in dictionary form"""
        this_month = date.today().replace(day=1)
        start = this_month - relativedelta(months=months)
        return self.get_cost_timespan(
            str(start), str(this_month)
            )

    def get_total_cost_for_past_months(self, months):
        """get a list of costs for the number of param: months"""
        bills = self.get_last_nbr_months_bills(months)
        monthly_costs = list()
        for bill in bills:
            cost = float(bill['Total']['UnblendedCost']['Amount'])
            if round(cost) > 0:
                # print(f"{account_id}: {cost}")
                monthly_costs.append(cost)
        return monthly_costs

    def get_mean_growth_over_months(self, months):
        """returns the percentage mean of growth for the past
        param:(int)months"""
        monthly_costs = self.get_total_cost_for_past_months(months)
        monthly_growth = list()
        for i in range(len(monthly_costs) - 1):
            monthly_growth.append(monthly_costs[i + 1]/monthly_costs[i])

        if len(monthly_growth) > 0:
            return sum(monthly_growth)/(len(monthly_growth)) - 1
        else:
            return 0

    def get_dto_total_cost(ce_groups_list):
        substring = 'DataTransfer-Out'
        total_amount = 0
        for item in ce_groups_list:
            if any(substring in key for key in item.get('Keys')):
                total_amount += float(
                    item['Metrics']['UnblendedCost']['Amount']
                    )
        return float(total_amount)

    def get_dto_by_groups(ce, start='', end=''):
        cost = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['UNBLENDED_COST'],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Elastic Compute Cloud - Compute']
                }
            },
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'USAGE_TYPE'
                }
            ]
        )['ResultsByTime']
        return cost[0].get('Groups')
