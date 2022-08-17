"""
Dashboard Enums and Models are from:
https://e360-dashboard-service-dev.internal.imsglobal.com/wrapper/documents
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BaseDashboardModel(BaseModel):
    def dump(self) -> dict:
        return json.loads(self.json(by_alias=True))

    class Config:
        use_enum_values = True


class DashboardStatus(str, Enum):
    UNLOCKED = "unlocked"
    LOCKED = "locked"


class TileType(str, Enum):
    STATIC_TEXT = "staticText"
    IMAGE = "image"
    CODELIST_SUMMARY = "codelistSummary"
    DOCUMENT = "document"
    COHORT_DETAILS = "cohortDetails"
    LINK = "link"
    COHORT_GENDER_BREAKDOWN = "cohortGenderBreakdown"
    COHORT_AGE_BREAKDOWN = "cohortAgeBreakdown"
    COHORT_GENDER_AGE_BREAKDOWN = "cohortGenderAgeBreakdown"
    STACK_EVENT_DISTRIBUTION = "stackEventDistribution"
    COHORT_GEOGRAPHIC_BREAKDOWN = "cohortGeographicBreakdown"
    ANALYTIC = "analytic"
    VISUALISATION_PREVIEW = "visualisationPreview"
    SUBHEADING = "subheading"
    COHORT_PREVIEW_DETAILS = "cohortPreviewDetails"
    COHORT_PREVIEW_GENDER_BREAKDOWN = "cohortPreviewGenderBreakdown"
    COHORT_PREVIEW_AGE_BREAKDOWN = "cohortPreviewAgeBreakdown"
    COHORT_PREVIEW_GENDER_AGE_BREAKDOWN = "cohortPreviewGenderAgeBreakdown"
    COHORT_PREVIEW_EVENT_DISTRIBUTION = "cohortPreviewEventDistribution"
    COHORT_PREVIEW_GEOGRAPHIC_BREAKDOWN = "cohortPreviewGeographicBreakdown"


class TileConfigurationModel(BaseDashboardModel):
    title: Optional[str] = None
    showTitle: Optional[bool] = None
    colourTheme: Optional[str] = None
    showBorder: Optional[bool] = None


class TileModel(BaseDashboardModel):
    internalId: Optional[int] = 0
    tileIndex: Optional[int] = 0
    assetId: Optional[UUID] = None
    width: Optional[int] = 0
    height: Optional[int] = 0
    x: Optional[int] = 0
    y: Optional[int] = 0
    version: Optional[int] = None
    tileType: Optional[TileType] = TileType.STATIC_TEXT
    tileConfiguration: Optional[TileConfigurationModel] = None
    breakdownConfiguration: Optional[Dict[str, Any]] = None


class DashboardModel(BaseDashboardModel):
    dashboardStatus: Optional[DashboardStatus] = DashboardStatus.UNLOCKED
    tiles: Optional[List[TileModel]] = Field(default_factory=list)
    id: Optional[int] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class ErrorMessageModel(BaseDashboardModel):
    message: Optional[str] = None
    errorCode: Optional[str] = None
    details: Optional[List[str]] = Field(default_factory=list)


class TabModel(BaseDashboardModel):
    internalId: Optional[int] = None
    tabIndex: Optional[int] = 0
    title: Optional[str] = None
    tiles: Optional[List[TileModel]] = Field(default_factory=list)


class TabbedDashboardModel(BaseDashboardModel):
    """Dashboard with tabs for v2 endpoint"""

    dashboardStatus: Optional[DashboardStatus] = DashboardStatus.UNLOCKED
    tabs: Optional[List[TabModel]] = Field(default_factory=list)
    id: Optional[int] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class VisualisationPublishRequestModel(BaseDashboardModel):
    visualisationResourceId: Optional[UUID] = None
    title: Optional[str] = None
    version: Optional[int] = None


class PublishedDashboardRequestModel(BaseDashboardModel):
    originalDashboardId: Optional[int] = None
    id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[str] = None
    visualizations: Optional[Dict[str, VisualisationPublishRequestModel]] = None
    assetData: Optional[Dict[str, Any]] = None
    isPreview: Optional[bool] = None


class PublishedTileModel(BaseDashboardModel):
    version: Optional[int] = None
    tileIndex: Optional[int] = None
    assetId: Optional[UUID] = None
    width: Optional[int] = None
    height: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    tileType: Optional[TileType] = TileType.STATIC_TEXT
    tileConfiguration: Optional[TileConfigurationModel] = None
    breakdownConfiguration: Optional[Dict[str, Any]] = None


class PublishedTabModel(BaseDashboardModel):
    tabIndex: Optional[int] = None
    title: Optional[str] = None
    tiles: Optional[List[PublishedTileModel]] = Field(default_factory=list)


class PublishedTabModelDashboardModel(BaseDashboardModel):
    dashboardStatus: Optional[DashboardStatus] = DashboardStatus.UNLOCKED
    tabs: Optional[List[PublishedTabModel]] = Field(default_factory=list)
    id: Optional[int] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class DashboardUserModel(BaseDashboardModel):
    email: Optional[str] = None
    accessToken: Optional[str] = None
    createDate: Optional[datetime] = None


class DashboardUserStatisticsEntryModel(BaseDashboardModel):
    viewedDate: Optional[datetime] = None
    ip: Optional[str] = None
    accessToken: Optional[str] = None


class DashboardUserStatisticsModel(BaseDashboardModel):
    viewed: Optional[int] = None
    lastViewed: Optional[datetime] = None
    history: Optional[List[DashboardUserStatisticsEntryModel]] = Field(
        default_factory=list
    )


class PublishedDashboardModel(BaseDashboardModel):
    dashboard: Optional[PublishedTabModelDashboardModel] = None
    users: Optional[Dict[str, DashboardUserModel]] = None
    statistics: Optional[Dict[str, DashboardUserStatisticsModel]] = None
    name: Optional[str] = None
    type: Optional[str] = None
    assetData: Optional[Dict[str, Any]] = None
    version: Optional[int] = None
    isPreview: Optional[bool] = None
    id: Optional[UUID] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class DashboardUserViewModel(BaseDashboardModel):
    email: Optional[str] = None
    ip: Optional[str] = None
    accessToken: Optional[str] = None


class TileTypeModel(BaseDashboardModel):
    name: Optional[str] = None
    description: Optional[str] = None
    minimumHeight: Optional[int] = None
    maximumHeight: Optional[int] = None
    minimumWidth: Optional[int] = None
    maximumWidth: Optional[int] = None
    defaultHeight: Optional[int] = None
    defaultWidth: Optional[int] = None
    assetType: Optional[str] = None
    id: Optional[TileType] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
