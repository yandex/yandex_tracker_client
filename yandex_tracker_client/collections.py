# coding: utf-8

import abc
import logging
import os
import time
import re
import uuid
import six


from six import iteritems, with_metaclass, string_types
from six.moves import range

from .settings import VERSION_V2
from .uriutils import Matcher
from . import exceptions


logger = logging.getLogger(__name__)


def injected_property(func):
    func._injected_property = True
    return func


def injected_method(func):
    func._injected_method = True
    return func


def match_collection(path):
    result = CollectionMeta.matcher.match(path)
    if result is not None:
        return result

    logger.warning('Unrecognized collection: %s', path)
    return Unknown


url_slots_re = re.compile(r'\{(\w+)\}')


class CollectionMeta(abc.ABCMeta):
    matcher = Matcher()

    def __new__(mcs, name, bases, members):
        injected_properties = {}
        injected_methods = {}
        for base in bases:
            injected_properties.update(
                getattr(base, '_injected_properties', {})
            )
            injected_methods.update(
                getattr(base, '_injected_methods', {})
            )
        for member, value in iteritems(members):
            if getattr(value, '_injected_property', None):
                injected_properties[member] = value
            elif getattr(value, '_injected_method', None):
                injected_methods[member] = value
        members['_injected_properties'] = injected_properties
        members['_injected_methods'] = injected_methods

        if 'path' in members and isinstance(members['path'], string_types):
            members['url_slots'] = set(url_slots_re.findall(members['path']))

        cls = super(CollectionMeta, mcs).__new__(mcs, name, bases, members)

        if isinstance(cls.path, str):
            mcs.matcher.add(cls.path, cls, cls._priority)
        return cls


class Collection(with_metaclass(CollectionMeta, object)):
    _injected_properties = {}
    _injected_methods = {}
    _priority = 0
    _fields = {}
    _connection = None
    _vars = None
    _header_param_names = {'x_org_id': 'X-ORG-ID'}
    _local_fields_map = {}
    has_local_fields = False


    def __init__(self, connection, **kwargs):
        self._connection = connection
        self._vars = kwargs

    def __getitem__(self, key):
        return self.get(key)

    def __iter__(self):
        return iter(self.get_all())

    def __reduce__(self):
        return (
            self.__class__,
            (self._connection,),
            {'_fields': self._fields, '_vars': self._vars},
        )

    @abc.abstractproperty
    def path(self):
        pass

    @abc.abstractproperty
    def fields(self):
        pass


    def _parse_value(self, value):
        if self.has_local_fields:
            local_fields_to_add = {}
            for field, field_value in six.iteritems(value):
                if '--' in field:
                    local_field_key = field.split('--')[-1]
                    if local_field_key in value:
                        local_field_key = 'local_{}'.format(local_field_key)
                    local_fields_to_add[local_field_key] = field_value
                    self._local_fields_map[local_field_key] = field
            value.update(local_fields_to_add)
        return value

    def _process_kwargs(self, kwargs):
        if self.has_local_fields:
            for field_value, local_field_value in six.iteritems(self._local_fields_map):
                if field_value in kwargs:
                    kwargs[local_field_value] = kwargs.pop(field_value)

        return kwargs

    def _execute_request(self, method, path, params=None, data=None, files=None, **kwargs):
        url_params, header_params, params = self._extract_params(params)
        path = path.format(**url_params)
        return method(path=path, params=params, headers=header_params, data=data, files=files, **kwargs)

    def _extract_params(self, params=None):
        params = params or {}
        url_params = {'api_version': getattr(self._connection, 'api_version', VERSION_V2)}
        header_params = {}
        get_params = {}

        for k, v in iteritems(self._vars):
            if k in self.url_slots:
                url_params[k] = v
            else:
                get_params[k] = v

        for k, v in iteritems(params):
            if k in self.url_slots:
                url_params[k] = v
            else:
                header_name = self._header_param_names.get(k)
                if header_name is not None:
                    header_params[header_name] = str(v)
                else:
                    get_params[k] = v

        for k in self.url_slots:
            if k not in url_params:
                url_params[k] = ''

        return url_params, header_params, get_params

    def get_all(self, **params):
        return self._execute_request(
            self._connection.get,
            path=self.path,
            params=params,
        )

    def get(self, key, **params):
        params['id'] = key
        return self.get_all(**params)

    def create(self, params=None, **kwargs):
        return self._execute_request(
            self._connection.post,
            path=kwargs.pop('_create_path', self.path),
            params=params,
            data=kwargs,
        )

    def _associated(self, collection, **kwargs):
        return collection(self._connection, **kwargs)

    @injected_method
    def update(self, obj, params=None, **kwargs):
        if kwargs:
            kwargs = self._process_kwargs(kwargs)
            ignore_version_change = kwargs.pop('ignore_version_change', False)
            if ignore_version_change:
                version = None
            else:
                version = obj._version

            result = self._execute_request(
                self._connection.patch,
                path=obj._path,
                params=params,
                data=kwargs,
                version=version,
            )
        else:
            result = self._execute_request(
                self._connection.get,
                path=obj._path,
                params=params,
            )
        obj.__dict__ = result.__dict__
        return obj

    @injected_method
    def delete(self, obj):
        return self._execute_request(
            self._connection.delete,
            path=obj._path,
        )

    @injected_method
    def perform_action(self, obj, action, method, params=None, ignore_empty_body=False, list_data=None, **kwargs):
        ignore_version_change = kwargs.pop('ignore_version_change', False)
        if ignore_version_change:
            version = None
        else:
            version = obj._version

        if not kwargs and ignore_empty_body:
            kwargs = None

        if list_data:
            data = list_data
        else:
            data = kwargs

        return self._execute_request(
            getattr(self._connection, method),
            path=obj._path + '/{}'.format(action),
            version=version,
            data=data,
            params=params,
        )


