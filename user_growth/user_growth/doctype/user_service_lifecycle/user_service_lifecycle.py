import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class UserServiceLifecycle(Document):
    def validate(self):
        self.validate_churn_date()

    def validate_churn_date(self):
        if self.service_status == "Active":
            self.churn_date = None
            return

        if self.service_status == "Churned" and not self.churn_date:
            frappe.throw("Churn Date is required when Service Status is Churned")

        if self.churn_date and getdate(self.churn_date) < getdate(self.signup_date):
            frappe.throw("Churn Date cannot be before Signup Date")
