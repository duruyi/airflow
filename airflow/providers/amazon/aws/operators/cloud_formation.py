#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""This module contains CloudFormation create/delete stack operators."""
from typing import TYPE_CHECKING, Optional, Sequence

from airflow.models import BaseOperator
from airflow.providers.amazon.aws.hooks.cloud_formation import CloudFormationHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class CloudFormationCreateStackOperator(BaseOperator):
    """
    An operator that creates a CloudFormation stack.

    :param stack_name: stack name (templated)
    :type stack_name: str
    :param params: parameters to be passed to CloudFormation.

        .. seealso::
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
    :type params: dict
    :param aws_conn_id: aws connection to uses
    :type aws_conn_id: str
    """

    template_fields: Sequence[str] = ('stack_name',)
    template_ext: Sequence[str] = ()
    ui_color = '#6b9659'

    def __init__(self, *, stack_name: str, params: dict, aws_conn_id: str = 'aws_default', **kwargs):
        super().__init__(**kwargs)
        self.stack_name = stack_name
        self.params = params
        self.aws_conn_id = aws_conn_id

    def execute(self, context: 'Context'):
        self.log.info('Parameters: %s', self.params)

        cloudformation_hook = CloudFormationHook(aws_conn_id=self.aws_conn_id)
        cloudformation_hook.create_stack(self.stack_name, self.params)


class CloudFormationDeleteStackOperator(BaseOperator):
    """
    An operator that deletes a CloudFormation stack.

    :param stack_name: stack name (templated)
    :type stack_name: str
    :param params: parameters to be passed to CloudFormation.

        .. seealso::
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack
    :type params: dict
    :param aws_conn_id: aws connection to uses
    :type aws_conn_id: str
    """

    template_fields: Sequence[str] = ('stack_name',)
    template_ext: Sequence[str] = ()
    ui_color = '#1d472b'
    ui_fgcolor = '#FFF'

    def __init__(
        self, *, stack_name: str, params: Optional[dict] = None, aws_conn_id: str = 'aws_default', **kwargs
    ):
        super().__init__(**kwargs)
        self.params = params or {}
        self.stack_name = stack_name
        self.aws_conn_id = aws_conn_id

    def execute(self, context: 'Context'):
        self.log.info('Parameters: %s', self.params)

        cloudformation_hook = CloudFormationHook(aws_conn_id=self.aws_conn_id)
        cloudformation_hook.delete_stack(self.stack_name, self.params)