class ImportCollectionMixin(object):
    @abc.abstractproperty
    def import_path(self):
        pass

    def import_object(self, *args, **kwargs):
        kwargs.setdefault('_create_path', self.import_path)
        return self.create(*args, **kwargs)


class Unknown(Collection):
    path = None
    fields = {}
    _priority = -1


class Users(Collection):
    """Extra get params = expand, localized"""
    path = '/{api_version}/users/{id}'
    fields = {
        'self': None,
        'uid': None,
        'login': None,
        'firstName': None,
        'lastName': None,
        'display': None,
        'email': None,
        'groups': [],
        'office': None,
    }

    @injected_property
    def settings(self, user):
        return self._execute_request(
            self._connection.get,
            path=user._path + '/settings',
        )


class IssueTypes(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/issuetypes/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'key': None,
        'name': None,
        'description': None,
    }


class Priorities(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/priorities/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'key': None,
        'name': None,
        'description': None,
        'order': None,
    }


class Groups(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/groups/{id}'
    fields = {
        'id': None,
        'self': None,
        'parent': None,
        'type': None,
        'code': None,
        'name': None,
        'url': None,
        'description': None,
    }


class Statuses(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/statuses/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'key': None,
        'name': None,
        'description': None,
        'order': None,
    }


class Resolutions(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/resolutions/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'key': None,
        'name': None,
        'description': None,
        'order': None,
    }


class Versions(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/versions/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'queue': None,
        'name': None,
        'description': None,
        'startDate': None,
        'dueDate': None,
        'releasedAt': None,
        'released': None,
        'archived': None,
        'next': None,
    }


class Components(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/components/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'queue': None,
        'name': None,
        'description': None,
        'lead': None,
        'archived': None,
        'assignAuto': None,
    }

    @injected_property
    def permissions(self, project):
        return self._execute_request(
            self._connection.get,
            path=project._path + '/permissions',
        )

    @injected_property
    def access(self, project):
        return self._execute_request(
            self._connection.get,
            path=project._path + '/access',
        )


class Permissions(Collection):
    path = '/{api_version}/{collection}/{id}/permissions'
    fields = {
        'self': None,
        'create': None,
        'read': None,
        'write': None,
        'grant': None,
    }
    _priority = 1


class PermissionsParticipants(Collection):
    path = '/{api_version}/{collection}/{id}/permissions/{type}'
    fields = {
        'self': None,
        'users': [],
        'groups': [],
        'roles': [],
    }
    _priority = 2


class Access(Collection):
    path = '/{api_version}/{collection}/{id}/access'
    fields = {
        'self': None,
        'create': None,
        'read': None,
        'write': None,
        'grant': None,
    }
    _priority = 1


class AccessParticipants(Collection):
    path = '/{api_version}/{collection}/{id}/access/{type}'
    fields = {
        'self': None,
        'users': [],
        'groups': [],
    }
    _priority = 2


def _upload_attachments(current_collection, data):
    attachments = data.pop('attachments', None)
    if attachments:
        collection = current_collection._associated(Attachments)
        data['attachmentIds'] = [
            collection.create(attachment).id
            for attachment in attachments
        ]


class Issues(ImportCollectionMixin, Collection):
    """Extra get params:
        filter*,
        filterId,
        fields,
        query,
        keys,
        queue,
        orderBy,
        orderAsc,
        language,
        expand,
        embed,
        localized,
        perPage,
        notifyAuthor

        Extra search get params:
        perPage,
        page,
        expand,
        fields,
        language,
        embed,
        localized,
        notifyAuthor
    """
    path = '/{api_version}/issues/{id}'
    search_path = '/{api_version}/issues/_search'
    import_path = '/{api_version}/issues/_import'
    unique_path = '/{api_version}/issues/_findByUnique'
    has_local_fields = True

    _fields = None

    @staticmethod
    def _parse_order_params(order_by, order_asc, order_list):
        if order_by:
            order_list = [
                '{direction}{field}'.format(
                    direction='+' if order_asc else '-',
                    field=order_by,
                )
            ]
        return order_list or None

    @property
    def fields(self):
        if self._fields is None:
            self._fields = dict(
                (field.id, [] if field.schema['type'] == 'array' else None)
                for field in Fields(self._connection).get_all()
            )
        return self._fields

    def create(self, params=None, **kwargs):
        _upload_attachments(self, kwargs)
        self._add_unique(kwargs)
        try:
            return super(Issues, self).create(params=params, **kwargs)
        except exceptions.Conflict as e:
            # Если st на создание вернул конфликт,
            # значит уже существует тикет с unique указанным в текущем запросе
            # Запрашиваем этот тикет и возвращаем
            unique = kwargs.get('unique')
            if unique is not None:
                try:
                    return self._execute_request(
                        self._connection.post,
                        path=self.unique_path,
                        params={'unique': unique},
                    )
                except exceptions.NotFound:
                    logger.error('Not found the issue by unique "%s"', unique)
            raise e

    def _add_unique(self, kwargs):
        if 'unique' not in kwargs:
            kwargs['unique'] = uuid.uuid4().hex

    @injected_method
    def update(self, obj, params=None, **kwargs):
        _upload_attachments(self, kwargs)
        return super(Issues, self).update(obj, params=params, **kwargs)

    def find(self, query=None, per_page=None, keys=None, filter=None, filter_id=None, order=None, **kwargs):
        """
        Parameters 'orderBy' and 'orderAsc' are deprecated in this method.
        Instead use the parameter 'order' in the form of the fields list
        like in Django: ['field1', '-field2', '+field3']
        """
        data = {
            'filter': filter,
            'filterId': filter_id,
            'query': query,
            'keys': keys,
            'queue': kwargs.pop('queue', None),
            'order': self._parse_order_params(
                kwargs.pop('orderBy', None),
                kwargs.pop('orderAsc', True),
                order or [],
            ),
        }
        return self._execute_request(
            self._connection.post,
            path=self.search_path,
            params=dict(kwargs, perPage=per_page),
            data=data,
        )

    @injected_method
    def add_remotelink(self, issue, relation, target_url):
        return self._connection.link(
            path=issue._path,
            target_url=target_url,
            rel=relation,
        )

    @injected_method
    def add_link(self, issue, relation, target_issue, params=None):
        return issue.links.create(
            relationship=relation,
            issue=target_issue,
            params=params,
        )

    @injected_method
    def create_subtask(self, issue, inherit=True, params=None, **kwargs):
        _kwargs = {
            'queue': issue.queue,
            'parent': issue
        }
        if inherit:
            # Inherit tags, fixVersions, components from parent issue
            _kwargs['tags'] = issue.tags
            _kwargs['fixVersions'] = issue.fixVersions
            _kwargs['components'] = issue.components
        _kwargs.update(kwargs)
        return self.create(params=params, **_kwargs)

    @injected_method
    def move_to(self, issue, queue):
        return self._execute_request(
            self._connection.post,
            path=issue._path + '/_move',
            params={'queue': queue},
        )

    @injected_method
    def clone_to(self, issue, queues, clone_all_fields=False, link_with_original=False):
        return self._execute_request(
            self._connection.post,
            path=issue._path + '/_clone',
            params={
                'queues': queues,
                'cloneAllFields': clone_all_fields,
                'linkWithOriginal': link_with_original,
            },
        )

    @injected_method
    def link(self, issue, resource, relationship):
        return self._connection.link(issue._path, resource, relationship)

    @injected_method
    def unlink(self, issue, resource, relationship):
        return self._connection.unlink(issue._path, resource, relationship)

    @injected_property
    def comments(self, issue):
        return self._associated(IssueComments, issue=issue.key)

    @injected_property
    def transitions(self, issue):
        return self._associated(IssueTransitions, issue=issue.key)

    @injected_property
    def links(self, issue):
        return self._associated(IssueLinks, issue=issue.key)

    @injected_property
    def attachments(self, issue):
        return self._associated(IssueAttachments, issue=issue.key)

    @injected_property
    def changelog(self, issue):
        return self._associated(IssueChangelog, issue=issue.key)

    @injected_property
    def worklog(self, issue):
        return self._associated(IssueWorklog, issue=issue.key)

    @injected_property
    def permissions(self, issue):
        if 'permissions' in issue._value:
            return issue._value['permissions']
        return self._execute_request(
            self._connection.get,
            path=issue._path + '/permissions',
        )

    @injected_property
    def checklist_items(self, issue):
        return self._associated(checklistItems, issue=issue.key)

    @injected_method
    def add_checklist_item(self, issue, text, checked=False, assignee=None, deadline=None, url=None, item_type=None):
        return issue.checklist_items.create(
            text=text,
            checked=checked,
            assignee=assignee,
            deadline=deadline,
            url=url,
            item_type=item_type
        )


class Queues(Collection):
    """Extra get params = expand, fields, localized"""
    path = '/{api_version}/queues/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'key': None,
        'name': None,
        'description': None,
        'lead': None,
        'assignAuto': None,
        'allowExternals': None,
        'defaultType': None,
        'defaultPriority': None,
        'teamUsers': [],
        'teamGroups': [],
    }

    @injected_property
    def components(self, queue):
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/components',
        )

    @injected_property
    def versions(self, queue):
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/versions',
        )

    @injected_property
    def projects(self, queue):
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/projects',
        )

    @injected_property
    def issuetypes(self, queue):
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/issuetypes',
        )

    @injected_property
    def permissions(self, queue):
        # XXX: Collection
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/permissions',
        )

    @injected_property
    def access(self, queue):
        # XXX: Collection
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/access',
        )

    @injected_property
    def triggers(self, queue):
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/triggers',
        )

    @injected_method
    def check_permissions(self, queue, permission_code):
        return self._execute_request(
            self._connection.get,
            path=queue._path + '/checkPermissions/{}'.format(permission_code),
        )


