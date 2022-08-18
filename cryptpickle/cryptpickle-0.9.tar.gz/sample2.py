import cryptpickle
import pandas as pd

# Create a dictionary with some data
df1 = pd.DataFrame({'A': [1, 2, 3],
                   'B': ['one', 'one', 'four']})

# Print the data
print(df1)

# Serialice the data in an encrypted file (path) with a password (password)
cryptpickle.obj_to_encrypted(df1,password="SecretPassword",path='./pd_data.crypt')

# Load the serialiced data in other Pandas DataFrame.
df2 =cryptpickle.obj_from_encrypted(password="SecretPassword",path='./pd_data.crypt')

# Print the data
print(df2)