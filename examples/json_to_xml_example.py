from json_to_many import convert

# Complex JSON data
json_data = {
    "report": {
        "title": "Sales Report",
        "date": "2023-10-01",
        "data": [
            {"region": "North", "sales": 1500, "change": 5.5},
            {"region": "South", "sales": 1250, "change": -3.2},
            {"region": "East", "sales": 1750, "change": 2.0},
            {"region": "West", "sales": 1600, "change": 4.1},
        ],
    }
}

# Convert JSON data to XML without saving to a file
xml_data = convert(json_data, "xml", return_data=True)
print(xml_data)
