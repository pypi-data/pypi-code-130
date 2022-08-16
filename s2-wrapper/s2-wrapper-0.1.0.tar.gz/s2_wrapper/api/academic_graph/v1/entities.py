from typing import Any, Dict, Generic, List, TypeVar, Union

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


class Author(BaseModel):
    """A class containing the information of a Semantic Scholar author."""

    author_id: Union[str, None] = Field(alias="authorId")
    external_ids: Union[Dict[str, List[str]], None] = Field(alias="externalIds")
    url: Union[str, None] = Field(alias="url")
    name: Union[str, None] = Field(alias="name")
    aliases: Union[List[str], None] = Field(alias="aliases")
    affiliations: Union[List[str], None] = Field(alias="affiliations")
    homepage: Union[str, None] = Field(alias="homepage")
    paper_count: Union[int, None] = Field(alias="paperCount")
    citation_count: Union[int, None] = Field(alias="citationCount")
    h_index: Union[str, None] = Field(alias="hIndex")
    papers: Union[List["Paper"], None] = Field(alias="papers")


class S2FieldOfStudy(BaseModel):
    """A class containing the informatoin of Semantic Scholar paper field of study."""

    category: str
    source: str


class Embedding(BaseModel):
    """A class containing the information of a Semantic Scholar paper embedding generated
    using SPECTER model."""

    model: str
    vector: List[float]


class TLDR(BaseModel):
    """A class containing the information of a Semantic Scholar auto-generated summary of
    the paper from the SciTLDR model."""

    model: str
    text: str


class Paper(BaseModel):
    """A class containing the information of a Semantic Scholar paper."""

    paper_id: Union[str, None] = Field(alias="paperId")
    corpus_id: Union[str, None] = Field(alias="corpusId")
    external_ids: Union[Dict[str, str], None] = Field(alias="externalIds")
    url: Union[str, None] = Field(alias="url")
    title: Union[str, None] = Field(None, alias="title")
    abstract: Union[str, None] = Field(alias="abstract")
    venue: Union[str, None] = Field(alias="venue")
    year: Union[int, None] = Field(alias="year")
    reference_count: Union[int, None] = Field(alias="referenceCount")
    citation_count: Union[int, None] = Field(alias="citationCount")
    influential_citation_count: Union[int, None] = Field(
        alias="influentialCitationCount"
    )
    is_open_access: Union[bool, None] = Field(alias="isOpenAccess")
    fields_of_study: Union[List[str], None] = Field(alias="fieldsOfStudy")
    s2_fields_of_study: Union[List[S2FieldOfStudy], None] = Field(
        alias="s2FieldsOfStudy"
    )
    publication_types: Union[List[str], None] = Field(alias="publicationTypes")
    publication_date: Union[str, None] = Field(alias="publicationDate")
    journal: Union[Dict[str, Any], None] = Field(alias="journal")
    authors: Union[List[Author], None] = Field(alias="authors")
    citations: Union[List["Paper"], None] = Field(alias="citations")
    references: Union[List["Paper"], None] = Field(alias="references")
    embedding: Union[Embedding, None] = Field(alias="embedding")
    tldr: Union[TLDR, None] = Field(alias="tldr")


class CitationReferenceDetails(BaseModel):
    """A class containing the information of a Semantic Scholar citation/reference details."""

    contexts: Union[List[str], None] = Field(alias="contexts")
    intents: Union[List[str], None] = Field(alias="intents")
    is_influential: Union[bool, None] = Field(alias="isInfluential")
    citing_paper: Union["Paper", None] = Field(alias="citingPaper")


T = TypeVar("T")


class PaginatedResult(GenericModel, Generic[T]):
    """A class containing a paginated result from Semantic Scholar API."""

    offset: int
    next: Union[int, None]
    data: List[T]


Author.update_forward_refs()