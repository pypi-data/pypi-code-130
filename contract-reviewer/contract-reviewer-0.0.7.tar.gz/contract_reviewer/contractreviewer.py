import sys, getopt, os, json 
from datasets import Dataset
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from transformers import pipeline
from tqdm import tqdm
from spacy import displacy
import tempfile
import webbrowser
import torch

QUESTION_FOR_LARGE = "Highlight the parts (if any) of this contract related to \"Parties\" that should be reviewed by a lawyer. Details: The two or more parties who signed the contract"
QUESTIONS = [
  {
    "Document Name": "Highlight the parts (if any) of this contract related to \"Document Name\" that should be reviewed by a lawyer. Details: The name of the contract"
  },
  {
    "Parties": "Highlight the parts (if any) of this contract related to \"Parties\" that should be reviewed by a lawyer. Details: The two or more parties who signed the contract"
  },
  {
    "Agreement Date": "Highlight the parts (if any) of this contract related to \"Agreement Date\" that should be reviewed by a lawyer. Details: The date of the contract"
  },
  {
    "Effective Date": "Highlight the parts (if any) of this contract related to \"Effective Date\" that should be reviewed by a lawyer. Details: The date when the contract is effective"
  },
  {
    "Expiration Date": "Highlight the parts (if any) of this contract related to \"Expiration Date\" that should be reviewed by a lawyer. Details: On what date will the contract's initial term expire?"
  },
  {
    "Renewal Term": "Highlight the parts (if any) of this contract related to \"Renewal Term\" that should be reviewed by a lawyer. Details: What is the renewal term after the initial term expires? This includes automatic extensions and unilateral extensions with prior notice."
  },
  {
    "Notice Period To Terminate Renewal": "Highlight the parts (if any) of this contract related to \"Notice Period To Terminate Renewal\" that should be reviewed by a lawyer. Details: What is the notice period required to terminate renewal?"
  },
  {
    "Governing Law": "Highlight the parts (if any) of this contract related to \"Governing Law\" that should be reviewed by a lawyer. Details: Which state/country's law governs the interpretation of the contract?"
  },
  {
    "Non-Compete": "Highlight the parts (if any) of this contract related to \"Non-Compete\" that should be reviewed by a lawyer. Details: Is there a restriction on the ability of a party to compete with the counterparty or operate in a certain geography or business or technology sector?"
  },
  {
    "Exclusivity": "Highlight the parts (if any) of this contract related to \"Exclusivity\" that should be reviewed by a lawyer. Details: Is there an exclusive dealing\u00a0 commitment with the counterparty? This includes a commitment to procure all \u201crequirements\u201d from one party of certain technology, goods, or services or a prohibition on licensing or selling technology, goods or services to third parties, or a prohibition on\u00a0 collaborating or working with other parties), whether during the contract or\u00a0 after the contract ends (or both)."
  },
  {
    "Change Of Control": "Highlight the parts (if any) of this contract related to \"Change Of Control\" that should be reviewed by a lawyer. Details: Does one party have the right to terminate or is consent or notice required of the counterparty if such party undergoes a change of control, such as a merger, stock sale, transfer of all or substantially all of its assets or business, or assignment by operation of law?"
  },
  {
    "Anti-Assignment": "Highlight the parts (if any) of this contract related to \"Anti-Assignment\" that should be reviewed by a lawyer. Details: Is consent or notice required of a party if the contract is assigned to a third party?"
  }
]
COLORS = ['#0DFAF4', '#10E040', '#0A9DF4', '#FAE900', '#FA0703', '#A3FAAB', '#BB6CF4', '#F400A7', '#DE5F0B', '#FADB0D', '#FA930D', '#A701F4']

def _extract_from_pdfs(paths):
    dicts = []

    for path in paths:
        output_string = StringIO()   
        try: 
            with open(path, 'rb') as fin:
                extract_text_to_fp(fin, output_string)
                _, tail = os.path.split(path)
                dicts.append({
                    'context': output_string.getvalue().strip(),
                    'title': tail[:-4]
                })
        except:
            print(f'Could not extract {path}')
    return dicts


def _read_contracts(paths):
    contracts = []
    for path in paths:
        # If dir then find all files with .pdf extension
        if os.path.isdir(path):
            for root, _, files in os.walk(path, topdown=False):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        contracts.append(os.path.join(root, file))
        else:
            if path.lower().endswith('.pdf'):
                contracts.append(path)

    return _extract_from_pdfs(contracts)


def _preprocess_contracts(contracts):
    customSet = []

    # load questions
    questions = QUESTIONS

    # add questions to documents
    for contract in contracts:
        for question in questions:
            temp = contract.copy()
            field, value = list(question.items())[0]
            temp['id'] = temp['title'] + '__' + field
            temp['question'] = value
            customSet.append(temp)

    customSet = {
        k: [d.get(k) for d in customSet]
        for k in set().union(*customSet)
    }
    return customSet
    

def create_dataset_from(paths):
    contracts = _read_contracts(paths)
    contracts = _preprocess_contracts(contracts)
    return Dataset.from_dict(contracts)


