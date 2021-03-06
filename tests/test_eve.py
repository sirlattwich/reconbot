import datetime
from unittest import TestCase
from unittest.mock import Mock
from reconbot.eve import Eve

class EveTest(TestCase):
    def setUp(self):
        self.db_mock = Mock()
        self.eve_api_mock = Mock()
        self.character_api_mock = Mock()
        self.eve = Eve(self.db_mock, self.eve_api_mock, self.character_api_mock)

        self.ccp_alliance = {
            'id': 434243723,
            'name': 'C C P Alliance'
        }

        self.ccp_corporation = {
            'id': 98356193,
            'name': 'C C P Alliance Holding',
            'alliance_id': 434243723
        }

        self.game_masters_corporation = {
            'id': 216121397,
            'name': 'Game Masters',
            'alliance_id': 434243723
        }

        self.ccp_falcon = {
            'id': 92532650,
            'name': 'CCP Falcon',
            'corp': self.ccp_corporation,
            'alliance': self.ccp_alliance
        }

        self.hed_gp = {
            'id': 30001161,
            'name': 'HED-GP',
            'region': 10000014
        }

        self.hed_gp_planet = {
            'id': 40073894,
            'name': 'HED-GP I',
            'system_id': self.hed_gp['id'],
        }

        self.hed_gp_moon = {
            'id': 40073896,
            'name': 'HED-GP II - Moon 1'
        }

        self.amarr_control_tower = {
            'id': 12235,
            'name': 'Amarr Control Tower'
        }


    def test_get_moon_by_id(self):
        moon = {
            'itemID': self.hed_gp_moon['id'],
            'itemName': self.hed_gp_moon['name']
        }
        self.db_mock.fetchone.return_value = moon
        self.assertEqual(
            self.eve.get_moon_by_id(moon['itemID']),
            {
                'id': moon['itemID'],
                'name': moon['itemName']
            }
        )
        self.assertEqual(self.db_mock.execute.call_args[0][1][0], moon['itemID'])
        self.assertTrue(self.db_mock.fetchone.called)

    def test_get_planet_by_id(self):
        planet = {
            'itemID': self.hed_gp_planet['id'],
            'itemName': self.hed_gp_planet['name'],
            'solarSystemID': self.hed_gp_planet['system_id'],
        }
        self.db_mock.fetchone.return_value = planet
        self.assertEqual(
            self.eve.get_planet_by_id(planet['itemID']),
            {
                'id': planet['itemID'],
                'name': planet['itemName'],
                'system_id': planet['solarSystemID']
            }
        )
        self.assertEqual(self.db_mock.execute.call_args[0][1][0], planet['itemID'])
        self.assertTrue(self.db_mock.fetchone.called)

    def test_get_system_by_id(self):
        system = {
            'itemID': self.hed_gp['id'],
            'itemName': self.hed_gp['name'],
        }
        self.db_mock.fetchone.return_value = system
        self.assertEqual(
            self.eve.get_system_by_id(system['itemID']),
            {
                'id': system['itemID'],
                'name': system['itemName']
            }
        )
        self.assertEqual(self.db_mock.execute.call_args[0][1][0], system['itemID'])
        self.assertTrue(self.db_mock.fetchone.called)

    def test_get_item_by_id(self):
        item = {
            'typeID': self.amarr_control_tower['id'],
            'typeName': self.amarr_control_tower['name']
        }
        self.db_mock.fetchone.return_value = item
        self.assertEqual(
            self.eve.get_item_by_id(item['typeID']),
            {
                'id': item['typeID'],
                'name': item['typeName']
            }
        )
        self.assertEqual(self.db_mock.execute.call_args[0][1][0], item['typeID'])
        self.assertTrue(self.db_mock.fetchone.called)

    def test_get_alliance_by_id(self):
        response_mock = Mock()
        response_mock.result = {
            self.ccp_alliance['id']: self.ccp_alliance['name']
        }
        self.eve_api_mock.character_names_from_ids.return_value = response_mock

        self.assertEqual(
            self.eve.get_alliance_name_by_id(self.ccp_alliance['id']),
            self.ccp_alliance['name']
        )
        self.eve_api_mock.character_names_from_ids.expect_called_once_with(
            self.ccp_alliance['id'])

    def test_get_corporation_by_id(self):
        response_mock = Mock()
        response_mock.result = {
            self.ccp_corporation['id']: self.ccp_corporation['name']
        }
        self.eve_api_mock.character_names_from_ids.return_value = response_mock

        self.assertEqual(
            self.eve.get_corporation_name_by_id(self.ccp_corporation['id']),
            self.ccp_corporation['name']
        )
        self.eve_api_mock.character_names_from_ids.expect_called_once_with(
            self.ccp_corporation['id'])

    def test_get_character_by_id(self):
        response_mock = Mock()
        response_mock.result = self.ccp_falcon
        self.eve_api_mock.affiliations_for_character.return_value = response_mock
        character = self.eve.get_character_by_id(self.ccp_falcon['id'])

        self.assertEqual(character['id'], self.ccp_falcon['id'])
        self.assertEqual(character['name'], self.ccp_falcon['name'])
        self.assertEqual(character['corp']['id'], self.ccp_falcon['corp']['id'])
        self.assertEqual(character['corp']['name'], self.ccp_falcon['corp']['name'])
        self.assertEqual(character['alliance']['id'], self.ccp_falcon['alliance']['id'])
        self.assertEqual(character['alliance']['name'], self.ccp_falcon['alliance']['name'])
        self.eve_api_mock.affiliations_for_character.expect_called_once_with(
            self.ccp_falcon['id'])

    def test_is_recent_notification(self):
        current_time = datetime.datetime.now().timestamp() - 1000

        self.assertTrue(
            self.eve.is_recent_notification(current_time, 3600))

        self.assertFalse(
            self.eve.is_recent_notification(current_time, 600))

    def test_get_new_notifications(self):
        current_time = datetime.datetime.now().timestamp()

        notifications = {
            1234567890: {
                'notification_id': 1234567890,
                'timestamp': current_time - 1000,
                'type_id': '100'
            },
            1234567891: {
                'notification_id': 1234567891,
                'timestamp': current_time - 2000,
                'type_id': '200'
            }
        };

        new_notifications = self.eve.get_new_notifications(notifications)
        self.assertEqual(len(new_notifications), 2)
        self.assertEqual(new_notifications[1234567890]['type_id'], '100')
        self.assertEqual(new_notifications[1234567891]['type_id'], '200')

        new_notifications = self.eve.get_new_notifications(notifications, 1500)
        self.assertEqual(len(new_notifications), 1)
        self.assertEqual(new_notifications[1234567890]['type_id'], '100')

    def test_get_notification_texts(self):
        current_time = datetime.datetime.now().timestamp()
        notifications = {
            1234567890: {
                'notification_id': 1234567890,
                'timestamp': current_time - 1000,
                'type_id': '100'
            },
            1234567891: {
                'notification_id': 1234567891,
                'timestamp': current_time - 2000,
                'type_id': '200'
            }
        };

        notification_texts_mock = Mock()
        notification_texts_mock.result = {
            1234567890: {
                'structureTypeID': self.amarr_control_tower['id']
            },
            1234567891: {
                'victimID': self.ccp_falcon['id']
            }
        }

        self.character_api_mock.notification_texts.expect_called_once_with(notifications)
        self.character_api_mock.notification_texts.return_value = notification_texts_mock

        notification_texts = self.eve.get_notification_texts(notifications)

        self.assertEqual(notification_texts[0]['notification_id'], 1234567891)
        self.assertEqual(notification_texts[0]['victimID'], self.ccp_falcon['id'])

        self.assertEqual(notification_texts[1]['notification_id'], 1234567890)
        self.assertEqual(notification_texts[1]['structureTypeID'], self.amarr_control_tower['id'])
