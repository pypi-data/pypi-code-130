

pact_cmd_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "hash": {
      "type": "string"
    },
    "sigs": {
      "type": "array",
      "items": [
        {
          "type": "object",
          "properties": {
            "sig": {
              "type": "string"
            }
          },
          "required": [
            "sig"
          ]
        }
      ]
    },
    "cmd": {
      "type": "string"
    }
  },
  "required": [
    "hash",
    "sigs",
    "cmd"
  ]
}

cmd_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "networkId": {
      "type": "string"
    },
    "payload": {
      "type": "object",
      "properties": {
        "exec": {
          "type": "object",
          "properties": {
            "data": {
              "type": "object",
              "properties": {
                "device_exec": {
                  "type": "object"
                }
              },
              "required": [
                "device_exec"
              ]
            },
            "code": {
              "type": "string"
            }
          },
          "required": [
            "data",
            "code"
          ]
        }
      },
      "required": [
        "exec"
      ]
    },
    "signers": {
      "type": "array",
      "items": {}
    },
    "meta": {
      "type": "object",
      "properties": {
        "sender": {
          "type": "string"
        },
        "creationTime": {
          "type": "integer"
        },
        "gasLimit": {
          "type": "integer"
        },
        "gasPrice": {
          "type": "number"
        },
        "chainId": {
          "type": "string"
        },
        "ttl": {
          "type": "integer"
        }
      },
      "required": [
        "sender",
        "creationTime",
        "gasLimit",
        "gasPrice",
        "chainId",
        "ttl"
      ]
    },
    "nonce": {
      "type": "string"
    }
  },
  "required": [
    "networkId",
    "payload",
    "signers",
    "meta",
    "nonce"
  ]
}
