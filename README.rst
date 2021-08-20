yandex_tracker_client
=====================

**yandex_tracker_client** provides python interface to `Yandex.Tracker
v2 API <https://tech.yandex.com/connect/tracker/>`_.

Installation
------------

**yandex_tracker_client** could be installed by pip:

.. code:: bash

   pip install yandex_tracker_client

Configuring
-----------

The Yandex.Tracker API uses the OAuth 2.0 protocol for application
authorization. Applications use the OAuth 2.0 protocol to access Yandex
services on behalf of a user.
You can get your token `here <https://tech.yandex.com/connect/tracker/api/concepts/access-docpage/>`_.

Usage
-----

To use client you need to initialize client first:

.. code:: python

   from yandex_tracker_client import TrackerClient

   client = TrackerClient(token=<token>, org_id=<org_id>)

**Getting issue:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   print issue.deadline, issue.updatedAt

Handling 404 exceptions:

.. code:: python

   from yandex_tracker_client.exceptions import NotFound

   try:
       issue = client.issues['MYQUEUE-42']
   except NotFound:
       pass

**Creating issue:**
Full field list `here <https://tech.yandex.com/connect/tracker/api/concepts/issues/create-issue-docpage/>`_.
.. code:: python

   client.issues.create(
       queue='MYQUEUE',
       summary='API Test Issue',
       type={'name': 'Bug'},
       description='test description'
   )

**Updating issue:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   issue.update(summary='East or west, Yandex.Tracker is the best', priority='minor')

**Searching for issues:**

.. code:: python

   issues = client.issues.find('Queue: MYQUEUE Assignee: me()') #You can copy this query from ui tracker interface
   print [issue.key for issue in issues]

Using the 'filter' parameter possible to pass the parameters of the
filtering as a dictionary:

.. code:: python

   issues = client.issues.find(
       filter={'queue': 'MYQUEUE', 'assignee': 'me()', 'created': {'from': '2019-03-02'}},
       order=['update','-status', '+priority'],
       per_page=15
   )
   print [issue.key for issue in issues]

**Obtaining list of transitions:**

.. code:: python

   transitions = issue.transitions.get_all()
   for transition in transitions:
     print transition

**Executing transition:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   issue.transitions['close'].execute()

Executing transition with comment and resolution:

.. code:: python

   issue = client.issues['MYQUEUE-42']
   transition = issue.transitions['close']
   transition.execute(comment='Fixed', resolution='fixed')

**Queue info:**

.. code:: python

   queue = client.queues['MYQUEUE']

or:

.. code:: python

   queue = client.issues['MYQUEUE-42'].queue

**Queue list:**

.. code:: python

   queues = client.queues.get_all()[:3]

**List issue attachments:**

.. code:: python

   attachments = client.issues['MYQUEUE-42'].attachments

**Downloading attachments to specified directory:**

.. code:: python

   [attachment.download_to('some/path') for attachments in client.get_attachments('MYQUEUE-42')]

**Uploading an attachment**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   client.attachments.create('path/to/file')

**Deleting an attachment**

.. code:: python

   ATTACHMENTS_TO_DELETE = {'to_delete.txt', 'smth.jpeg'}
   issue = client.issues['MYQUEUE-42']
   for attach in issue.attachments:
       if attach.name in ATTACHMENTS_TO_DELETE:
           attach.delete()

or

.. code:: python

   client.attachments[42].delete()

**List issue comments:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   comments = list(issue.comments.get_all())[:3]

**Add comment:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   comment = issue.comments.create(text='Test Comment')

**Add comment with attachments:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   comment = issue.comments.create(text='Test comment', attachments=['path/to/file1', 'path/to/file2'])

**Update comment:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   comment = issue.comments[42]
   comment.update(text='New Text')

**Deleting a comment:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   comment = issue.comments[42]
   comment.delete()

**List issue links:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   links = issue.links

**Add link:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   link = issue.links.create(issue='TEST-42', relationship='relates')

