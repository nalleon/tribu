from functools import partial

from faker import Faker
from model_bakery.recipe import Recipe, foreign_key

fake = Faker()

user = Recipe(
    'auth.User',
    username=fake.user_name,
    first_name=fake.first_name,
    last_name=fake.last_name,
    email=fake.email,
    _fill_optional=True,
)

echo = Recipe(
    'echos.Echo',
    content=partial(fake.paragraph, nb_sentences=10),
    _fill_optional=True,
)

wave = Recipe(
    'waves.Wave',
    content=partial(fake.sentence, nb_words=15),
    _fill_optional=True,
)

profile = Recipe(
    'users.Profile',
    user=foreign_key(user),
    bio=partial(fake.text, max_nb_chars=200),
    avatar='path/to/default/avatar.jpg',
    _fill_optional=True,
)
