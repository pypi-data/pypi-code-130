#
# Pyserini: Reproducible IR research with sparse and dense representations
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json

from pyserini.encode import QueryEncoder


class CachedDataQueryEncoder(QueryEncoder):
    def __init__(self, model_name_or_path):
        self.vectors = self._load_from_jsonl(model_name_or_path)

    @staticmethod
    def _load_from_jsonl(path):
        vectors = {}
        with open(path) as f:
            for line in f:
                info = json.loads(line)
                text = info['contents'].strip()
                vec = info['vector']
                vectors[text] = vec
        return vectors

    def encode(self, text, **kwargs):
        return self.vectors[text.strip()]