def run_model(dataset, base_model_name, large_model_name, score_threshold):
    base_tokenizer = AutoTokenizer.from_pretrained(base_model_name, TOKENIZERS_PARALLELISM=True)
    base_model = AutoModelForQuestionAnswering.from_pretrained(base_model_name)
    large_tokenizer = AutoTokenizer.from_pretrained(large_model_name, TOKENIZERS_PARALLELISM=True)
    large_model = AutoModelForQuestionAnswering.from_pretrained(large_model_name)

    base_nlp = None
    large_nlp = None
    if torch.cuda.is_available():
        base_nlp = pipeline("question-answering", model=base_model, tokenizer=base_tokenizer, device=0)
        large_nlp = pipeline("question-answering", model=large_model, tokenizer=large_tokenizer, device=0)
    else:
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        base_nlp = pipeline("question-answering", model=base_model, tokenizer=base_tokenizer)
        large_nlp = pipeline("question-answering", model=large_model, tokenizer=large_tokenizer)

    print("\nRunning contracts through models")
    predictions = []
    for idx in tqdm(range(dataset.num_rows)):
        temp = {}
        temp["id"] = dataset[idx]["id"]
        if dataset[idx]['question'] == QUESTION_FOR_LARGE:
            answer = large_nlp(context=dataset[idx]["context"], question=dataset[idx]["question"], top_k=100)
            answer = [ans for ans in answer if ans['score'] >= score_threshold] # and len(ans['answer']) > 2]
        else:
            answer = base_nlp(context=dataset[idx]["context"], question=dataset[idx]["question"])
            if answer['score'] >= score_threshold:
                answer = [answer]
            else:
                answer = []
        temp["scores"] = [ans['score'] for ans in answer]
        temp["prediction_text"] = [ans['answer'] for ans in answer]
        temp["answer_start"] = [ans['start'] for ans in answer]
        temp["answer_end"] = [ans['end'] for ans in answer]
        if len(temp["prediction_text"]) == 0:
            temp["prediction_text"] = [" "]
        predictions.append(temp)
    print()

    predictions = [{'question': pred['id'].partition('__')[2], 'answer': pred['prediction_text'], 'scores': pred['scores'], 'answer_start': pred['answer_start'], 'answer_end': pred['answer_end']} for pred in predictions]
    return predictions

def visualize(predictions, contracts, output_dir, display_score):
    def find_color(score):
        green = '#2bbd35'
        yellow = '#b3bf26'
        red = '#ba1616'
        if score >= 0.5:
            return green
        elif 0.5 > score >= 0.10:
            return yellow
        else:
            return red

    html_results = []
    for idx, contract in enumerate(contracts):
        colors = {}
        options = {'ents': []}
        ents = []
        for color_idx, pred in enumerate(predictions[12*idx:12*(idx+1)]):
            color = COLORS[color_idx]
            for start, end, score in zip(pred['answer_start'], pred['answer_end'], pred['scores']):
                ents.append({
                    'start': start,
                    'end': end,
                    'label': pred['question']
                })
                if display_score and pred['question'] not in colors:
                    colors[pred['question']] = find_color(score)
            options['ents'].append(pred['question'])
            if not display_score:
                colors[pred['question']] = color
        options['colors'] = colors

        html_results.append({
            contract['title']: displacy.render({
                'text': contract['context'],
                'ents': ents,
                'title': None
            }, manual=True, style='ent', options=options)
        })

    for html_result in html_results:
        (filename, html), = html_result.items()
        if output_dir == None:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
                url = 'file://' + f.name
                f.write(html)
            webbrowser.open(url)
        else:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(os.path.join(output_dir, filename + '.html'), 'w+') as f:
                f.write(html)


def main():
    argv = sys.argv
    display_score = False
    output_dir = None
    base_model_name = 'alex-apostolo/legal-bert-base-cuad'
    large_model_name = 'akdeniz27/roberta-large-cuad'
    help_msg = 'contract-reviewer -s -b <alex-apostolo/legal-bert-base-cuad> -l <akdeniz27/roberta-large-cuad> -o <output_dir> ...<files>\ncontract-reviewer -m <alex-apostolo/legal-bert-base-cuad> -o <output_dir> ...<files>'
    try:
        opts, args = getopt.getopt(argv[1:],"shb:l:m:o:",["base-model=","large-model=", "model=", "output="])
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        elif opt == '-s':
            display_score = True
        elif opt in ("-b", "--base-model"):
            base_model_name = arg
        elif opt in ("-l", "--large-model"):
            large_model_name = arg
        elif opt in ("-m", "--model"):
            base_model_name = arg
            large_model_name = arg
        elif opt in ('-o', '--output'):
            output_dir = arg

    paths = args
    if len(paths) == 0:
        print(help_msg)
        sys.exit(2)
    print('Successfully imported modules')
    dataset = create_dataset_from(paths)
    print('Successfully created dataset from contracts')
    predictions = run_model(dataset, base_model_name, large_model_name, score_threshold=0.05)
    print('Successfully ran the NLP model on the dataset')
    visualize(predictions, _read_contracts(paths), output_dir, display_score)