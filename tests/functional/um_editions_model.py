
from functional import actions

from modules.um_editions.model import EditionDAO


class EditionsDAOTest(actions.TestBase):

    def test_create_and_get(self):
        EditionDAO.create(
            'madrid-02',
            'Madrid Febrero')
        edition = EditionDAO.get('madrid-02')
        self.assertEqual(edition.key, 'madrid-02')
        self.assertEqual(edition.name, 'Madrid Febrero')

    def test_name_change(self):
        edition = EditionDAO.create(
            'madrid-02',
            'Madrid Febrero')
        edition.name = "Madrid Marzo"
        EditionDAO.set(edition)

        edition = EditionDAO.get('madrid-02')
        self.assertEqual(edition.name, "Madrid Marzo")