class QueueDefaultValues(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/queues/{queue}/defaultValues/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'queue': None,
        'type': None,
        'component': None,
        'values': {},
        'appendFields': [],
        'createdBy': None,
        'createdAt': None,
        'updatedBy': None,
        'updatedAt': None,
    }
    _priority = 1


class Triggers(Collection):
    path = '/{api_version}/queues/{queue}/triggers/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'queue': None,
        'name': None,
        'actions': [],
        'conditions': [],
        'active': None,
    }
    _priority = 1


class IssueTransitions(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/issues/{issue}/transitions/{id}'
    fields = {
        'id': None,
        'self': None,
        'to': None,
        'screen': None,
    }
    _priority = 1

    @injected_method
    def execute(self, transition, **kwargs):
        return self._execute_request(
            self._connection.post,
            path=transition._path + '/_execute',
            data=kwargs,
        )


class IssueComments(ImportCollectionMixin, Collection):
    """Extra get params = expand, localized, notifyAuthor"""
    path = '/{api_version}/issues/{issue}/comments/{id}'
    import_path = '/{api_version}/issues/{issue}/comments/_import'
    fields = {
        'id': None,
        'self': None,
        'text': None,
        'textHtml': None,
        'attachments': [],
        'createdBy': None,
        'createdAt': None,
        'updatedBy': None,
        'updatedAt': None,
        'summonees': [],
        'email': None,
    }
    _priority = 1

    def create(self, params=None, **kwargs):
        _upload_attachments(self, kwargs)
        return super(IssueComments, self).create(params=params, **kwargs)

    @injected_method
    def update(self, obj, **kwargs):
        _upload_attachments(self, kwargs)
        return super(IssueComments, self).update(obj, **kwargs)


class Links(Collection):
    path = '/{api_version}/links/{id}'
    fields = {
        'id': None,
        'self': None,
        'type': None,
        'direction': None,
        'object': None,
        'createdBy': None,
        'createdAt': None,
        'updatedBy': None,
        'updatedAt': None,
    }
    _noindex = True


class IssueLinks(ImportCollectionMixin, Collection):
    path = '/{api_version}/issues/{issue}/links/{id}'
    import_path = '/{api_version}/issues/{issue}/links/_import'
    fields = Links.fields
    _priority = 1

    def create(self, relationship, issue, params=None, **kwargs):
        assert 'issue' in self._vars
        return super(IssueLinks, self).create(
            relationship=relationship,
            issue=issue,
            params=params,
            **kwargs
        )


class Attachments(Collection):
    path = '/{api_version}/attachments/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
        'content': None,
        'thumbnail': None,
        'createdBy': None,
        'createdAt': None,
        'mimetype': None,
        'size': None,
        'metadata': {},
    }
    _priority = 1

    def create(self, file, params=None, **kwargs):
        """
        @type file: basestring | file
        """
        if isinstance(file, string_types):
            with open(file, 'rb') as file_to_upload:
                return self._create_from_file(file_to_upload, params, **kwargs)
        else:
            return self._create_from_file(file, params, **kwargs)

    def _create_from_file(self, file, params=None, **kwargs):
        params = params or {}
        params['filename'] = params.get('filename', self._get_filename(file))
        return self._execute_request(
            self._connection.post,
            path=kwargs.pop('_create_path', self.path),
            params=params,
            files={'file': ('file', file)},
            **kwargs
        )

    @staticmethod
    def _get_filename(file):
        DEFAULT_FILENAME = 'file'

        if isinstance(file, string_types):
            filename = file
        else:
            filename = getattr(file, 'name', None)

        if not filename:
            return DEFAULT_FILENAME

        try:
            filename.encode('ascii')
        except UnicodeEncodeError:
            return DEFAULT_FILENAME

        return filename.rsplit('/', 1)[-1]

    @injected_method
    def read(self, attachment):
        return self._connection.stream(path=attachment.content)

    @injected_method
    def download_to(self, attachment, directory):
        assert attachment.content is not None
        with open(os.path.join(directory, attachment.name), 'wb') as dest:
            for chunk in self._connection.stream(path=attachment.content):
                dest.write(chunk)

    @injected_method
    def download_thumbnail_to(self, attachment, directory):
        assert attachment.thumbnail is not None
        with open(os.path.join(directory, attachment.name), 'wb') as dest:
            for chunk in self._connection.stream(path=attachment.thumbnail):
                dest.write(chunk)


