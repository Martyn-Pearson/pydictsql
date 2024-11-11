import pydictsql

SALES_TEAM = [
		{'name': 'Adam', 'city': 'London', 'sales': 100},
		{'name': 'Bob', 'city': 'London', 'sales': 400},
		{'name': 'Charles', 'city': 'Birmingham', 'sales': 350},
		{'name': 'David', 'city': 'London', 'sales': 290},
		{'name': 'Edward', 'city': 'Cardiff', 'sales': 180},
		{'name': 'Frank', 'city': 'Glasgow', 'sales': 320},
		{'name': 'Geoff', 'city': 'Cardiff', 'sales': 500},
		{'name': 'Hugh', 'city': 'London', 'sales': 380},
		{'name': 'Ian', 'city': 'Birmingham', 'sales': 350},
		{'name': 'John', 'city': 'Birmingham', 'sales': 460}
	]

filter = pydictsql.DictFilter("SELECT {name} FROM {sales_team} WHERE {sales} > 400")
results = filter.filter(sales_team = SALES_TEAM)
for record in results:
    print(record["name"])