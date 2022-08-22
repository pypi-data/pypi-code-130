def clean(data_file, country_code = '+91'):
    # Global Variables (List)
    raw_data = []
    data = []
    processed_data = []
    str = ''

    # Read Raw_Data
    with open(data_file, 'r', encoding='utf8') as file:
        str = file.read()

    raw_data = str.split(',')

    # Cleaning Data
    for z in raw_data:
        val = []
        # Removing Country Code
        val.append(z.replace(country_code, ''))

        for z in val:
            # Removing Blank Spaces
            processed_data.append(z.replace(' ', ''))

    # Removing Duplicates
    for x in set(processed_data):
        data.append(x)

    # Writing Cleaned Data to data.txt
    with open('data.txt', 'w', encoding='utf8') as file:
        for x in (data):
            file.write(x + '\n')