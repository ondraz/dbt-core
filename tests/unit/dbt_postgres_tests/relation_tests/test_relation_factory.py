"""
Uses the following fixtures in `unit/dbt_postgres_tests/conftest.py`:
- `relation_factory`
- `materialized_view_ref`
"""

from dbt.contracts.relation import RelationType

from dbt.adapters.postgres.relation import models


def test_make_ref(materialized_view_ref):
    assert materialized_view_ref.name == "my_materialized_view"
    assert materialized_view_ref.schema_name == "my_schema"
    assert materialized_view_ref.database_name == "my_database"
    assert materialized_view_ref.type == "materialized_view"
    assert materialized_view_ref.can_be_renamed is True


def test_make_backup_ref(relation_factory, materialized_view_ref):
    backup_ref = relation_factory.make_backup_ref(materialized_view_ref)
    assert backup_ref.name == '"my_materialized_view__dbt_backup"'


def test_make_intermediate(relation_factory, materialized_view_ref):
    intermediate_relation = relation_factory.make_intermediate(materialized_view_ref)
    assert intermediate_relation.name == '"my_materialized_view__dbt_tmp"'


def test_make_from_describe_relation_results(
    relation_factory, materialized_view_describe_relation_results
):
    materialized_view = relation_factory.make_from_describe_relation_results(
        materialized_view_describe_relation_results, RelationType.MaterializedView
    )

    assert materialized_view.name == "my_materialized_view"
    assert materialized_view.schema_name == "my_schema"
    assert materialized_view.database_name == "my_database"
    assert materialized_view.query == "select 42 from meaning_of_life"

    index_1 = models.PostgresIndexRelation(
        column_names=frozenset({"id", "value"}),
        method=models.PostgresIndexMethod.hash,
        unique=False,
        render=models.PostgresRenderPolicy,
    )
    index_2 = models.PostgresIndexRelation(
        column_names=frozenset({"id"}),
        method=models.PostgresIndexMethod.btree,
        unique=True,
        render=models.PostgresRenderPolicy,
    )
    assert index_1 in materialized_view.indexes
    assert index_2 in materialized_view.indexes


def test_make_from_model_node(relation_factory, materialized_view_model_node):
    materialized_view = relation_factory.make_from_model_node(materialized_view_model_node)

    assert materialized_view.name == "my_materialized_view"
    assert materialized_view.schema_name == "my_schema"
    assert materialized_view.database_name == "my_database"
    assert materialized_view.query == "select 42 from meaning_of_life"

    index_1 = models.PostgresIndexRelation(
        column_names=frozenset({"id", "value"}),
        method=models.PostgresIndexMethod.hash,
        unique=False,
        render=models.PostgresRenderPolicy,
    )
    index_2 = models.PostgresIndexRelation(
        column_names=frozenset({"id"}),
        method=models.PostgresIndexMethod.btree,
        unique=True,
        render=models.PostgresRenderPolicy,
    )
    assert index_1 in materialized_view.indexes
    assert index_2 in materialized_view.indexes