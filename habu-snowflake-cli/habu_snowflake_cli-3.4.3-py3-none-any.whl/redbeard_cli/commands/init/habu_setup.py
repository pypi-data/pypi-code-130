from redbeard_cli import snowflake_utils, file_utils
import pkg_resources
from redbeard_cli.commands.init.clean_room_setup import install_clean_room_objects


def init_framework(sf_connection, organization_id: str, customer_account_id: str,
                   share_restrictions: bool, habu_account_id: str):

    sp_sql = file_utils.get_file_contents('sqlfiles/V1_0_0_create.sql')
    snowflake_utils.run_multiple_statements(sf_connection, sp_sql)

    sp_sql = file_utils.get_file_contents('sqlfiles/R__setup_cleanroom_common.sql')
    snowflake_utils.run_query(sf_connection, sp_sql)

    sp_sql = file_utils.get_file_contents('sqlfiles/R__setup_data_connection_objects.sql')
    snowflake_utils.run_query(sf_connection, sp_sql)

    sp_sql = file_utils.get_file_contents('sqlfiles/R__1init_habu_installer.sql')
    snowflake_utils.run_query(sf_connection, sp_sql)

    sp_sql = file_utils.get_file_contents('sqlfiles/R__init_habu_shares.sql')
    snowflake_utils.run_query(sf_connection, sp_sql)

    result = snowflake_utils.fetch_one_query(sf_connection, "CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.INSTALLER()")
    print(result)
    install_clean_room_objects(sf_connection)
    result = snowflake_utils.fetch_one_query(sf_connection, "CALL HABU_CLEAN_ROOM_COMMON.HABU_SCHEMA.INIT_FRAMEWORK('%s', '%s')" % (organization_id, habu_account_id))
    print(result)

    version = pkg_resources.require("habu-snowflake-cli")[0].version

    snowflake_utils.run_query(
        sf_connection,
        """
        merge into HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.APP_METADATA d using (select 'VERSION_INFO' as METADATA_NAME, '%s' as METADATA_VALUE ) s
            on d.METADATA_NAME = s.METADATA_NAME
            when matched then update set d.METADATA_VALUE = s.METADATA_VALUE, d.UPDATED_AT = current_timestamp()
            when not matched then insert (ID, METADATA_NAME, METADATA_VALUE, CREATED_AT) values (uuid_string(), s.METADATA_NAME, s.METADATA_VALUE, current_timestamp()
        );""" % version
    )
    return 0