class IssueAttachments(ImportCollectionMixin, Attachments):
    path = '/{api_version}/issues/{issue}/attachments/{id}'
    import_path = '/{api_version}/issues/{issue}/attachments/_import'
    fields = Attachments.fields


class Screens(Collection):
    path = '/{api_version}/screens/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'type': None,
        'elements': [],
    }


class ScreenElements(Collection):
    path = '/{api_version}/screens/{screen}/elements/{id}'
    fields = {
        'self': None,
        'field': None,
        'required': None,
        'defaultValue': None,
    }
    _priority = 1


class IssueScreens(Collection):
    path = '/{api_version}/issues/{issue}/screens/{id}'
    fields = Screens.fields
    _priority = 1


class IssueChangelog(Collection):
    """Extra get params = sort, field*, type*"""
    path = '/{api_version}/issues/{issue}/changelog/{id}'
    fields = {
        'id': None,
        'self': None,
        'issue': None,
        'updatedAt': None,
        'updatedBy': None,
        'type': None,
        'transport': None,
        'fields': [],
        'attachments': None,
        'comments': None,
        'worklog': [],
        'messages': [],
        'links': [],
        'ranks': []
    }
    _priority = 1


class Worklog(Collection):
    path = '/{api_version}/worklog/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'issue': None,
        'comment': None,
        'createdBy': None,
        'createdAt': None,
        'updatedBy': None,
        'updatedAt': None,
        'start': None,
        'duration': None,
    }

    def find(self, params=None, **kwargs):
        params = params or {}
        params.update(kwargs)
        return self._execute_request(
            self._connection.get,
            path=self.path,
            params=params,
        )


