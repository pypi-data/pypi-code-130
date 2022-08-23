import pytest
import ipytest

import pandas as pd
from tqdm import tqdm
import numpy as np
import urllib
from datetime import date, timedelta
from itertools import permutations
import datetime
import string
from IPython.core.display import display, HTML
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from IPython.display import Image
from IPython import get_ipython
import html2text
import torch
import datasets
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import wandb

from transformers.utils.dummy_pt_objects import TRANSFO_XL_PRETRAINED_MODEL_ARCHIVE_LIST


def identify_tensor_device():
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    return device


def get_datapath(context,run_name=None):
    if context == 'local-drive':
        path_root = '/Volumes/GoogleDrive/My Drive/'
    elif context == 'gdrive':
        path_root = '/content/drive/MyDrive/'

    path_project = path_root+'Data Science/Projects/Vivian-Health/'
    path_data = path_project+'data/'
    path_output = path_project+'artifacts/'

    if run_name is None:
        path_artifact = None
    else:
        path_artifact = path_output+f'{run_name}'

    return path_data,path_output,path_artifact


def retrieve_data(path, index_column, method='filepath'):
    if method == 'filepath':
        data = pd.read_csv(path)
    else:
        raise NotImplementedError(f'Method {method} is not implemented.')
    
    assert data.shape[0] > 0, 'Data file has no rows'
    
    data = data.dropna(subset=[index_column]).set_index(index_column)

    return data

def remove_html_tags(string):
    text_maker = html2text.HTML2Text()
    return text_maker.handle(string)


def concatenate_title_with_description(row,
                                       title_col = 'job_title',
                                       description_col = 'description'):
    """Concatenates job title with the description, also removes HTML tags from description"""
    if pd.notnull(row[title_col]) and pd.notnull(row[description_col]):
        concatenated = f"""title: {row[title_col]}
        description: {remove_html_tags(row[description_col])}""".strip()
    elif pd.notnull(row[title_col]):
        concatenated = f"title: {row[title_col]}"
    elif pd.notnull(row[description_col]):
        concatenated = f"description: {remove_html_tags(row[description_col])}"
    else:
        concatenated = None
    return concatenated

def preprocess(data_df, text_column_name):
    data_df[text_column_name] = data_df.apply(concatenate_title_with_description, axis=1)
    return data_df


def fetch_label_mapping(y_data):
    id2label = {i: name for i, name in enumerate(y_data.names)}
    label2id = {name: i for i, name in enumerate(y_data.names)}
    return id2label, label2id

def split(data, x_col_name, y_col_name, test_size=.33, random_state=42):
    label_is_not_null = data[y_col_name].notnull()
    labelled_data = data.loc[label_is_not_null, [x_col_name, y_col_name]]
    train_df, test_df = train_test_split(labelled_data,
                                         test_size=test_size,
                                         random_state=random_state)

    # Need to see the exact same classes in the train and test.
    assert set(train_df[y_col_name] == set(test_df[y_col_name]))

    dataset = datasets.DatasetDict({'train': datasets.Dataset.from_pandas(train_df),
                                'test': datasets.Dataset.from_pandas(test_df)
                                })
    
    dataset = dataset.rename_column(y_col_name, 'label')
    dataset = dataset.class_encode_column('label')

    id2label, label2id = fetch_label_mapping(dataset['train'].features['label'])

    return dataset, id2label, label2id

def get_tokenizer(pretrained_model_name):
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name)
    return tokenizer

def get_wrapped_tokenizer(tokenizer, max_sequence_length=512, tokenizer_kwargs={}):
    def tokenize_data(examples):
        if max_sequence_length is not None:
            encoding = tokenizer(examples['text'], **tokenizer_kwargs)
        else:
            encoding = tokenizer(examples['text'], **tokenizer_kwargs)
        encoding['token_count'] = [np.sum(x) for x in encoding['attention_mask']]
        if max_sequence_length is not None:
            encoding['is_max_count'] = [x == max_sequence_length for x in encoding['token_count']]
        return encoding
    return tokenize_data


def initialize_pretrained_model(pretrained_model_name, device,
                                id2label, label2id):
    model = AutoModelForSequenceClassification\
        .from_pretrained(pretrained_model_name,
                            num_labels=len(id2label),
                            id2label=id2label,
                            label2id=label2id)\
        .to(device)
    return model


def compute_accuracy(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy_metric = datasets.load_metric('accuracy')
    return accuracy_metric.compute(predictions=predictions, references=labels)

def preds_to_fake_probs(preds):
    ilogit_preds = 1 / (1 + np.exp(-preds))
    ilogit_preds_normalized = ilogit_preds / np.sum(ilogit_preds, axis=1)[:, None]
    return ilogit_preds_normalized


def compute_auc(eval_pred):
    logits, labels = eval_pred
    scores = preds_to_fake_probs(logits)
    auc_multiclass_metric = datasets.load_metric('roc_auc', 'multiclass')
    return auc_multiclass_metric.compute(prediction_scores=scores, references=labels, multi_class='ovr')


def train_model(dataset, pretrained_model_name, device, id2label, label2id,
                artifact_dir, compute_metrics, model_kwargs={}, training_kwargs={}, trainer_kwargs={}):
    
    model = initialize_pretrained_model(pretrained_model_name, device,
                                id2label, label2id)

    training_args = TrainingArguments(output_dir=artifact_dir, **training_kwargs)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset['train'],
        eval_dataset=dataset['test'],
        compute_metrics=compute_metrics,
    )

    return trainer

def get_predictions(trainer, data):
    predictions, label_ids, metrics = trainer.predict(data)
    return predictions, label_ids, metrics


def threshold_curve(preds, label_ids, n_ntiles=10):
    correct = np.argmax(preds, axis=1) == label_ids
    fake_probs = preds_to_fake_probs(preds)
    confidences = np.max(fake_probs, axis=1)
    ntile, bins = pd.qcut(confidences, n_ntiles, labels=False, retbins=True)

    results = []
    for i in range(n_ntiles):
        count = np.sum(ntile >= i)
        accuracy = np.mean(correct[ntile >= i])
        results.append({'ntile': i,
                      'proportion': count / len(preds),
                      'accuracy': accuracy})
    return pd.DataFrame(results)

def truncate_words(text,max_lenght=510,opt='right'):
    if len(text.split())<=max_lenght:
        return text
    else:
        return ' '.join(text.split()[:max_lenght])