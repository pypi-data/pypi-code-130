from typing import Any, Dict, List, Union

from functools import partial
from s2_wrapper.api.base import BaseEndpoints
from s2_wrapper.api.utils import endpoint
from s2_wrapper.api.academic_graph.v1 import entities

SEARCH_PAPER_FIELDS = [
    "paperId",
    "externalIds",
    "url",
    "title",
    "abstract",
    "venue",
    "year",
    "referenceCount",
    "citationCount",
    "influentialCitationCount",
    "isOpenAccess",
    "fieldsOfStudy",
    "s2FieldsOfStudy",
    "publicationTypes",
    "publicationDate",
    "journal",
    "authors",
]

PAPER_FIELDS = [
    "paperId",
    "externalIds",
    "url",
    "title",
    "abstract",
    "venue",
    "year",
    "referenceCount",
    "citationCount",
    "influentialCitationCount",
    "isOpenAccess",
    "fieldsOfStudy",
    "s2FieldsOfStudy",
    "publicationTypes",
    "publicationDate",
    "journal",
    "authors",
    "citations",
    "references",
    "embedding",
    "tldr",
]
"""Semantic Scholar available paper fields."""

AUTHOR_FIELDS = [
    "authorId",
    "externalIds",
    "name",
    "aliases",
    "affiliations",
    "homepage",
    "paperCount",
    "citationCount",
    "hIndex",
    "papers",
]

CITATION_REFERENCE_DETAILS_FIELDS = [
    "contexts",
    "intents",
    "isInfluential",
    "paperId",
    "corpusId",
    "externalIds",
    "url",
    "title",
    "abstract",
    "venue",
    "year",
    "referenceCount",
    "citationCount",
    "influentialCitationCount",
    "isOpenAccess",
    "fieldsOfStudy",
    "s2FieldsOfStudy",
    "publicationTypes",
    "publicationDate",
    "journal",
    "authors",
]


def details_fields_transform(
    x: Union[List[str], str], allowed_fields: List[str], entity: str
) -> str:
    """Transforms the `fields` argument of `AcademicGraphEndpointsV1.{paper_details,paper_author_details}`
    methods.

    Args:
        x: The `fields` argument of the method.
        allowed_fields: a list containing the allowed fields names.
        entity: the name of the entity to be retrieved.

    Returns:
        The transformed `fields` argument of the method.
    """
    if isinstance(x, str) and x == "all":
        return ",".join(allowed_fields)

    fields = []
    for field in x:
        if field not in allowed_fields:
            raise ValueError(
                f"{field} is not a valid Semantic Scholar {entity} field. Valid fields are: {allowed_fields}"
            )
        fields.append(field)
    return ",".join(fields)


search_paper_details_fields_transform = partial(
    details_fields_transform, allowed_fields=SEARCH_PAPER_FIELDS, entity="paper search"
)

paper_details_fields_transform = partial(
    details_fields_transform, allowed_fields=PAPER_FIELDS, entity="paper"
)

author_details_fields_transform = partial(
    details_fields_transform, allowed_fields=AUTHOR_FIELDS, entity="author"
)

paper_citation_refence_details_fields_transform = partial(
    details_fields_transform,
    allowed_fields=CITATION_REFERENCE_DETAILS_FIELDS,
    entity="citation details",
)


MAX_LIMIT = 1000


def details_limit(x: int) -> int:
    if x > 1000:
        raise ValueError("The value of 'limit' has to <= {MAX_LIMIT}")
    return x