class IssueWorklog(Collection):
    path = '/{api_version}/issues/{issue}/worklog/{id}'
    fields = Worklog.fields
    _priority = 1

    def create(self, start, duration, comment=None):
        assert 'issue' in self._vars
        super(IssueWorklog, self).create(
            start=start,
            duration=duration,
            comment=comment
        )


class LinkTypes(Collection):
    path = '/{api_version}/linktypes/{id}'
    fields = {
        'id': None,
        'self': None,
        'inward': None,
        'outward': None,
    }


class Fields(Collection):
    path = '/{api_version}/fields/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
        'description': None,
        'schema': None,
        'readonly': None,
        'options': None,
        'suggest': None,
    }


class Sprints(Collection):
    path = '/{api_version}/sprints/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'name': None,
        'board': None,
        'status': None,
        'archived': None,
        'createdBy': None,
        'createdAt': None,
        'startDate': None,
        'endDate': None,
        'startDateTime': None,
        'endDateTime': None,
    }


class BoardSprints(Sprints):
    path = '/{api_version}/boards/{board}/sprints/'


class Roles(Collection):
    path = '/{api_version}/roles/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
    }


class Countries(Collection):
    path = '/{api_version}/countries/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
    }


class Workflows(Collection):
    path = '/{api_version}/workflows/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'xml': None,
    }


