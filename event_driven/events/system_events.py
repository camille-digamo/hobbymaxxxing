"""
System-level events for the YouTube Hobby Maxxxer.

These events handle workflow orchestration, system state, and coordination.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.event_bus import Event


@dataclass
class SystemStarted(Event):
    """Event: Event-driven system has started"""
    event_type: str = "system.started"
    mode: str = ""  # daily-job, listen, interactive, test
    version: str = "1.0.0"
    startup_time: str = ""

    def __post_init__(self):
        super().__post_init__()
        if not self.startup_time:
            self.startup_time = datetime.now().isoformat()


@dataclass
class SystemStopping(Event):
    """Event: Event-driven system is stopping"""
    event_type: str = "system.stopping"
    reason: str = "normal"  # normal, error, timeout, user_interrupt
    uptime_seconds: float = 0.0
    events_processed: int = 0


@dataclass
class SystemError(Event):
    """Event: System-level error occurred"""
    event_type: str = "system.error"
    error_type: str = ""
    error_message: str = ""
    component: str = ""
    stack_trace: str = ""
    recoverable: bool = True
    retry_count: int = 0


@dataclass
class DailyJobTriggered(Event):
    """Event: Daily video recommendation job has been triggered"""
    event_type: str = "system.daily_job_triggered"
    trigger_source: str = "cron"  # cron, github_actions, manual, test
    scheduled_time: str = ""
    actual_time: str = ""

    def __post_init__(self):
        super().__post_init__()
        if not self.actual_time:
            self.actual_time = datetime.now().isoformat()


@dataclass
class ListenerModeStarted(Event):
    """Event: Persistent listener mode has started"""
    event_type: str = "system.listener_mode_started"
    listener_type: str = "full"  # full, minimal, railway
    capabilities: list = None

    def __post_init__(self):
        super().__post_init__()
        if self.capabilities is None:
            self.capabilities = ["reactions", "messages", "topic_exploration"]


@dataclass
class WorkflowStarted(Event):
    """Event: A workflow has been initiated"""
    event_type: str = "system.workflow_started"
    workflow_type: str = ""  # daily_recommendation, interactive_session, topic_expansion
    workflow_id: str = ""
    trigger_event: str = ""
    expected_duration: int = 0  # seconds


@dataclass
class WorkflowCompleted(Event):
    """Event: A workflow has completed successfully"""
    event_type: str = "system.workflow_completed"
    workflow_type: str = ""
    workflow_id: str = ""
    outcome: str = "success"  # success, partial, failed
    duration_seconds: float = 0.0
    events_generated: int = 0


@dataclass
class WorkflowFailed(Event):
    """Event: A workflow has failed"""
    event_type: str = "system.workflow_failed"
    workflow_type: str = ""
    workflow_id: str = ""
    failure_reason: str = ""
    failure_point: str = ""
    retry_possible: bool = True


@dataclass
class HealthCheckRequested(Event):
    """Event: System health check requested"""
    event_type: str = "system.health_check_requested"
    check_type: str = "full"  # full, api, database, discord
    requested_by: str = "system"


@dataclass
class HealthCheckCompleted(Event):
    """Event: System health check completed"""
    event_type: str = "system.health_check_completed"
    overall_status: str = "healthy"  # healthy, degraded, unhealthy
    component_status: Dict[str, str] = None
    response_time_ms: float = 0.0
    issues_found: list = None

    def __post_init__(self):
        super().__post_init__()
        if self.component_status is None:
            self.component_status = {}
        if self.issues_found is None:
            self.issues_found = []


@dataclass
class ConfigurationChanged(Event):
    """Event: System configuration has been updated"""
    event_type: str = "system.configuration_changed"
    config_type: str = ""  # environment, runtime, feature_flags
    changed_keys: list = None
    previous_values: Dict[str, Any] = None
    new_values: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.changed_keys is None:
            self.changed_keys = []
        if self.previous_values is None:
            self.previous_values = {}
        if self.new_values is None:
            self.new_values = {}


@dataclass
class PerformanceMetricRecorded(Event):
    """Event: Performance metric has been recorded"""
    event_type: str = "system.performance_metric_recorded"
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
    component: str = ""
    tags: Dict[str, str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.tags is None:
            self.tags = {}


@dataclass
class RateLimitWarning(Event):
    """Event: API rate limit warning"""
    event_type: str = "system.rate_limit_warning"
    api_service: str = ""  # youtube, anthropic, discord, sheets
    current_usage: int = 0
    limit: int = 0
    usage_percentage: float = 0.0
    reset_time: str = ""
    action_taken: str = ""


@dataclass
class RateLimitExceeded(Event):
    """Event: API rate limit exceeded"""
    event_type: str = "system.rate_limit_exceeded"
    api_service: str = ""
    attempted_operation: str = ""
    retry_after_seconds: int = 0
    fallback_available: bool = False


@dataclass
class BackupRequested(Event):
    """Event: Data backup requested"""
    event_type: str = "system.backup_requested"
    backup_type: str = "incremental"  # full, incremental, emergency
    target_data: list = None
    requested_by: str = "system"

    def __post_init__(self):
        super().__post_init__()
        if self.target_data is None:
            self.target_data = ["sheets_data", "user_state", "configuration"]


@dataclass
class BackupCompleted(Event):
    """Event: Data backup completed"""
    event_type: str = "system.backup_completed"
    backup_id: str = ""
    backup_size_mb: float = 0.0
    items_backed_up: int = 0
    duration_seconds: float = 0.0
    backup_location: str = ""


# Helper functions for creating common system events

def create_daily_job_trigger(source: str = "cron", scheduled_time: str = "",
                           session_id: str = None) -> DailyJobTriggered:
    """Create a daily job triggered event"""
    return DailyJobTriggered(
        trigger_source=source,
        scheduled_time=scheduled_time,
        session_id=session_id
    )


def create_workflow_started(workflow_type: str, trigger_event: str = "",
                          expected_duration: int = 0, session_id: str = None) -> WorkflowStarted:
    """Create a workflow started event"""
    import uuid
    return WorkflowStarted(
        workflow_type=workflow_type,
        workflow_id=str(uuid.uuid4()),
        trigger_event=trigger_event,
        expected_duration=expected_duration,
        session_id=session_id
    )


def create_workflow_completed(workflow_type: str, workflow_id: str, outcome: str = "success",
                            duration: float = 0.0, session_id: str = None) -> WorkflowCompleted:
    """Create a workflow completed event"""
    return WorkflowCompleted(
        workflow_type=workflow_type,
        workflow_id=workflow_id,
        outcome=outcome,
        duration_seconds=duration,
        session_id=session_id
    )


def create_system_error(error_type: str, message: str, component: str = "",
                       recoverable: bool = True, session_id: str = None) -> SystemError:
    """Create a system error event"""
    return SystemError(
        error_type=error_type,
        error_message=message,
        component=component,
        recoverable=recoverable,
        session_id=session_id
    )