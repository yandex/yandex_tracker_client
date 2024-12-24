# coding: utf-8

from common.url import api_url


def test_entities_checklist_create(net_mock, client, fake_entity, mocked_fake_entity):
    data = {
        "text": "test_text",
        "checked": True,
        "assignee": "assigner",
        "deadline": {
            "date": "2021-05-09T00:00:00.000+0000",
            "deadlineType": "date"
        },
    }

    net_mock.post(
        api_url('/entities/{entity_type}/{idx}/checklistItems'.format(entity_type=fake_entity.entity_type,
                                                                      idx=fake_entity.idx)),
        json=fake_entity.json)

    mocked_fake_entity.checklist_items.create(**data)
    real_request = net_mock.request_history[1].json()

    assert real_request == data


def test_entities_checklist_delete(net_mock, client, fake_entity, mocked_fake_entity):
    net_mock.delete(
        api_url('/entities/{entity_type}/{idx}/checklistItems'.format(entity_type=fake_entity.entity_type,
                                                                      idx=fake_entity.idx)),
        status_code=204)

    mocked_fake_entity.checklist_items.delete()


def test_entities_checklist_update(net_mock, client, fake_entity, mocked_fake_entity):
    net_mock.patch(
        api_url('/entities/{entity_type}/{idx}/checklistItems'.format(entity_type=fake_entity.entity_type,
                                                                      idx=fake_entity.idx)),
        status_code=200)

    data = {
        "id": "123",
        "text": "1234"
    }

    mocked_fake_entity.checklist_items.update(data)
    real_request = net_mock.request_history[1].json()

    assert real_request == data


def test_entities_checklists_move_item(net_mock, client, fake_entity, mocked_fake_entity):
    before_item_id = 1
    item_id = 2

    net_mock.post(
        api_url(
            '/entities/{entity_type}/{idx}/checklistItems/{item_id}/_move'.format(entity_type=fake_entity.entity_type,
                                                                                  idx=fake_entity.idx,
                                                                                  item_id=item_id)),
        status_code=200)

    mocked_fake_entity.checklist_items.move_item(item_id=item_id, before=before_item_id)
    real_request = net_mock.request_history[1].json()

    assert real_request == {'before': before_item_id}


def test_entities_checklists_delete_item(net_mock, client, fake_entity, mocked_fake_entity):
    item_id = 1

    net_mock.delete(
        api_url('/entities/{entity_type}/{idx}/checklistItems/{item_id}'.format(entity_type=fake_entity.entity_type,
                                                                                idx=fake_entity.idx, item_id=item_id)),
        status_code=204)

    mocked_fake_entity.checklist_items.delete_item(item_id=item_id)
