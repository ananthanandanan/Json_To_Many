from json_to_many import convert

# Complex JSON data for CSV conversion
json_data = [
    {
        "name": "Alice",
        "age": 30,
        "contact": {"email": "alice@example.com", "phone": "123-456-7890"},
        "skills": ["Python", "Data Analysis"],
        "address": {
            "street": "123 Maple Street",
            "city": "New York",
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
        },
    },
    {
        "name": "Bob",
        "age": 25,
        "contact": {"email": "bob@example.com", "phone": "987-654-3210"},
        "skills": ["JavaScript", "Web Development"],
        "address": {
            "street": "456 Oak Avenue",
            "city": "Los Angeles",
            "coordinates": {"latitude": 34.0522, "longitude": -118.2437},
        },
    },
]

# Convert JSON data to XML without saving to a file
xml_data = convert(json_data, "csv", return_data=True)
print(xml_data)