class Projects(Collection):
    """Extra get params = expand, localized"""
    path = '/{api_version}/projects/{id}'
    fields = {
        'id': None,
        'self': None,
        'key': None,
        'name': None,
        'description': None,
        'lead': None,
        'teamUsers': [],
        'teamGroups': [],
        'status': None,
        'startDate': None,
        'endDate': None,
        'queues': [],
    }

    @injected_property
    def permissions(self, project):
        # XXX: Collection
        return self._execute_request(
            self._connection.get,
            path=project._path + '/permissions',
        )

    @injected_property
    def access(self, project):
        # XXX: Collection
        return self._execute_request(
            self._connection.get,
            path=project._path + '/access',
        )


class MailLists(Collection):
    path = '/{api_version}/maillists/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
        'email': None,
        'open': None,
        'info': None,
    }


class Boards(Collection):
    """Extra get params = localized"""
    path = '/{api_version}/boards/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'name': None,
        'columns': [],
        'filter': {},
        'orderBy': None,
        'orderAsc': None,
        'query': None,
        'selected': None,
        'useRanking': None,
        'country': None,
    }

    @injected_property
    def columns(self, board):
        return self._associated(BoardColumns, board=board.id)

    @injected_property
    def sprints(self, board):
        return self._associated(BoardSprints, board=board.id)


