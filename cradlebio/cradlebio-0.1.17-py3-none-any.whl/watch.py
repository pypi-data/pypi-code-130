import logging
import threading
from typing import Any, List

from google.cloud import firestore
from google.cloud.firestore_v1.watch import DocumentChange, ChangeType
from tqdm import tqdm
from proto.datetime_helpers import DatetimeWithNanoseconds


def unsubscribe_watch(event, job_watch):
    event.wait()
    job_watch.unsubscribe()


def add_progress_listener(job_doc: firestore.DocumentReference, seq_count: int):
    """ Listens to changes on the job document and sequences in firestore and updates a progress bar. """
    msa_bar = tqdm(desc='MSA ', total=100, unit='%', miniters=1, mininterval=0, ncols=110,
                   bar_format='{l_bar}{bar}|[{unit}]')
    fold_bar = None
    folding_progress = [0 for _ in range(seq_count)]

    event = threading.Event()

    def job_callback(docs: List[firestore.DocumentSnapshot],
                     changes: List[DocumentChange],
                     _: DatetimeWithNanoseconds):
        for document, change in zip(docs, changes):
            if change.type in {ChangeType.MODIFIED}:
                data = document.to_dict()
                if 'status' not in data:
                    continue
                status = data['status']
                if status == 'MSA_QUEUE':
                    msa_bar.unit = 'MSA Queue'.ljust(34)
                    msa_bar.update()
                elif status == 'MSA_RUNNING':
                    data = document.to_dict()
                    if 'msa_progress' not in data:
                        msa_bar.unit = 'MSA Running'.ljust(34)
                        msa_bar.update()
                    else:
                        msa_bar.unit = data['msa_progress']['status'].ljust(34)
                        msa_bar.n = 2 * data['msa_progress']['current']  # MSA progress goes up to 50
                        msa_bar.update(0)
                elif status == 'MSA_COMPLETE':
                    msa_bar.unit = 'MSA Complete'.ljust(34)
                    msa_bar.n = 100
                    msa_bar.close()
                    print('\nFolding is typically slower than MSA (about 15mins/100 AAs). Please be patient!\n')
                    nonlocal fold_bar
                    fold_bar = tqdm(desc='Fold', total=100, unit='%', miniters=1, mininterval=0, ncols=110,
                                    bar_format='{l_bar}{bar}|[{unit}]')
                    for seq in job_doc.collection('sequences').stream():
                        if seq.get('status') == 'DONE':  # cached sequence
                            folding_progress[int(seq.id)] = 10
                elif status == 'FOLD_QUEUE':
                    fold_bar.unit = 'Fold Queue'.ljust(34)
                    fold_bar.update()
                elif status == 'FOLDING':
                    if 'fold_progress' not in data:
                        fold_bar.unit = 'Folding'.ljust(34)
                        fold_bar.update()
                    else:
                        progress = data['fold_progress']['current']
                        seq_id = int(data['fold_progress']['seq_id'])
                        folding_progress[seq_id] = progress
                        if progress > 0:
                            current_progress = sum(folding_progress) / (seq_count * data['fold_progress']['total'])
                            fold_bar.n = 100 * current_progress
                            fold_bar.update(0)  # force refresh
                        action = 'Folding' if progress % 2 == 0 else 'Amber relax'
                        model = min(5, progress // 2 + 1)
                        fold_bar.unit = f'Sequence {seq_id}, model {model}/5, {action}'.ljust(34)
                elif status == 'DONE' or status == 'MSA_FAILED' or status == 'FOLDING_FAILED':
                    bar = msa_bar if fold_bar is None else fold_bar
                    bar.unit = status.ljust(34)
                    bar.n = 100
                    bar.update(0)
                    bar.close()
                    event.set()

    job_watch = job_doc.on_snapshot(job_callback)
    threading.Thread(target=unsubscribe_watch, args=(event, job_watch)).start()


def field(doc: firestore.DocumentReference, *field_names: str) -> Any:
    """
    Watches the given fields in the document for changes and returns when one of the desired
    fields has changed.
    """
    event = threading.Event()
    retval = None

    def callback(docs: List[firestore.DocumentSnapshot],
                 changes: List[DocumentChange],
                 _: DatetimeWithNanoseconds):
        for document, change in zip(docs, changes):
            if change.type in {ChangeType.ADDED, ChangeType.MODIFIED}:
                data = document.to_dict()
                result = {field_name: data[field_name] for field_name in field_names if field_name in data}
                if result:
                    nonlocal retval
                    retval = result
                    event.set()

    doc.on_snapshot(callback)

    result = doc.get(field_names).to_dict()
    if result:  # the document already has the fields we are looking for
        return result

    event.wait()
    return retval
