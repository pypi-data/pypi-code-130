# -*- coding: utf-8 -*-

from amazon_ad.api_v3.base import ZADOpenAPIV3


class SpReportV3(ZADOpenAPIV3):

    def request(self, data: dict):
        """
        :param data: 请求体
        :return:
        """
        path = "/reporting/reports"
        return self.post(path, data)

    def sp_campaigns(self, start_date, end_date, **kwargs):
        """SponsoredProductsCampaignsWithPlacementSummaryReport
        :param start_date: "2022-07-01"
        :param end_date: "2022-07-04"
        :return:
        """
        data = {
            "value": {
                "startDate": start_date,
                "endDate": end_date,
                "configuration": {
                    "adProduct": "SPONSORED_PRODUCTS",
                    "columns": [
                        "impressions",
                        "clicks",
                        "cost",
                        "purchases1d",
                        "purchases7d",
                        "purchases14d",
                        "purchases30d",
                        "purchasesSameSku1d",
                        "purchasesSameSku7d",
                        "purchasesSameSku14d",
                        "purchasesSameSku30d",
                        "unitsSoldClicks1d",
                        "unitsSoldClicks7d",
                        "unitsSoldClicks14d",
                        "unitsSoldClicks30d",
                        "sales1d",
                        "sales7d",
                        "sales14d",
                        "sales30d",
                        "attributedSalesSameSku1d",
                        "attributedSalesSameSku7d",
                        "attributedSalesSameSku14d",
                        "attributedSalesSameSku30d",
                        "unitsSoldSameSku1d",
                        "unitsSoldSameSku7d",
                        "unitsSoldSameSku14d",
                        "unitsSoldSameSku30d",
                        "kindleEditionNormalizedPagesRead14d",
                        "kindleEditionNormalizedPagesRoyalties14d",
                        "startDate",
                        "endDate",
                        "campaignBiddingStrategy",
                        "costPerClick",
                        "clickThroughRate",
                        "spend",
                        "campaignName",
                        "campaignId",
                        "campaignStatus",
                        "campaignBudgetType",
                        "campaignBudgetAmount",
                        "campaignRuleBasedBudgetAmount",
                        "campaignApplicableBudgetRuleId",
                        "campaignApplicableBudgetRuleName",
                        "campaignBudgetCurrencyCode"
                    ],
                    "reportTypeId": "spCampaigns",
                    "format": "GZIP_JSON",
                    "groupBy": [
                        "campaign",
                        "campaignPlacement"
                    ],
                    "filters": [
                        {
                            "field": "campaignStatus",
                            "values": [
                                "ENABLED",
                                "PAUSED",
                                "ARCHIVED"
                            ]
                        }
                    ],
                    "timeUnit": "SUMMARY"
                },
                "name": f"SponsoredProductsCampaignsWithPlacementSummaryReport_{start_date}_{end_date}"
            }
        }
        return self.request(data)
