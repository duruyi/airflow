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

from typing import TYPE_CHECKING, Iterable, Optional, Sequence

from airflow.exceptions import AirflowException
from airflow.providers.amazon.aws.hooks.dms import DmsHook
from airflow.sensors.base import BaseSensorOperator

if TYPE_CHECKING:
    from airflow.utils.context import Context


class DmsTaskBaseSensor(BaseSensorOperator):
    """
    Contains general sensor behavior for DMS task.

    Subclasses should set ``target_statuses`` and ``termination_statuses`` fields.

    :param replication_task_arn: AWS DMS replication task ARN
    :type replication_task_arn: str
    :param aws_conn_id: aws connection to uses
    :type aws_conn_id: str
    :param target_statuses: the target statuses, sensor waits until
        the task reaches any of these states
    :type target_states: list[str]
    :param termination_statuses: the termination statuses, sensor fails when
        the task reaches any of these states
    :type termination_statuses: list[str]
    """

    template_fields: Sequence[str] = ('replication_task_arn',)
    template_ext: Sequence[str] = ()

    def __init__(
        self,
        replication_task_arn: str,
        aws_conn_id='aws_default',
        target_statuses: Optional[Iterable[str]] = None,
        termination_statuses: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.aws_conn_id = aws_conn_id
        self.replication_task_arn = replication_task_arn
        self.target_statuses: Optional[Iterable[str]] = target_statuses
        self.termination_statuses: Optional[Iterable[str]] = termination_statuses
        self.hook: Optional[DmsHook] = None

    def get_hook(self) -> DmsHook:
        """Get DmsHook"""
        if self.hook:
            return self.hook

        self.hook = DmsHook(self.aws_conn_id)
        return self.hook

    def poke(self, context: 'Context'):
        status: str = self.get_hook().get_task_status(self.replication_task_arn)

        if not status:
            raise AirflowException(
                f'Failed to read task status, task with ARN {self.replication_task_arn} not found'
            )

        self.log.info('DMS Replication task (%s) has status: %s', self.replication_task_arn, status)

        if status in self.target_statuses:
            return True

        if status in self.termination_statuses:
            raise AirflowException(f'Unexpected status: {status}')

        return False


class DmsTaskCompletedSensor(DmsTaskBaseSensor):
    """
    Pokes DMS task until it is completed.

    .. seealso::
        For more information on how to use this operator, take a look at the guide:
        :ref:`howto/sensor:DmsTaskCompletedSensor`

    :param replication_task_arn: AWS DMS replication task ARN
    :type replication_task_arn: str
    """

    template_fields: Sequence[str] = ('replication_task_arn',)
    template_ext: Sequence[str] = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_statuses = ['stopped']
        self.termination_statuses = [
            'creating',
            'deleting',
            'failed',
            'failed-move',
            'modifying',
            'moving',
            'ready',
            'testing',
        ]
