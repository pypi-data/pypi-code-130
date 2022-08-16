# #!/usr/bin/env python3
#
# import json
#
# import lhub_cli
#
# # ToDo Figure out how to set these dynamically so different testers can have different inputs, and so that log level can be changed
# LOG_LEVEL = "INFO"
# DEFAULT_INSTANCE_NAME = "lh-lab-chad.dev.logichub.io"
#
# # If the instance name does not already exist as a saved connection, this will assist the user in saving a new one.
# cli = lhub_cli.LogicHubCLI(
#     instance_name=DEFAULT_INSTANCE_NAME,
#
#     # If the --debug option was passed by the user, set log level to debug, otherwise leave it default
#     log_level=LOG_LEVEL or None
# )
#
# # Choose the API call or Action to execute
# # Direct API calls:
# #   cli.session.api
# # Predefined actions for multiple calls or customized output:
# #   cli.session.actions
# # Examples:
# #   cli.session.api.list_fields()
# #   cli.session.api.list_playbooks()
# #   cli.session.api.list_streams()
# #   vs.
# #   cli.session.actions.list_fields(map_mode="name")
# #   cli.session.actions.list_playbooks(map_mode="id")
# #   cli.session.actions.list_streams()
# results = cli.session.actions.list_streams(search_text="met", verify_stream_states=True)
#
# # print(json.dumps(results, indent=2))
# print(json.dumps(results))