class AcademicGraphEndpointsV1(BaseEndpoints):
    """Semantic Scholar Academic Graph API V1 endpoints."""

    API_PATH = "/graph/v1"

    @endpoint(
        "GET",
        "/paper/search",
        query_params_names={
            "query": None,
            "offset": None,
            "limit": details_limit,
            "fields": search_paper_details_fields_transform,
        },
    )
    def search_paper_by_keyword(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.PaginatedResult[entities.Paper]:
        """Search papers by keyword.

        Args:
            query: A plain-text search query string. No special query syntax is supported.
            offset: when returning a list of results, start with the element at this position
                in the list. The sum of `offset` and `limit` must be < 10000. Defaults to `0`.
            limit: the maximum number of results to return. Must be <= 1000. Defaults to
                `100`.
            fields: The fields of the papers to return.

        Returns:
            List of papers with default or requested fields.
        """
        return entities.PaginatedResult[entities.Paper](**_json)

    @endpoint(
        "GET",
        "/paper/{paper_id}",
        query_params_names={"fields": paper_details_fields_transform},
    )
    def paper_details(
        self,
        paper_id: str,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.Paper:
        """Get details of a paper.

        Args:
            paper_id: The ID of the paper. It can be the Semantic Scholar ID, the Semantic
                Scholar numerical ID, the DOI, the arXiv ID, the MAG ID, the ACL ID, the
                PMID, the PMCID or the URL from semanticscholar.org, arxiv.org, aclweb.org,
                acm.org or biorxiv.org.
            fields: The fields of the paper to return.

        Returns:
            Paper with the default or requested fields.
        """
        return entities.Paper(**_json)

    @endpoint(
        "GET",
        "/paper/{paper_id}/authors",
        query_params_names={
            "offset": None,
            "limit": details_limit,
            "fields": author_details_fields_transform,
        },
    )
    def paper_authors_details(
        self,
        paper_id: str,
        offset: int = 0,
        limit: int = 100,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.PaginatedResult[entities.Author]:
        """Get the authors from a paper.

        Args:
            paper_id: The ID of the paper. It can be the Semantic Scholar ID, the Semantic
                Scholar numerical ID, the DOI, the arXiv ID, the MAG ID, the ACL ID, the
                PMID, the PMCID or the URL from semanticscholar.org, arxiv.org, aclweb.org,
                acm.org or biorxiv.org.
            offset: when returning a list of results, start with the element at this position
                in the list. The sum of `offset` and `limit` must be < 10000. Defaults to `0`.
            limit: the maximum number of results to return. Must be <= 1000. Defaults to
                `100`.
            fields: The fields of the authors to return.

        Returns:
            List of authors with default or requested fields.
        """
        return entities.PaginatedResult[entities.Author](**_json)

    @endpoint(
        "GET",
        "/paper/{paper_id}/citations",
        query_params_names={
            "offset": None,
            "limit": details_limit,
            "fields": paper_citation_refence_details_fields_transform,
        },
    )
    def paper_citations_details(
        self,
        paper_id: str,
        offset: int = 0,
        limit: int = 100,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.PaginatedResult[entities.CitationReferenceDetails]:
        """Get the citations of a paper.

        Args:
            paper_id: The ID of the paper. It can be the Semantic Scholar ID, the Semantic
                Scholar numerical ID, the DOI, the arXiv ID, the MAG ID, the ACL ID, the
                PMID, the PMCID or the URL from semanticscholar.org, arxiv.org, aclweb.org,
                acm.org or biorxiv.org.
            offset: when returning a list of results, start with the element at this position
                in the list. The sum of `offset` and `limit` must be < 10000. Defaults to `0`.
            limit: the maximum number of results to return. Must be <= 1000. Defaults to
                `100`.
            fields: The fields of the citations to return.

        Returns:
            List of citations with default or requested fields.
        """
        return entities.PaginatedResult[entities.CitationReferenceDetails](**_json)

    @endpoint(
        "GET",
        "/paper/{paper_id}/citations",
        query_params_names={
            "offset": None,
            "limit": details_limit,
            "fields": paper_citation_refence_details_fields_transform,
        },
    )
    def paper_references_details(
        self,
        paper_id: str,
        offset: int = 0,
        limit: int = 100,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.PaginatedResult[entities.CitationReferenceDetails]:
        """Get the references of a paper.

        Args:
            paper_id: The ID of the paper. It can be the Semantic Scholar ID, the Semantic
                Scholar numerical ID, the DOI, the arXiv ID, the MAG ID, the ACL ID, the
                PMID, the PMCID or the URL from semanticscholar.org, arxiv.org, aclweb.org,
                acm.org or biorxiv.org.
            offset: when returning a list of results, start with the element at this position
                in the list. The sum of `offset` and `limit` must be < 10000. Defaults to `0`.
            limit: the maximum number of results to return. Must be <= 1000. Defaults to
                `100`.
            fields: The fields of the citations to return.

        Returns:
            List of references with default or requested fields.
        """
        return entities.PaginatedResult[entities.CitationReferenceDetails](**_json)

    @endpoint(
        "GET",
        "/author/search",
        query_params_names={
            "query": None,
            "offset": None,
            "limit": details_limit,
            "fields": author_details_fields_transform,
        },
    )
    def search_author_by_name(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.PaginatedResult[entities.Author]:
        """Search authors by keyword.

        Args:
            query: A plain-text search query string. No special query syntax is supported.
            offset: when returning a list of results, start with the element at this position
                in the list. The sum of `offset` and `limit` must be < 10000. Defaults to `0`.
            limit: the maximum number of results to return. Must be <= 1000. Defaults to
                `100`.
            fields: The fields of the papers to return.

        Returns:
            List of papers with default or requested fields.
        """
        return entities.PaginatedResult[entities.Author](**_json)

    @endpoint(
        "GET",
        "/author/{author_id}",
        query_params_names={"fields": author_details_fields_transform},
    )
    def author_details(
        self,
        author_id: str,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.Author:
        """Get details of an author.

        Args:
            author_id: The Semantic Scholar ID of the author.
            fields: The fields of the author to return.

        Returns:
            Author with the default or requested fields.
        """
        return entities.Author(**_json)

    @endpoint(
        "GET",
        "/author/{author_id}/papers",
        query_params_names={
            "query": None,
            "offset": None,
            "limit": details_limit,
            "fields": search_paper_details_fields_transform,
        },
    )
    def author_papers_details(
        self,
        author_id: str,
        offset: int = 0,
        limit: int = 100,
        fields: Union[List[str], str, None] = None,
        _json: Dict[str, Any] = {},
    ) -> entities.PaginatedResult[entities.Paper]:
        """Fetch the papers of an author in batches.
        
        Args:
            author_id: The Semantic Scholar ID of the author.
            offset: when returning a list of results, start with the element at this position
                in the list. The sum of `offset` and `limit` must be < 10000. Defaults to `0`.
            limit: the maximum number of results to return. Must be <= 1000. Defaults to
                `100`.
            fields: The fields of the author to return.

        Returns:
            List of author papers with default or requested fields.
        """
        return entities.PaginatedResult[entities.Paper](**_json)
