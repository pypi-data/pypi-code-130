# -*- coding: UTF-8 -*-
#   Copyright 2009-2022 Fumail Project
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
#

DISTRO_NONE = 0
DISTRO_ELASTIC = 1
DISTRO_OPEN = 2


HAVE_ELASTICSEARCH = DISTRO_NONE
try:
    import elasticsearch as elasticclientlib
    ElasticClient = elasticclientlib.Elasticsearch
    ElasticException = elasticclientlib.exceptions.ElasticsearchException
    HAVE_ELASTICSEARCH = DISTRO_ELASTIC
except ImportError:
    try:
        import opensearchpy as elasticclientlib
        ElasticClient = elasticclientlib.OpenSearch
        ElasticException = elasticclientlib.exceptions.OpenSearchException
        HAVE_ELASTICSEARCH = DISTRO_OPEN
    except ImportError:
        elasticclientlib = None
        ElasticClient = None
        class ElasticException(Exception):
            pass


def lint_elastic():
    if HAVE_ELASTICSEARCH == DISTRO_NONE:
        print('ERROR: elasticsearch or opensearch library not available')
        return False
    elif HAVE_ELASTICSEARCH == DISTRO_ELASTIC:
        print('INFO: Elastic Distro is ElasticSearch, library version %s' % elasticclientlib.__versionstr__)
    elif HAVE_ELASTICSEARCH == DISTRO_OPEN:
        print('INFO: Elastic Distro is OpenSearch, library version %s' % elasticclientlib.__versionstr__)
    return True