**Deleting a link:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   link = issue.links[42]
   link.delete()

**Add remote link:**

.. code:: python

   issue = client.issues['MYQUEUE-42']
   link = issue.remotelinks.create(origin="ru.yandex.lunapark", key="MYQUEUE-42", relationship="relates")

Advanced Usage
--------------

**Bulk update:**

.. code:: python

   bulkchange = client.bulkchange.update(
       ['MYQUEUE-42', 'MYQUEUE-43', 'MYQUEUE-44'],
       priority='minor',
       tags={'add': ['minored']})
   print bulkchange.status
   bulkchange = bulkchange.wait()
   print bulkchange.status

**Bulk transition:**

.. code:: python

   bulkchange = client.bulkchange.transition(
       ['MYQUEUE-42', 'MYQUEUE-43'], 'need_info', priority='minor')
   bulkchange.wait()

**Bulk move:**

.. code:: python

   bulkchange = client.bulkchange.move(['MYQUEUE-42', 'MYQUEUE-43'], 'TEST')
   bulkchange.wait()

**Perform actions with objects**

Client allows to make arbitrary subqueries to entities, for example in
order to archive version you have to make request
``POST /v2/versions/<id>/_archive``

In order to support such separate subqueries exists method
perform_action, usage example:

::

   version = client.versions[60031]
   version.perform_action('_archive', 'post', ignore_empty_body=True)

Some of tracker api endpoints doesn't work correctly with blank (``{}``)
body, in this case you should pass ``ignore_empty_body=True`` to this
method.
If endpoint require list in body use ``list_data`` param
and just pass needed kwargs otherwise.

Examples
--------

**Change assignee in all tickets**

.. code:: python

   from yandex_tracker_client import TrackerClient

   client = TrackerClient(token=<token>, org_id=<org_id>)

   def sent_employee_to_vacation(assignee, replace_with):
       """
       :param assignee: login in Yandex.Tracker
       :type assignee: ``str``

       :param replace_with: login in Yandex.Tracker
       :type replace_with: ``str``

       :return: is operation was successful
       :rtype: ``bool``
       """
       issues_to_transfer = client.issues.find(filter={'queue': 'MYQUEUE', 'assignee': assignee})
       bulk_change = client.bulkchange.update(issues_to_transfer, assignee=replace_with)
       bulk_change.wait()

       if bulk_change.status == 'COMPLETED':
           log.info('Successfully change assignee in bulkchange {}'.format(bulk_change.id))
           for issue in issues_to_transfer:
               issue.comments.create('Your ticket will be processed by another employee - {}'.format(replace_with))
           successful = True
       else:
           log.error('Bulkchange operation {} failed'.format(bulk_change.id))
           successful = False

       return successful

**Create related issues**

.. code:: python

       def start_new_feature_creation_process(feature):
           feature_type = get_feature_type(feature)
           manager = get_manager_by_type(feature_type)
           # manager = 'manager_login'
           main_issue = client.issues.create(
               queue='MAINQUEUE',
               assignee=manager,
               summary='New feature request: {}'.format(feature),
               type={'name': 'Task'},
               description='New feature request arrived'
           )
           if feature_type.need_design:
               design_issue = client.issues.create(
                   queue='DESIGN',
                   summary='Feature "{}" design'.format(feature),
                   type={'name': 'Task'},
                   description='Need design for new feature, main task: {}'.format(main_issue.id)
               )
               main_issue.links.create(issue=design_issue.id, relationship='relates')

           if feature_type.add_followers:
               followers = get_followers(feature_type)
               # followers = ['my_login', 'someoneelse_login']
               main_issue.update(followers={'add': followers})

           if feature_type.need_testing:
               tester = get_random_tester()
               # tester = 'tester_login'
               main_issue.update(qa=tester)

           log.info('Successfully start new feature creation process')
           return main_issue.id

Run tests
---------

::

   ./run_tests.sh

