from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("roberta-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

code = '''import requests
def get_ip():
    """Get my current external IP.
    Other line.
    """
    result = requests.get("https://icanhazip.com").text.strip()
    return result
'''

tokenized_code = tokenizer.encode(code, padding=True, truncation=True, return_tensors="pt")
encoded_code = model(tokenized_code)["last_hidden_state"]
print(encoded_code.shape)
