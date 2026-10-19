from alembic import command

from tests.conftest import ALEMBIC_CFG


def test_models_match_migrations() -> None:
    """Fails (alembic raises) when a model changed without a new revision."""
    command.check(ALEMBIC_CFG)
