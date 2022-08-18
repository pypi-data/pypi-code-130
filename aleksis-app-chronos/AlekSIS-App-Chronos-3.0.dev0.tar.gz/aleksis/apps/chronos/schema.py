import graphene
from graphene_django import DjangoObjectType

from aleksis.core.models import Group, Person

from .models import (
    Event,
    ExtraLesson,
    Lesson,
    LessonPeriod,
    Room,
    Subject,
    TimePeriod,
    ValidityRange,
)


class ExtraLessonType(DjangoObjectType):
    class Meta:
        model = ExtraLesson


class EventType(DjangoObjectType):
    class Meta:
        model = Event


class LessonPeriodType(DjangoObjectType):
    class Meta:
        model = LessonPeriod


class LessonDateTimeType(graphene.ObjectType):
    year = graphene.Int()
    week = graphene.Int()
    datetime_start = graphene.DateTime()
    datetime_end = graphene.DateTime()
    lesson_period = graphene.Field(LessonPeriodType)

    def resolve_year(parent, info):
        return parent["year"]

    def resolve_week(parent, info):
        return parent["week"]

    def resolve_datetime_start(parent, info):
        return parent["datetime_start"]

    def resolve_datetime_end(parent, info):
        return parent["datetime_end"]

    def resolve_lesson_period(parent, info):
        return parent["lesson_period"]


class LessonType(DjangoObjectType):
    planned_lessonperiods_datetimes = graphene.List(LessonDateTimeType)

    class Meta:
        model = Lesson


class RoomType(DjangoObjectType):
    class Meta:
        model = Room


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject


class TimePeriodType(DjangoObjectType):
    class Meta:
        model = TimePeriod


class CalendarWeekType(graphene.ObjectType):
    year = graphene.Int()
    week = graphene.Int()

    def resolve_year(parent, info):
        return parent.year

    def resolve_week(parent, info):
        return parent.week


class ValidityRangeType(DjangoObjectType):
    calendarweeks = graphene.List(CalendarWeekType)

    class Meta:
        model = ValidityRange


class RoomMutation(graphene.Mutation):
    class Arguments:
        short_name = graphene.String(required=True)
        name = graphene.String(required=True)

    room = graphene.Field(RoomType)

    @classmethod
    def mutate(cls, root, info, short_name, name):
        room = Room.objects.create(short_name=short_name, name=name)

        return RoomMutation(room=room)


class SubjectMutation(graphene.Mutation):
    class Arguments:
        short_name = graphene.String(required=True)
        name = graphene.String(required=True)

    subject = graphene.Field(SubjectType)

    @classmethod
    def mutate(cls, root, info, short_name, name):
        subject = Subject.objects.create(short_name=short_name, name=name)

        return SubjectMutation(subject=subject)


class TimePeriodMutation(graphene.Mutation):
    class Arguments:
        weekday = graphene.Int(required=True)
        period = graphene.Int(required=True)
        time_start = graphene.Time(required=True)
        time_end = graphene.Time(required=True)

    time_period = graphene.Field(TimePeriodType)

    @classmethod
    def mutate(cls, root, info, weekday, period, time_start, time_end):
        time_period = TimePeriod.objects.create(
            weekday=weekday, period=period, time_start=time_start, time_end=time_end
        )

        return TimePeriodMutation(time_period=time_period)


class LessonMutation(graphene.Mutation):
    class Arguments:
        subject = graphene.ID(required=True)
        teachers = graphene.List(graphene.ID, required=True)
        groups = graphene.List(graphene.ID, required=True)

    lesson = graphene.Field(LessonType)

    @classmethod
    def mutate(cls, root, info, subject, teachers, groups):
        subject = Subject.objects.get(pk=subject)
        teachers = Person.objects.filter(pk__in=teachers)
        groups = Group.objects.filter(pk__in=groups)
        lesson = Lesson.objects.create(subject=subject)
        lesson.teachers.set(teachers)
        lesson.groups.set(groups)

        return LessonMutation(lesson=lesson)


class LessonPeriodMutation(graphene.Mutation):
    class Arguments:
        lesson = graphene.ID(required=True)
        period = graphene.ID(required=True)
        room = graphene.ID(required=True)

    lesson_period = graphene.Field(LessonPeriodType)

    @classmethod
    def mutate(cls, root, info, lesson, period, room):
        lesson = Lesson.objects.get(pk=lesson)
        period = TimePeriod.objects.get(pk=period)
        room = Room.objects.get(pk=room)
        lesson_period = LessonPeriod.create(lesson=lesson, period=period, room=room)

        return LessonPeriodMutation(lesson_period=lesson_period)


class Mutation(graphene.ObjectType):
    pass
    # room_mutation = RoomMutation.Field()
    # subject_mutation = SubjectMutation.Field()
    # time_period_mutation = TimePeriodMutation.Field()
    # lesson_mutation = LessonMutation.Field()
    # lesson_period_mutation = LessonPeriodMutation.Field()


class Query(graphene.ObjectType):
    lessons = graphene.List(LessonType)
    lesson_by_id = graphene.Field(LessonType, id=graphene.ID())  # noqa
    lesson_periods = graphene.List(LessonPeriodType)
    subjects = graphene.List(SubjectType)
    rooms = graphene.List(RoomType)
    validity_ranges = graphene.List(ValidityRangeType)

    def resolve_lessons(root, info, **kwargs):
        return Lesson.objects.all()

    def resolve_lesson_by_id(root, info, id):  # noqa
        return Lesson.objects.get(pk=id)  # noqa

    def resolve_lesson_periods(root, info, **kwargs):
        return LessonPeriod.objects.all()

    def resolve_subjects(root, info, **kwargs):
        return Subject.objects.all()

    def resolve_rooms(root, info, **kwargs):
        return Room.objects.all()

    def resolve_validity_ranges(root, info, **kwargs):
        return ValidityRange.objects.all()
