import requests
from models import Customer
from datetime import datetime

SUPABASE_URL = "https://pmgfhwzkzowqzezhnhlx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZ2Zod3prem93cXplemhuaGx4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg1MDUzNjEsImV4cCI6MjA5NDA4MTM2MX0.ZwhTApwng1cKfEHFFn4BWn0nYG3mDuoGb8jv6JQY1E4"

class Database:
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def login(self, email, password):
        try:
            payload = {"email": email, "password": password}
            r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers=self.headers, json=payload)
            if r.status_code == 200:
                return "SUCCESS"
            return "ERROR"
        except Exception as e:
            return "CONNECTION_ERROR"

    def get_all_customers(self):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/customers?select=*", headers=self.headers)
        if r.status_code == 200:
            return [Customer(id=r_['id'], full_name=r_['name'], phone=r_['phone'], address=r_['address']) for r_ in r.json()]
        return []

    def get_debtors_count(self):
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/debts?select=customer_id&amount=gt.0",
            headers=self.headers
        )
        if r.status_code == 200:
            ids = set(item['customer_id'] for item in r.json())
            return len(ids)
        return 0

    def get_total_debt_sum(self):
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/debts?select=amount",
            headers=self.headers
        )
        if r.status_code == 200:
            return sum(item['amount'] for item in r.json())
        return 0

    def get_customer_total_debt(self, customer_id):
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/debts?select=amount&customer_id=eq.{customer_id}",
            headers=self.headers
        )
        if r.status_code == 200:
            return sum(item['amount'] for item in r.json())
        return 0

    def delete_customer(self, customer_id):
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/customers?id=eq.{customer_id}",
            headers=self.headers
        )
        return r.status_code == 204

    def update_customer(self, customer_id, name, phone, address):
        payload = {"name": name, "phone": phone, "address": address}
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/customers?id=eq.{customer_id}",
            headers=self.headers,
            json=payload
        )
        return r.status_code == 200

    def add_customer(self, customer):
        payload = {"name": customer.full_name, "phone": customer.phone, "address": customer.address}
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/customers",
            headers=self.headers,
            json=payload
        )
        return r.status_code == 201

    def add_debt(self, customer_id, amount, description):
        payload = {
            "customer_id": customer_id,
            "amount": amount,
            "desc": description,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/debts",
            headers=self.headers,
            json=payload
        )
        return r.status_code == 201

    def add_payment(self, customer_id, amount, description):
        payload = {
            "customer_id": customer_id,
            "amount": -amount,
            "desc": description,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/debts",
            headers=self.headers,
            json=payload
        )
        return r.status_code == 201

    def get_customer_history(self, customer_id):
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/debts?select=amount,date,desc&customer_id=eq.{customer_id}&order=id.asc",
            headers=self.headers
        )
        if r.status_code == 200:
            return [(item['amount'], item['date'], item['desc']) for item in r.json()]
        return []

    def get_filtered_customers(self, min_debt=None, max_debt=None, address=None, date=None):
        customers = self.get_all_customers()
        result = []

        for c in customers:
            debt = self.get_customer_total_debt(c.id)

            if min_debt:
                try:
                    if debt < float(min_debt):
                        continue
                except:
                    pass

            if max_debt:
                try:
                    if debt > float(max_debt):
                        continue
                except:
                    pass

            if address:
                if address.lower() not in c.address.lower():
                    continue

            if date:
                history = self.get_customer_history(c.id)
                dates = [row[1] for row in history if row[1]]
                if not any(date in str(d) for d in dates):
                    continue

            result.append((
                (c.id, c.full_name, c.phone, c.address),
                debt
            ))

        return result
