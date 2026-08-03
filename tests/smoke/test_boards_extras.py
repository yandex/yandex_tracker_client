# coding: utf-8

from common.url import api_url


def _board():
    return {"self": api_url('/boards/10'), "id": "10", "version": 1,
            "name": "B"}


def test_suggest_boards(net_mock, client):
    net_mock.get(
        api_url('/boards/_suggest'),
        json=[
            {"self": api_url('/boards/1'), "id": "1", "name": "Board 1"},
            {"self": api_url('/boards/2'), "id": "2", "name": "Board 2"},
        ],
    )
    boards = client.boards.suggest('Board')
    assert [b.id for b in boards] == ["1", "2"]
    assert net_mock.last_request.method == 'GET'
    assert 'input' in net_mock.last_request.qs


def test_get_board_notes(net_mock, client):
    # List endpoint is /notes with no trailing slash; the response items carry
    # no `self`, so they come back as plain dicts, not resources.
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.get(
        api_url('/boards/10/notes'),
        json=[
            {"columnId": 100, "version": 1, "text": "hi"},
        ],
    )
    notes = board.notes.get_all()
    assert notes[0]["text"] == "hi"
    assert net_mock.last_request.path.endswith('/boards/10/notes')


def test_create_board_note(net_mock, client):
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.post(
        api_url('/boards/10/notes/100'),
        json={"columnId": 100, "version": 1, "text": "new"},
    )
    note = board.notes.create_for_column('100', text='new')
    assert note["text"] == "new"
    assert net_mock.last_request.json() == {"text": "new"}


def test_update_board_note(net_mock, client):
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.patch(
        api_url('/boards/10/notes/100'),
        json={"columnId": 100, "version": 2, "text": "upd"},
    )
    note = board.notes.update_for_column('100', text='upd')
    assert note["text"] == "upd"
    assert net_mock.last_request.json() == {"text": "upd"}


def test_delete_board_note(net_mock, client):
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.delete(api_url('/boards/10/notes/100'))
    board.notes.delete_for_column('100')
    assert net_mock.last_request.method == 'DELETE'
    assert net_mock.last_request.path.endswith('/boards/10/notes/100')


def test_add_board_quick_filter(net_mock, client):
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.post(
        api_url('/boards/10/quick-filters'),
        json={"self": api_url('/boards/10/quick-filters/5'), "id": "5",
              "name": "qf"},
    )
    qf = board.quick_filters.add('qf', query='Resolution: empty()')
    assert qf.name == "qf"
    assert net_mock.last_request.json() == {
        "name": "qf", "searchRequest": {"query": "Resolution: empty()"}}


def test_update_board_quick_filter(net_mock, client):
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.patch(
        api_url('/boards/10/quick-filters/5'),
        json={"self": api_url('/boards/10/quick-filters/5'), "id": "5",
              "name": "qf2"},
    )
    qf = board.quick_filters.update_filter(
        '5', name='qf2', query='Resolution: notEmpty()')
    assert qf.name == "qf2"
    assert net_mock.last_request.json() == {
        "name": "qf2", "searchRequest": {"query": "Resolution: notEmpty()"}}


def test_delete_board_quick_filter(net_mock, client):
    net_mock.get(api_url('/boards/10'), json=_board())
    board = client.boards['10']
    net_mock.delete(api_url('/boards/10/quick-filter/5'))
    board.quick_filters.delete_filter('5')
    assert net_mock.last_request.method == 'DELETE'
    assert net_mock.last_request.path.endswith('/boards/10/quick-filter/5')
