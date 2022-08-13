'''
# Eventbridge SaaS Partner fURLs

This CDK Construct library provides CDK constructs for the 1st-party (i.e. developed by AWS) lambda fURL webhook receivers for:

* GitHub
* Stripe (TODO)
* Twilio (TODO)

See [here](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-saas-furls.html) for additional information.
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

import aws_cdk.aws_events
import aws_cdk.aws_lambda
import aws_cdk.aws_secretsmanager
import constructs


class GitHubEventProcessor(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-eventbridge-partner-processors.GitHubEventProcessor",
):
    '''CDK wrapper for the GitHub Eventbridge processor.

    :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-saas-furls.html#furls-connection-github
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        event_bus: aws_cdk.aws_events.IEventBus,
        git_hub_webhook_secret: aws_cdk.aws_secretsmanager.ISecret,
        lambda_invocation_alarm_threshold: jsii.Number,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param event_bus: Eventbus to send GitHub events to.
        :param git_hub_webhook_secret: SM Secret containing the secret string used to validate webhook events.
        :param lambda_invocation_alarm_threshold: Maximum number of concurrent invocations on the fURL function before triggering the alarm.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(GitHubEventProcessor.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GitHubProps(
            event_bus=event_bus,
            git_hub_webhook_secret=git_hub_webhook_secret,
            lambda_invocation_alarm_threshold=lambda_invocation_alarm_threshold,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="githubEventsFunction")
    def github_events_function(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "githubEventsFunction"))

    @github_events_function.setter
    def github_events_function(self, value: aws_cdk.aws_lambda.Function) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(GitHubEventProcessor, "github_events_function").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "githubEventsFunction", value)

    @builtins.property
    @jsii.member(jsii_name="invocationAlarm")
    def invocation_alarm(self) -> "InvocationAlarm":
        return typing.cast("InvocationAlarm", jsii.get(self, "invocationAlarm"))

    @invocation_alarm.setter
    def invocation_alarm(self, value: "InvocationAlarm") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(GitHubEventProcessor, "invocation_alarm").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invocationAlarm", value)


@jsii.data_type(
    jsii_type="cdk-eventbridge-partner-processors.GitHubProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_bus": "eventBus",
        "git_hub_webhook_secret": "gitHubWebhookSecret",
        "lambda_invocation_alarm_threshold": "lambdaInvocationAlarmThreshold",
    },
)
class GitHubProps:
    def __init__(
        self,
        *,
        event_bus: aws_cdk.aws_events.IEventBus,
        git_hub_webhook_secret: aws_cdk.aws_secretsmanager.ISecret,
        lambda_invocation_alarm_threshold: jsii.Number,
    ) -> None:
        '''
        :param event_bus: Eventbus to send GitHub events to.
        :param git_hub_webhook_secret: SM Secret containing the secret string used to validate webhook events.
        :param lambda_invocation_alarm_threshold: Maximum number of concurrent invocations on the fURL function before triggering the alarm.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(GitHubProps.__init__)
            check_type(argname="argument event_bus", value=event_bus, expected_type=type_hints["event_bus"])
            check_type(argname="argument git_hub_webhook_secret", value=git_hub_webhook_secret, expected_type=type_hints["git_hub_webhook_secret"])
            check_type(argname="argument lambda_invocation_alarm_threshold", value=lambda_invocation_alarm_threshold, expected_type=type_hints["lambda_invocation_alarm_threshold"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_bus": event_bus,
            "git_hub_webhook_secret": git_hub_webhook_secret,
            "lambda_invocation_alarm_threshold": lambda_invocation_alarm_threshold,
        }

    @builtins.property
    def event_bus(self) -> aws_cdk.aws_events.IEventBus:
        '''Eventbus to send GitHub events to.'''
        result = self._values.get("event_bus")
        assert result is not None, "Required property 'event_bus' is missing"
        return typing.cast(aws_cdk.aws_events.IEventBus, result)

    @builtins.property
    def git_hub_webhook_secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''SM Secret containing the secret string used to validate webhook events.'''
        result = self._values.get("git_hub_webhook_secret")
        assert result is not None, "Required property 'git_hub_webhook_secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    @builtins.property
    def lambda_invocation_alarm_threshold(self) -> jsii.Number:
        '''Maximum number of concurrent invocations on the fURL function before triggering the alarm.'''
        result = self._values.get("lambda_invocation_alarm_threshold")
        assert result is not None, "Required property 'lambda_invocation_alarm_threshold' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InvocationAlarm(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-eventbridge-partner-processors.InvocationAlarm",
):
    '''Cloudwatch Alarm used across this construct library.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        event_function: aws_cdk.aws_lambda.IFunction,
        threshold: jsii.Number,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param event_function: The function to monitor.
        :param threshold: Lambda Invocation threshold.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(InvocationAlarm.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InvocationAlarmProps(
            event_function=event_function, threshold=threshold
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-eventbridge-partner-processors.InvocationAlarmProps",
    jsii_struct_bases=[],
    name_mapping={"event_function": "eventFunction", "threshold": "threshold"},
)
class InvocationAlarmProps:
    def __init__(
        self,
        *,
        event_function: aws_cdk.aws_lambda.IFunction,
        threshold: jsii.Number,
    ) -> None:
        '''
        :param event_function: The function to monitor.
        :param threshold: Lambda Invocation threshold.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(InvocationAlarmProps.__init__)
            check_type(argname="argument event_function", value=event_function, expected_type=type_hints["event_function"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
        self._values: typing.Dict[str, typing.Any] = {
            "event_function": event_function,
            "threshold": threshold,
        }

    @builtins.property
    def event_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The function to monitor.'''
        result = self._values.get("event_function")
        assert result is not None, "Required property 'event_function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Lambda Invocation threshold.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InvocationAlarmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GitHubEventProcessor",
    "GitHubProps",
    "InvocationAlarm",
    "InvocationAlarmProps",
]

publication.publish()
