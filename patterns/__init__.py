from .strategies import (
    GradeStrategy,
    SimpleAverageStrategy,
    WeightedGradeStrategy,
    ECTSRatingStrategy,
    GradeCalculator
)
from .observers import (
    GradeObserver,
    GradeEventPublisher,
    AuditLogObserver,
    NotificationObserver,
    DashboardStatsObserver
)
from .reports import (
    Report,
    ReportCreator,
    TasksSummaryReport,
    AcademicPerformanceReport,
    TasksReportCreator,
    AcademicReportCreator
)
from .repositories import (
    ITaskRepository,
    InMemoryTaskRepository
)
