from datetime import datetime

import graphene
from graphene_django import DjangoObjectType

from aleksis.apps.chronos.models import Lesson
from aleksis.core.models import Group, Person
from aleksis.core.util.core_helpers import get_site_preferences

from .models import (
    Event,
    ExcuseType,
    ExtraLesson,
    ExtraMark,
    LessonDocumentation,
    LessonPeriod,
    PersonalNote,
)


class ExcuseTypeType(DjangoObjectType):
    class Meta:
        model = ExcuseType


class PersonalNoteType(DjangoObjectType):
    class Meta:
        model = PersonalNote


class LessonDocumentationType(DjangoObjectType):
    class Meta:
        model = LessonDocumentation

    personal_notes = graphene.List(PersonalNoteType)
    date = graphene.Field(graphene.Date)
    period = graphene.Field(graphene.Int)

    def resolve_personal_notes(root: LessonDocumentation, info, **kwargs):
        persons = Person.objects.filter(
            member_of__in=Group.objects.filter(pk__in=root.register_object.get_groups().all())
        )
        return PersonalNote.objects.filter(
            week=root.week,
            year=root.year,
            lesson_period=root.lesson_period,
            person__in=persons,
        )

    def resolve_period(root: LessonDocumentation, info, **kwargs):
        return root.period.period

    def resolve_date(root: LessonDocumentation, info, **kwargs):
        return root.date


class ExtraMarkType(DjangoObjectType):
    class Meta:
        model = ExtraMark


class LessonDocumentationMutation(graphene.Mutation):
    class Arguments:
        year = graphene.Int(required=True)
        week = graphene.Int(required=True)

        lesson_period_id = graphene.ID(required=False)
        event_id = graphene.ID(required=False)
        extra_lesson_id = graphene.ID(required=False)

        lesson_documentation_id = graphene.ID(required=False)

        topic = graphene.String(required=False)
        homework = graphene.String(required=False)
        group_note = graphene.String(required=False)

    lesson_documentation = graphene.Field(LessonDocumentationType)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        year,
        week,
        lesson_period_id=None,
        event_id=None,
        extra_lesson_id=None,
        lesson_documentation_id=None,
        topic=None,
        homework=None,
        group_note=None,
    ):

        lesson_period = LessonPeriod.objects.filter(pk=lesson_period_id).first()
        event = Event.objects.filter(pk=event_id).first()
        extra_lesson = ExtraLesson.objects.filter(pk=extra_lesson_id).first()

        lesson_documentation, created = LessonDocumentation.objects.get_or_create(
            year=year,
            week=week,
            lesson_period=lesson_period,
            event=event,
            extra_lesson=extra_lesson,
        )

        if topic is not None:
            lesson_documentation.topic = topic
        if homework is not None:
            lesson_documentation.homework = homework
        if group_note is not None:
            lesson_documentation.group_note = group_note

        lesson_documentation.save()

        if (
            get_site_preferences()["alsijil__save_lesson_documentations_by_week"]
            and (
                lesson_documentation.topic
                or lesson_documentation.homework
                or lesson_documentation.group_note
            )
            and lesson_documentation.lesson_period
        ):
            lesson_documentation.carry_over_data(
                LessonPeriod.objects.filter(lesson=lesson_documentation.lesson_period.lesson), True
            )

        return LessonDocumentationMutation(lesson_documentation=lesson_documentation)


class PersonalNoteMutation(graphene.Mutation):
    class Arguments:
        person_id = graphene.ID(required=True)
        lesson_documentation = graphene.ID(required=True)

        personal_note_id = graphene.ID(required=False)  # Update or create personal note

        late = graphene.Int(required=False)
        absent = graphene.Boolean(required=False)
        excused = graphene.Boolean(required=False)
        excuse_type = graphene.ID(required=False)
        remarks = graphene.String(required=False)
        extra_marks = graphene.List(graphene.ID, required=False)

    personal_note = graphene.Field(PersonalNoteType)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        person_id,
        lesson_documentation,
        personal_note_id=None,
        late=None,
        absent=None,
        excused=None,
        excuse_type=None,
        remarks=None,
        extra_marks=None,
    ):
        person = Person.objects.get(pk=person_id)
        lesson_documentation = LessonDocumentation.objects.get(pk=lesson_documentation)

        personal_note, created = PersonalNote.objects.get_or_create(
            person=person,
            event=lesson_documentation.event,
            extra_lesson=lesson_documentation.extra_lesson,
            lesson_period=lesson_documentation.lesson_period,
            week=lesson_documentation.week,
            year=lesson_documentation.year,
        )
        if late is not None:
            personal_note.late = late
        if absent is not None:
            personal_note.absent = absent
        if excused is not None:
            personal_note.excused = excused
        if excuse_type is not None:
            personal_note.excuse_type = ExcuseType.objects.get(pk=excuse_type)
        if remarks is not None:
            personal_note.remarks = remarks

        if created:
            personal_note.groups_of_person.set(person.member_of.all())

        personal_note.save()

        if extra_marks is not None:
            extra_marks = ExtraMark.objects.filter(pk__in=extra_marks)
            personal_note.extra_marks.set(extra_marks)
            personal_note.save()
        return PersonalNoteMutation(personal_note=personal_note)


class Mutation(graphene.ObjectType):
    update_or_create_lesson_documentation = LessonDocumentationMutation.Field()
    update_or_create_personal_note = PersonalNoteMutation.Field()
    # update_personal_note = PersonalNoteMutation.Field()


class Query(graphene.ObjectType):
    excuse_types = graphene.List(ExcuseTypeType)
    lesson_documentations = graphene.List(LessonDocumentationType)
    lesson_documentation_by_id = graphene.Field(LessonDocumentationType, id=graphene.ID())
    lesson_documentations_by_lesson_id = graphene.List(LessonDocumentationType, id=graphene.ID())
    personal_notes = graphene.List(PersonalNoteType)
    extra_marks = graphene.List(ExtraMarkType)

    def resolve_excuse_types(root, info, **kwargs):
        # FIXME do permission stuff
        return ExcuseType.objects.all()

    def resolve_lesson_documentations(root, info, **kwargs):
        # FIXME do permission stuff
        return LessonDocumentation.objects.all().order_by(
            "-year", "-week", "-lesson_period__period__weekday", "-lesson_period__period__period"
        )

    def resolve_lesson_documentation_by_id(root, info, id, **kwargs):  # noqa
        return LessonDocumentation.objects.get(id=id)

    def resolve_lesson_documentations_by_lesson_id(root, info, id, **kwargs):  # noqa
        lesson = Lesson.objects.get(id=id)
        now = datetime.now()
        for planned in lesson.planned_lessonperiods_datetimes:
            if planned["datetime_start"] <= now:
                LessonDocumentation.objects.get_or_create(
                    week=planned["week"],
                    year=planned["year"],
                    lesson_period=planned["lesson_period"],
                )  # FIXME: Queries shouldn't alter data

        return LessonDocumentation.objects.filter(
            lesson_period_id__in=LessonPeriod.objects.filter(lesson_id=id).values_list(
                "id", flat=True
            )
        ).order_by(
            "-year", "-week", "-lesson_period__period__weekday", "-lesson_period__period__period"
        )

    def resolve_personal_notes(root, info, **kwargs):
        # FIXME do permission stuff
        return PersonalNote.objects.all()

    def resolve_extra_marks(root, info, **kwargs):
        return ExtraMark.objects.all()
