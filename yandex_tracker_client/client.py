# coding: utf-8

from .connection import Connection
from . import collections

__all__ = ['TrackerClient']


class TrackerClient(object):
    def __init__(self, *args, **kwargs):
        self._collections = {}
        self.connector = kwargs.pop('connector', Connection)

        conn = kwargs.pop('connection', None)

        if conn is None:
            conn = self.connector(*args, **kwargs)

        conn._client = self

        self._connection = conn

        self.attachments = self._get_collection(collections.Attachments)
        self.users = self._get_collection(collections.Users)
        self.queues = self._get_collection(collections.Queues)
        self.issues = self._get_collection(collections.Issues)
        self.issue_types = self._get_collection(collections.IssueTypes)
        self.boards = self._get_collection(collections.Boards)
        self.sprints = self._get_collection(collections.Sprints)
        self.priorities = self._get_collection(collections.Priorities)
        self.groups = self._get_collection(collections.Groups)
        self.statuses = self._get_collection(collections.Statuses)
        self.resolutions = self._get_collection(collections.Resolutions)
        self.versions = self._get_collection(collections.Versions)
        self.projects = self._get_collection(collections.Projects)
        self.components = self._get_collection(collections.Components)
        self.linktypes = self._get_collection(collections.LinkTypes)
        self.fields = self._get_collection(collections.Fields)
        self.screens = self._get_collection(collections.Screens)
        self.worklog = self._get_collection(collections.Worklog)
        self.bulkchange = collections.BulkChange(conn)
        self.translations = self._get_collection(collections.Translations)
        self.departments = self._get_collection(collections.Departments)
        self.issue_templates = self._get_collection(collections.IssueTemplates)
        self.comment_templates = self._get_collection(collections.CommentTemplates)
        self.filters = self._get_collection(collections.Filters)
        self.workflows = self._get_collection(collections.Workflows)
        # Entities
        self.project = self._get_collection(collections.Project)
        self.portfolio = self._get_collection(collections.Portfolio)
        self.goal = self._get_collection(collections.Goal)

    @property
    def myself(self):
        return self._connection.get(path='/v2/myself')

    def _get_collection(self, cls):
        if cls not in self._collections:
            self._collections[cls] = cls(self._connection)
        return self._collections[cls]
