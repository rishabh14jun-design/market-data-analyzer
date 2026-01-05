import csv

total_balance = 0
valid = 0
invalid = 0

with open("batch_job/accounts.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:
        balance = int(row["balance"])
        status = row["status"]

        if status != "ACTIVE":
            continue

        if balance < 0:
            invalid += 1
        else:
            valid += 1
            total_balance += balance

print("Valid accounts :", valid)
print("Invalid accounts :", invalid)
print("Total balance :", total_balance)
