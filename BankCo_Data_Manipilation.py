import requests
import geocoder
import xml.etree.ElementTree as ET
import csv

cities = {}

def get_city_name(lat, lon):
    key = "%s,%s" % (lat, lon)
    name = cities.get(key, None)
    if name is None:
        foo = geocoder.osm([lat,lon], method='reverse')
        name = foo.current_result.state
        cities[key] = name 
    return name

resp = requests.get('https://df-dev.bk.rw/interview01/transactions')
raw_transactions = resp.json()
print(raw_transactions)

resp2 = requests.get("https://df-dev.bk.rw/interview01/customers")

root = ET.fromstring(resp2.content)

customers = {}
for elt in root.getchildren():
    cust_dict = {}
    for tag_elt in elt.getchildren():
        cust_dict[tag_elt.tag] = tag_elt.text
    customers[cust_dict['id']] = cust_dict['name']

print(customers)
transactions =[]
city_transactions = {}

i = 1
for elt in raw_transactions:
    transaction_id = i
    datetime = elt['timestamp']
    customer_id = elt['customerId']
    city_name = get_city_name(elt['latitude'], elt['longitude'])
    customer_name = customers[str(elt['customerId'])]
    amount = elt['amount']
	
    transactions.append(dict(
        transaction_id=transaction_id, 
        datetime=datetime, 
        customer_id=customer_id, 
        city_name=city_name, 
        customer_name=customer_name, 
        amount=amount)
    )
    if city_name not in city_transactions:
        city_transactions[city_name] = dict(amount=[], customers=[], trans_ids=[])
    city_transactions[city_name]['amount'].append(amount)
    city_transactions[city_name]['customers'].append(customer_id)
    city_transactions[city_name]['trans_ids'].append(transaction_id)

    i += 1

with open('transactions.csv', 'w') as trans_csv:
    csv_writer = csv.writer(trans_csv)
    csv_writer.writerow(["%s, %s, %s, %s, %s, %s/n" % ("transaction_id", "datetime", "customer_id", "customer_name", "amount", "city_name")])
    for elt in transactions:
        csv_writer.writerow(["%s, %s, %s, %s, %s, %s/n" % (elt["transaction_id"], elt["datetime"], elt["customer_id"], elt["customer_name"], elt["amount"], elt["city_name"])])


with open('city_totals.csv', 'w') as city_csv:
    csv_writer = csv.writer(city_csv)
    csv_writer.writerow(["%s, %s, %s, %s/n" % ("city_name", "total_amount", "unique_customers", "total_trancactions")])
    for elt in city_transactions.keys():
        csv_writer.writerow(["%s, %s, %s, %s/n" % (elt, sum(city_transactions[elt]['amount']), len(set(city_transactions[elt]['customers'])), len(city_transactions[elt]['trans_ids']))])