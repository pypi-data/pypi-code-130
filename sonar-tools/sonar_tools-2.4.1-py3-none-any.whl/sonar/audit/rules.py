#
# sonar-tools
# Copyright (C) 2019-2022 Olivier Korach
# mailto:olivier.korach AT gmail DOT com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import enum
import json
from sonar.audit import severities, types
import sonar.utilities as util

__RULES = {}


class RuleId(enum.Enum):
    DEFAULT_ADMIN_PASSWORD = 1
    BELOW_LTS = 2
    LOG4SHELL_WEB = 3
    LOG4SHELL_CE = 4
    LOG4SHELL_ES = 5
    BELOW_LATEST = 6
    LTS_PATCH_MISSING = 7

    SETTING_FORCE_AUTH = 100
    SETTING_PROJ_DEFAULT_VISIBILITY = 101
    SETTING_CPD_CROSS_PROJECT = 102

    SETTING_NOT_SET = 110
    SETTING_SET = 111
    SETTING_VALUE_INCORRECT = 112
    SETTING_VALUE_OUT_OF_RANGE = 113

    SETTING_BASE_URL = 120
    SETTING_DB_CLEANER = 121
    SETTING_MAINT_GRID = 122
    SETTING_SLB_RETENTION = 123
    SETTING_TD_LOC_COST = 124

    SETTING_WEB_HEAP = 130
    SETTING_ES_HEAP = 131
    SETTING_CE_HEAP = 132
    SETTING_CE_TOO_MANY_WORKERS = 133
    SETTING_JDBC_URL_NOT_SET = 134
    SETTING_DB_ON_SAME_HOST = 135

    SETTING_WEB_NO_HEAP = 140
    SETTING_ES_NO_HEAP = 141
    SETTING_CE_NO_HEAP = 142

    ANYONE_WITH_GLOBAL_PERMS = 150
    SONAR_USERS_WITH_ELEVATED_PERMS = 151
    FAILED_WEBHOOK = 152

    DCE_DIFFERENT_APP_NODES_VERSIONS = 160
    DCE_DIFFERENT_APP_NODES_PLUGINS = 161
    DCE_APP_NODE_UNOFFICIAL_DISTRO = 162
    DCE_APP_NODE_NOT_GREEN = 163
    DCE_APP_CLUSTER_NOT_HA = 164
    DCE_ES_CLUSTER_NOT_HA = 170
    DCE_ES_UNBALANCED_INDEX = 171
    DCE_ES_INDEX_EMPTY = 172
    DCE_ES_CLUSTER_WRONG_NUMBER_OF_NODES = 173
    DCE_ES_CLUSTER_EVEN_NUMBER_OF_NODES = 174

    BACKGROUND_TASKS_FAILURE_RATE_HIGH = 200
    BACKGROUND_TASKS_PENDING_QUEUE_LONG = 201
    BACKGROUND_TASKS_PENDING_QUEUE_VERY_LONG = 202

    PROJ_LAST_ANALYSIS = 1000
    PROJ_NOT_ANALYZED = 1001
    PROJ_VISIBILITY = 1002
    PROJ_DUPLICATE = 1003

    BRANCH_LAST_ANALYSIS = 1020
    PULL_REQUEST_LAST_ANALYSIS = 1030

    PROJ_PERM_MAX_USERS = 1100
    PROJ_PERM_MAX_ADM_USERS = 1101
    PROJ_PERM_MAX_ISSUE_ADM_USERS = 1102
    PROJ_PERM_MAX_HOTSPOT_ADM_USERS = 1103
    PROJ_PERM_MAX_SCAN_USERS = 1104

    PROJ_PERM_MAX_GROUPS = 1200
    PROJ_PERM_MAX_ADM_GROUPS = 1201
    PROJ_PERM_MAX_ISSUE_ADM_GROUPS = 1202
    PROJ_PERM_MAX_HOTSPOT_ADM_GROUPS = 1203
    PROJ_PERM_MAX_SCAN_GROUPS = 1204
    PROJ_PERM_SONAR_USERS_ELEVATED_PERMS = 1205
    PROJ_PERM_ANYONE = 1206

    PROJ_UTILITY_LOCS = 1300
    PROJ_SUSPICIOUS_EXCLUSION = 1301
    PROJ_DUPLICATE_BINDING = 1302
    PROJ_INVALID_BINDING = 1303
    PROJ_ZERO_LOC = 1304
    PROJ_SCM_DISABLED = 1305
    PROJ_MAIN_AND_MASTER = 1306
    PROJ_ANALYSIS_WARNING = 1307
    BG_TASK_FAILED = 1308
    OBSOLETE_SCANNER = 1309
    NOT_LATEST_SCANNER = 1310

    NOT_USING_BRANCH_ANALYSIS = 1400
    UNDETECTED_SCM = 1401

    QG_NO_COND = 2000
    QG_TOO_MANY_COND = 2001
    QG_NOT_USED = 2002
    QG_TOO_MANY_GATES = 2003
    QG_WRONG_METRIC = 2004
    QG_WRONG_THRESHOLD = 2005

    QP_TOO_MANY_QP = 3000
    QP_LAST_USED_DATE = 3001
    QP_LAST_CHANGE_DATE = 3002
    QP_TOO_FEW_RULES = 3003
    QP_NOT_USED = 3004
    QP_USE_DEPRECATED_RULES = 3005

    TOKEN_TOO_OLD = 4000
    TOKEN_UNUSED = 4001
    TOKEN_NEVER_USED = 4002
    USER_UNUSED = 4010

    PORTFOLIO_EMPTY = 5000
    PORTFOLIO_SINGLETON = 5001

    APPLICATION_EMPTY = 5100
    APPLICATION_SINGLETON = 5101

    GROUP_EMPTY = 5200

    def __str__(self):
        return repr(self.name)[1:-1]


class RuleConfigError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class Rule:
    def __init__(self, rule_id, severity, rule_type, concerned_object, message):
        self.id = to_id(rule_id)
        self.severity = severities.to_severity(severity)
        self.type = types.to_type(rule_type)
        self.object = concerned_object
        self.msg = message


def to_id(val):
    for enum_val in RuleId:
        if repr(enum_val.name)[1:-1] == val:
            return enum_val
    return None


def load():
    global __RULES
    import pathlib

    util.logger.info("Loading audit rules")
    path = pathlib.Path(__file__).parent
    with open(path / "rules.json", "r", encoding="utf-8") as rulefile:
        rules = json.loads(rulefile.read())
    rulefile.close()
    __RULES = {}
    for rule_id, rule in rules.items():
        if to_id(rule_id) is None:
            raise RuleConfigError(f"Rule '{rule_id}' from rules.json is not a legit ruleId")
        if types.to_type(rule.get("type", "")) is None:
            raise RuleConfigError(f"Rule '{rule_id}' from rules.json has no or incorrect type")
        if severities.to_severity(rule.get("severity", "")) is None:
            raise RuleConfigError(f"Rule '{rule_id}' from rules.json has no or incorrect severity")
        if "message" not in rule:
            raise RuleConfigError(f"Rule '{rule_id}' from rules.json has no message defined'")
        __RULES[to_id(rule_id)] = Rule(
            rule_id,
            rule["severity"],
            rule["type"],
            rule.get("object", ""),
            rule["message"],
        )

    # Cross check that all rule Ids are defined in the JSON
    for rule in RuleId:
        if rule not in __RULES:
            raise RuleConfigError(f"Rule {rule} has no configuration defined in 'rules.json'")


def get_rule(rule_id):
    return __RULES[rule_id]
