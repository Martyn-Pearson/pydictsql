###Introduction
pydictsql is a library which allows you to filter records using SQL. It is aimed at filtering JSON records, or records returned by reading a CSV file with a DictReader, but of course may have many other uses.

###Example

Say we have the following data:

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

If we want to find the names of all sales people with a sales figure of over 400, we can then use the library to filter that list as follows:

	import pydictsql

	filter = pydictsql.DictFilter("SELECT {name} FROM {sales_team} WHERE {sales} > 400")
	results = filter.filter(sales_team = SALES_TEAM)
	for record in results:
		print(record["name"])

###SQL Syntax
The syntax is a subset of the SQL syntax that you will be familiar with when working with databases. 

Because field names in json and CSV files may not adhere to the same standards as those in databases, all field names are enclosed in curly brackets.

pydictsql supports the following logical operators:
- AND
- OR
- NOT

and the following comparison operators:
- less than <
- greater than >
- less than or equal to <=
- greater than or equal to >=
- equal to = 
- not equal to <>

Note that the reference in the FROM clause of the SQL must match the named parameter passed to the filter / filtergen methods.

###Class Reference
####pydictsql.DictFilter()
#####Details
Constructs a DictFilter object, taking the SQL which will be applied to filter data.
#####Parameters
- sql SQL Select statement which is used to filter data

#####Raises
- InvalidTokenError: Raised when tokenising and an invalid value is read
- UnexpectedTokenError: Raised when an unexpected token is encountered parsing the SQL

####pydictsql.DictFilter.filter()
#####Details
Applies the SQL to the given data, return the records which satisfy the given SQL.

#####Parameters
- &lt;collection&gt; Data to be filtered. Note that the kwarg name &lt;collection&gt; must match that in the FROM reference in the SQL

#####Returns
- Tuple (If passed a tuple) or list of records satisfying the given SQL, with each records having the selected fields as defined in the SQL.

#####Raises
- ValueError: Raised when an invalid parameter is passed to the method, for example a parameter which is not a list, tuple or generator, or the kwarg name not matching the FROM clause in the SQL.
- UnexpectedReferenceError: Raised when a field reference in the SQL is not found in the passed data.

####pydictsql.DictFilter.filtergen()
#####Details
Applies the SQL to the given data, yielding each matching record as the given data is iterated over. This may be preferred when processing larger data sets.

#####Parameters
- &lt;collection&gt; Data to be filtered. Note that the kwarg name &lt;collection&gt; must match that in the FROM reference in the SQL

#####Returns
- Tuple (If passed a tuple) or list of records satisfying the given SQL, with each records having the selected fields as defined in the SQL.

#####Raises
- ValueError: Raised when an invalid parameter is passed to the method, for example a parameter which is not a list, tuple or generator, or the kwarg name not matching the FROM clause in the SQL.
- UnexpectedReferenceError: Raised when a field reference in the SQL is not found in the passed data.

###General Points
#### filter() vs filtergen()
Filter will return a collection containing each of the records which meet the SQL criteria, meaning that they will be loaded into memory. If you are processing a large amount of data and do not wish to store all matching records at the same time, then filtergen should be used.

#### Why the named parameter?
I&apos;m future proofing here, leaving the door open to easily adding multiple data sources with joins or unions.

