
class DashboardDataObjects:

    def __init__(
            self,
            total_no_of_leads,
            total_account_created,
            leads_to_be_covered,
            total_loan_amount,
            total_application_created,
            total_disbursed_amount,
            total_application_assets_net_weight,
            total_loan_created,
            # leaderboard,
            timestamps,
            gold_rate_per_gram,
            lending_gold_rate_per_gram,
            # recent_apps,
            # recent_accounts
        ):

        self.total_no_of_leads=total_no_of_leads
        self.total_account_created=total_account_created
        self.leads_to_be_covered=leads_to_be_covered
        self.total_loan_amount=total_loan_amount
        self.total_application_created=total_application_created
        self.total_disbursed_amount=total_disbursed_amount
        self.total_application_assets_net_weight=total_application_assets_net_weight
        self.total_loan_created=total_loan_created
        # self.leaderboard=leaderboard
        self.timestamps=timestamps
        self.lending_gold_rate_per_gram=lending_gold_rate_per_gram
        self.gold_rate_per_gram=gold_rate_per_gram
        # self.recent_apps=recent_apps
        # self.recent_accounts=recent_accounts