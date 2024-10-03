import os


class PrivacyPolicy:
    def __init__(self, company_name):
        self.path = os.path.join(os.getcwd(), "privacy_policies", company_name.lower() + ".txt")
        self.policy_text = self.get_policy_text()

    def get_policy_text(self):
        with open(self.path) as f:
            policy_text = "\n".join(line.rstrip() for line in f if line != "\n")
        return policy_text