class BoardColumns(Collection):
    path = '/{api_version}/boards/{board}/columns/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
        'limit': None,
        'statuses': [],
    }
    _priority = 1


class BulkChange(Collection):
    path = '/{api_version}/bulkchange/{id}'
    fields = {
        'id': None,
        'self': None,
        'createdAt': None,
        'status': None,
        'statusText': None,
        'executionChunkPercent': None,
        'executionIssuePercent': None,
    }

    def update(self, issues, **values):
        params = values.pop('params', None)
        return self._execute_request(
            self._connection.post,
            path=self.path + '_update',
            data={'issues': issues, 'values': values},
            params=params,
        )

    def transition(self, issues, transition, **values):
        return self._execute_request(
            self._connection.post,
            path=self.path + '_transition',
            data={'transition': transition, 'issues': issues, 'values': values},
        )

    def move(self, issues, queue, move_all_fields=False, **values):
        return self._execute_request(
            self._connection.post,
            path=self.path + '_move',
            data={
                'queue': queue,
                'issues': issues,
                'values': values,
                'moveAllFields': move_all_fields,
            },
        )

    @injected_method
    def wait(self, bulkchange, interval=1.0):
        for _ in range(10):
            try:
                bulkchange = self[bulkchange.id]
            except exceptions.NotFound:
                logger.warning(
                    'Not found bulkchange with id: "{}", retrying'.format(bulkchange.id)
                )
                time.sleep(interval)
        while bulkchange.status not in ('COMPLETE', 'FAILED'):
            time.sleep(interval)
            bulkchange = self[bulkchange.id]
        return bulkchange


class Translations(Collection):
    path = '/{api_version}/translations/{id}'
    fields = {
        'id': None,
        'key': None,
        'self': None,
        'version': None,
        'value': None,
        'createdBy': None,
        'createdAt': None,
        'updatedBy': None,
        'updatedAt': None,
    }


class Departments(Collection):
    path = '/{api_version}/departments/{id}'
    fields = {
        'id': None,
        'key': None,
        'self': None,
        'name': None,
    }


class IssueTemplates(Collection):
    path = '/{api_version}/issueTemplates/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'name': None,
        'fieldTemplates': {},
        'queue': None,
    }


class CommentTemplates(Collection):
    path = '/{api_version}/commentTemplates/{id}'
    fields = {
        'id': None,
        'self': None,
        'version': None,
        'name': None,
        'description': None,
        'template': None,
        'summonees': [],
        'maillistSummonees': [],
        'queue': None,
    }


class Filters(Collection):
    path = '/{api_version}/filters/{id}'
    fields = {
        'id': None,
        'self': None,
        'name': None,
        'sorts': [],
        'filter': {},
        'query': None,
        'groupBy': None,
    }


class checklistItems(Collection):
    path = '/{api_version}/issues/{issue}/checklistItems/{id}'
    fields = {
        'id': None,
        'self': None,
        'text': None,
        'checked': False,
        'assignee': None,
        'deadline': None,
        'url': None,
        'checklistItemType': None
    }


    def create(self, text, checked=False, assignee=None, deadline=None, url=None, item_type=None):
        assert 'issue' in self._vars
        super(checklistItems, self).create(
            text=text,
            checked=checked,
            assignee=assignee,
            deadline=deadline,
            url=url,
            checklistItemType=item_type
        )
