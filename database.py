import requests
from models import Customer
from datetime import datetime

# BU YERGA SUPABASE MA'LUMOTLARINGIZNI QO'YING
SUPABASE_URL = "https://pmgfhwzkzowqzezhnhlx.supabase.co"
SUPABASE_KEY = "sb_publishable_dkoB3iz1D6bM6t2SQFf6yg_CMbt6T_v"

class Database:
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def add_customer(self, customer):
        data = {"name": customer.full_name, "phone": customer.phone, "address": customer.address}
        requests.post(f"{SUPABASE_URL}/rest/v1/customers", headers=self.headers, json=data)

    def get_all_customers(self):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/customers?select=*", headers=self.headers)
        if r.status_code == 200:
            return [Customer(id=r_['id'], full_name=r_['name'], phone=r_['phone'], address=r_['address']) for r_ in r.json()]
        return []

    def get_customer_total_debt(self, customer_id):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/debts?customer_id=eq.{customer_id}&select=amount", headers=self.headers)
        if r.status_code == 200:
            return sum(item['amount'] for item in r.json())
        return 0

    def get_total_debt_sum(self):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/debts?select=amount", headers=self.headers)
        if r.status_code == 200:
            return sum(item['amount'] for item in r.json())
        return 0

    def get_debtors_count(self):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/debts?select=customer_id,amount", headers=self.headers)
        if r.status_code == 200:
            debtors = {item['customer_id'] for item in r.json() if item['amount'] > 0}
            return len(debtors)
        return 0

    def update_customer(self, customer_id, name, phone, address):
        data = {"name": name, "phone": phone, "address": address}
        requests.patch(f"{SUPABASE_URL}/rest/v1/customers?id=eq.{customer_id}", headers=self.headers, json=data)

    def delete_customer(self, customer_id):
        requests.delete(f"{SUPABASE_URL}/rest/v1/customers?id=eq.{customer_id}", headers=self.headers)

    def add_debt(self, customer_id, amount, description):
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        data = {"customer_id": customer_id, "amount": float(amount), "desc": description, "date": date}
        r = requests.post(f"{SUPABASE_URL}/rest/v1/debts", headers=self.headers, json=data)
        
    def add_payment(self, customer_id, amount, description):
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        data = {"customer_id": customer_id, "amount": -float(amount), "desc": description, "date": date}
        r = requests.post(f"{SUPABASE_URL}/rest/v1/debts", headers=self.headers, json=data)
        
        if r.status_code not in [200, 201]:
            print(f"TO'LOVDA XATO: {r.status_code} - {r.text}")
        else:
            print("To'lov muvaffaqiyatli qo'shildi!")

    def add_payment(self, customer_id, amount, description):
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        data = {"customer_id": customer_id, "amount": -float(amount), "desc": description, "date": date}
        requests.post(f"{SUPABASE_URL}/rest/v1/debts", headers=self.headers, json=data)

    def get_customer_history(self, customer_id):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/debts?customer_id=eq.{customer_id}&order=id.desc", headers=self.headers)
        if r.status_code == 200:
            return [(item['amount'], item['date'], item['desc']) for item in r.json()]
        return []

    def get_filtered_customers(self, min_debt=None, max_debt=None, address=None):
        url = f"{SUPABASE_URL}/rest/v1/customers?select=*"
        if address:
            url += f"&address=ilike.*{address}*"
        
        r = requests.get(url, headers=self.headers)
        filtered = []
        if r.status_code == 200:
            for cust in r.json():
                total_debt = self.get_customer_total_debt(cust['id'])
                if min_debt and total_debt < float(min_debt): continue
                if max_debt and total_debt > float(max_debt): continue
                filtered.append(((cust['id'], cust['name'], cust['phone'], cust['address']), total_debt))
        return filtered
    def login(self, email, password):
        try:
            payload = {"email": email, "password": password}
            r = requests.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                headers=self.headers,
                json=payload
            )
            
            if r.status_code == 200:
                token = r.json().get("access_token")
                self.headers["Authorization"] = f"Bearer {token}"
                return "SUCCESS"
            elif r.status_code == 400:
                if "Email not confirmed" in r.text:
                    return "CONFIRM_REQUIRED"
                return "WRONG_DATA"
            return "ERROR"
        except Exception as e:
            print(f"Login xatosi: {e}")
            return "ERROR"
