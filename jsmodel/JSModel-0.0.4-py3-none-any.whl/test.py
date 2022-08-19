from Model import ParseModel
from typing import Optional
import re
class A:
    valueA=["Data","Information","Age"]



data=[
{
"Data":{
    "Information":
        {
        "Age":"20"
        }
    },
},
{
"Data":{
    "Information":
        {
        "Age":"22"
        }
    },
}



]
instance=ParseModel(A)
instance.data(data)
return_data=instance.parse()
for i in return_data:
    print(i)

# value="customerAthisisworld"
# test_str="customer*thisisworld"
# print(test_str.find("*"))
# new_str=test_str[0:test_str.find("*")]+"."+test_str[test_str.find("*"):]
# print(new_str)
# pattern=re.compile("customer.*")
# print(re.fullmatch(new_str,value))