import pytest
from mock import call, patch

from noscrapy import Selector
from noscrapy.utils import Field, PyQuery


def test_selector_init():
    class OtherSelector(Selector):
        foo = Field(1)

    s = Selector()
    assert type(s) is Selector

    s = Selector(id='a')
    assert s.id == 'a'
    s = Selector({'id': 'a'})
    assert s.id == 'a'
    o = OtherSelector('a')
    s = Selector(o)
    assert s.id == 'a'
    assert s == o
    assert s is not o
    assert isinstance(s, OtherSelector)

    s = Selector({'id': 'a'}, id='b')
    assert s.id == 'b'
    s = Selector(o, id='b')
    assert s.id == 'b'
    assert s != o
    assert s is not o
    assert isinstance(s, OtherSelector)

    s = Selector(type='OtherSelector')
    assert type(s) is OtherSelector
    assert s.foo == 1
    s = Selector(type='OtherSelector', foo=2)
    assert s.foo == 2

    with pytest.raises(TypeError):
        class OtherSelector(Selector):  # @DuplicatedSignature
            pass

def test_setattr():
    s = Selector()
    with pytest.raises(AttributeError):
        s.foo = 1

def test_copy():
    s = Selector('a')
    c = s.copy()
    assert s == c
    assert s is not c

def test_selector_parents():
    s = Selector()
    assert s.has_parent('_root')
    s.remove_parent('_root')
    assert not s.has_parent('_root')
    s.remove_parent('_root')
    assert not s.has_parent('_root')
    s.parents.append('_root')
    s.parents.append('a')
    assert s.has_parent('a')
    s.rename_parent('a', 'b')
    assert s.parents == ['_root', 'b']
    s.rename_parent('_root', 'a')
    assert s.parents == ['a', 'b']
    # no raise on missed
    s.rename_parent('_root', 'a')


@patch.object(Selector, '_get_data')
def test_selector_get_data(inner_get_data_mock):
    inner_get_data_mock.return_value = iter([{'a': 'a'}])
    assert list(Selector(id='id', css='a').get_data('<a>a</a>')) == [{'a': 'a'}]

@patch.object(Selector, '_get_data')
@patch('noscrapy.selector.sleep')
def test_selector_get_data_delay(sleep_mock, inner_get_data_mock):
    inner_get_data_mock.return_value = iter([{'a': 'a'}])
    selector = Selector(id='a', css='a', delay=100)
    actual = list(selector.get_data('<a>a</a>'))
    assert sleep_mock.call_args_list == [call(100)]
    assert actual == [{'a': 'a'}]

def test_columns():
    assert Selector('id').columns == ('id',)

def test_selector_get_items():
    selector = Selector(id='a', css='a')
    assert list(selector.get_items('   ')) == []
    assert list(selector.get_items('')) == []
    assert list(selector.get_items(None)) == []
    assert list(selector.get_items('<a>a</a>')) == list(PyQuery('<a>a</a>').items())
    assert list(selector.get_items(PyQuery('<a>a</a>'))) == list(PyQuery('<a>a</a>').items())

    selector = Selector(id='a', css='a', many=False)
    assert list(selector.get_items(PyQuery('<a>a</a><a>b</b>'))
                ) == [list(PyQuery('<a>a</a>').items())[0]]

def test_selector_inner_get_data_has_to_be_implemented():
    with pytest.raises(NotImplementedError):
        list(Selector(id='id', css='a')._get_data('<a>test</a>'))

def test_selector_repr_only_shows_non_default_values():
    assert repr(Selector('a', css='b', many=True)) == "Selector('a', css='b')"

@patch.object(Selector, '_get_item_data')
def test_items_selector_inner_get_data(item_data_mock):
    selector = Selector('id', css='a')

    item_data_mock.return_value = iter([])
    assert list(selector.get_data('')) == [{'id': None}]

    item_data_mock.return_value = iter([{'id': 'text'}])
    assert list(selector.get_data('<a>text</a>')) == [{'id': 'text'}]


@patch.object(Selector, '_get_item_data')
def test_items_selector_inline_many(item_data_mock):
    class InliningSelector(Selector):
        inline_many = Field(True, ro=True)

    selector = InliningSelector('id', css='a')

    item_data_mock.return_value = iter([])
    assert list(selector.get_data('')) == [{'id': ()}]

    item_data_mock.return_value = iter([{'id': 'text'}])
    assert list(selector.get_data('<a>text</a>')) == [{'id': ({'id': 'text'},)}]


@patch.object(Selector, '_get_item_data')
def test_items_selector_regex(item_data_mock):
    selector = Selector('id', css='a', regex=r'[a-z]{4}')

    item_data_mock.return_value = iter([{'id': '1234'}])
    assert list(selector.get_data('<a>1234</a>')) == [{'id': None}]

    item_data_mock.return_value = iter([{'id': 'text'}])
    assert list(selector.get_data('<a>text</a>')) == [{'id': 'text'}]

def test_items_selector_get_item_data_has_to_be_implemented():
    with pytest.raises(NotImplementedError):
        list(Selector('id', css='a')._get_data('<a>test</a>'))
