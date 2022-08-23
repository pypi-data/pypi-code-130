'''
# Halloumi Cross Account Parameter Store

A custom CDK construct to manage a parameter across an AWS account. This construct creates a Lambda-backed custom resource using AWS CloudFormation that handles assuming a role on the target AWS account and puts, updates or deletes a parameter on that account. Role and parameter related variables are passed to the construct and are used by the function to perform these operations.

## Usage

```python
import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {
  HalloumiCrossAccountParameterStore,
  CustomResourceProvider,
} from 'halloumi-cross-account-parameter-store';

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    const provider = new CustomResourceProvider(
      this,
      'CrossAccountParameterStoreCustomResourceProvider',
      {
        roleArn: 'arn:aws:iam::123412341234:role/role-name',
        roleExternalId: '',
        roleSessionName: '',
      }
    );

    new HalloumiCrossAccountParameterStore(this, 'Parameter1', {
      customResourceProvider: provider,
      parameterName: '/some/parameter/name',
      parameterValue: 'some-value',
      parameterDescription: 'my-description',
    });

    new HalloumiCrossAccountParameterStore(this, 'Parameter2', {
      customResourceProvider: provider,
      parameterName: '/some/parameter/name2',
      parameterValue: 'some-value-2',
      parameterDescription: 'my-description',
    });
  }
}
```

**Note: You only need to define the `CustomResourceProvider` once and pass it to the `HalloumiCrossAccountParameterStore` constructor of your new instance. If you need to assume different roles, create a new instance of the `CustomResourceProvider` and use it accordingly.**

## Setting Up Trust Relationship and the Permissions

The Lambda function role needs to have permission to assume the role in the target account and perform `ssm:PutParameter` and `ssm:DeleteParameter` actions. Here's what you need to do to setup the IAM role on the target account that allows the function role on `111111111111` account to create, update or delete parameters with a prefix of `/halloumi-cross-account/` on `eu-central-1` region. Be sure to adjust the values accordingly.

Trust relationship policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111111111111:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "SET_OR_REMOVE_THE_CONDITION_AND_EXTERNAL_ID_ACCORDINGLY"
        }
      }
    }
  ]
}
```

Policy Document:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPutDeleteParameterWithPrefix",
      "Effect": "Allow",
      "Action": ["ssm:PutParameter", "ssm:DeleteParameter"],
      "Resource": "arn:aws:ssm:eu-central-1:YOUR_SANDBOX_ACCOUNT_ID:parameter/halloumi-cross-account/*"
    }
  ]
}
```

For more information, please check the [API Doc](API.md)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.custom_resources
import constructs


class CustomResourceProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="halloumi-cross-account-parameter-store.CustomResourceProvider",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role_arn: builtins.str,
        role_external_id: typing.Optional[builtins.str] = None,
        role_session_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param role_arn: The ARN of the role on the target account that the STS client on the Lambda function assumes and has permissions to create, update and delete a parameter on that account.
        :param role_external_id: Optional: Information that you can use in an IAM role trust policy to designate who can assume the role.
        :param role_session_name: Optional: IAM role session name when STS client on the Lambda function assumes the role on the target account. Default is ``halloumi_cross_account_parameter_store``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CustomResourceProvider.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FunctionProps(
            role_arn=role_arn,
            role_external_id=role_external_id,
            role_session_name=role_session_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="gProviderFramework")
    def g_provider_framework(self) -> aws_cdk.custom_resources.Provider:
        return typing.cast(aws_cdk.custom_resources.Provider, jsii.invoke(self, "gProviderFramework", []))


class FunctionConstruct(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="halloumi-cross-account-parameter-store.FunctionConstruct",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role_arn: builtins.str,
        role_external_id: typing.Optional[builtins.str] = None,
        role_session_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param role_arn: The ARN of the role on the target account that the STS client on the Lambda function assumes and has permissions to create, update and delete a parameter on that account.
        :param role_external_id: Optional: Information that you can use in an IAM role trust policy to designate who can assume the role.
        :param role_session_name: Optional: IAM role session name when STS client on the Lambda function assumes the role on the target account. Default is ``halloumi_cross_account_parameter_store``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(FunctionConstruct.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FunctionProps(
            role_arn=role_arn,
            role_external_id=role_external_id,
            role_session_name=role_session_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="gFunction")
    def g_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''Get the function.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.invoke(self, "gFunction", []))

    @jsii.member(jsii_name="gFunctionRole")
    def g_function_role(self) -> aws_cdk.aws_iam.IRole:
        '''Get the IAM Role attached to the function.'''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.invoke(self, "gFunctionRole", []))


@jsii.data_type(
    jsii_type="halloumi-cross-account-parameter-store.FunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "role_external_id": "roleExternalId",
        "role_session_name": "roleSessionName",
    },
)
class FunctionProps:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        role_external_id: typing.Optional[builtins.str] = None,
        role_session_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: The ARN of the role on the target account that the STS client on the Lambda function assumes and has permissions to create, update and delete a parameter on that account.
        :param role_external_id: Optional: Information that you can use in an IAM role trust policy to designate who can assume the role.
        :param role_session_name: Optional: IAM role session name when STS client on the Lambda function assumes the role on the target account. Default is ``halloumi_cross_account_parameter_store``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(FunctionProps.__init__)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument role_external_id", value=role_external_id, expected_type=type_hints["role_external_id"])
            check_type(argname="argument role_session_name", value=role_session_name, expected_type=type_hints["role_session_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
        }
        if role_external_id is not None:
            self._values["role_external_id"] = role_external_id
        if role_session_name is not None:
            self._values["role_session_name"] = role_session_name

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''The ARN of the role on the target account that the STS client on the Lambda function assumes and has permissions to create, update and delete a parameter on that account.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_external_id(self) -> typing.Optional[builtins.str]:
        '''Optional: Information that you can use in an IAM role trust policy to designate who can assume the role.'''
        result = self._values.get("role_external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_session_name(self) -> typing.Optional[builtins.str]:
        '''Optional: IAM role session name when STS client on the Lambda function assumes the role on the target account.

        Default is ``halloumi_cross_account_parameter_store``.
        '''
        result = self._values.get("role_session_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HalloumiCrossAccountParameterStore(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="halloumi-cross-account-parameter-store.HalloumiCrossAccountParameterStore",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        custom_resource_provider: CustomResourceProvider,
        parameter_description: builtins.str,
        parameter_name: builtins.str,
        parameter_value: typing.Any,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param custom_resource_provider: An instance of the ``CustomResourceProvider``.
        :param parameter_description: A description for the parameter.
        :param parameter_name: The name of the parameter on the target account that is going to be managed.
        :param parameter_value: The value of the parameter on the target account.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(HalloumiCrossAccountParameterStore.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ParameterManagerProps(
            custom_resource_provider=custom_resource_provider,
            parameter_description=parameter_description,
            parameter_name=parameter_name,
            parameter_value=parameter_value,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createParameterManager")
    def create_parameter_manager(self, id: builtins.str) -> aws_cdk.CustomResource:
        '''
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(HalloumiCrossAccountParameterStore.create_parameter_manager)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(aws_cdk.CustomResource, jsii.invoke(self, "createParameterManager", [id]))


