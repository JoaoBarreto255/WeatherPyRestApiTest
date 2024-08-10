import pytest

from internal.models import ModelTableNameFactory, Base


def test_model_table_name_factory__digest_name() -> None:
    """
    test private method "ModelTableNameFactory::__digest_name"
    """

    factory = ModelTableNameFactory()

    assert (
        "b74205508da5f5838c1f209e44c2be45"
        == factory._ModelTableNameFactory__digest_name("Este é um teste!")
    )

    assert (
        "b74205508da5f5838c1f209e44c2be45"
        == factory._ModelTableNameFactory__digest_name("Este é um teste!")
    )


def test_model_table_name_factory__call__() -> None:
    """
    test special method ModelTableNameFactory::__call__
    """

    factory = ModelTableNameFactory()

    class TestName:
        pass

    CLASSNAME = str(TestName)
    CLASSNAME_HASH = factory._ModelTableNameFactory__digest_name(CLASSNAME)
    assert CLASSNAME_HASH == factory(TestName)
    assert CLASSNAME_HASH == factory(TestName())


def test_base_table_name() -> None:
    """
    test class method Base::table_name
    """

    factory = ModelTableNameFactory()
    BASE_HASH = factory(Base)
    assert BASE_HASH == Base.table_name()


def test_base_db_index() -> None:
    """
    test class method Base::db_index
    """

    BASE_HASH = Base.table_name()
    assert f"{BASE_HASH}_0" == Base().db_index()
    assert f"{BASE_HASH}_1" == Base(index=1).db_index()
    assert f"{BASE_HASH}_100" == Base(index=100).db_index()