@jsii.data_type(
    jsii_type="halloumi-cross-account-parameter-store.ParameterManagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "custom_resource_provider": "customResourceProvider",
        "parameter_description": "parameterDescription",
        "parameter_name": "parameterName",
        "parameter_value": "parameterValue",
    },
)
class ParameterManagerProps:
    def __init__(
        self,
        *,
        custom_resource_provider: CustomResourceProvider,
        parameter_description: builtins.str,
        parameter_name: builtins.str,
        parameter_value: typing.Any,
    ) -> None:
        '''
        :param custom_resource_provider: An instance of the ``CustomResourceProvider``.
        :param parameter_description: A description for the parameter.
        :param parameter_name: The name of the parameter on the target account that is going to be managed.
        :param parameter_value: The value of the parameter on the target account.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(ParameterManagerProps.__init__)
            check_type(argname="argument custom_resource_provider", value=custom_resource_provider, expected_type=type_hints["custom_resource_provider"])
            check_type(argname="argument parameter_description", value=parameter_description, expected_type=type_hints["parameter_description"])
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        self._values: typing.Dict[str, typing.Any] = {
            "custom_resource_provider": custom_resource_provider,
            "parameter_description": parameter_description,
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
        }

    @builtins.property
    def custom_resource_provider(self) -> CustomResourceProvider:
        '''An instance of the ``CustomResourceProvider``.'''
        result = self._values.get("custom_resource_provider")
        assert result is not None, "Required property 'custom_resource_provider' is missing"
        return typing.cast(CustomResourceProvider, result)

    @builtins.property
    def parameter_description(self) -> builtins.str:
        '''A description for the parameter.'''
        result = self._values.get("parameter_description")
        assert result is not None, "Required property 'parameter_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''The name of the parameter on the target account that is going to be managed.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_value(self) -> typing.Any:
        '''The value of the parameter on the target account.'''
        result = self._values.get("parameter_value")
        assert result is not None, "Required property 'parameter_value' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ParameterManagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CustomResourceProvider",
    "FunctionConstruct",
    "FunctionProps",
    "HalloumiCrossAccountParameterStore",
    "ParameterManagerProps",
]

publication.publish()
