import pytest

from noscrapy.utils import PyQuery, attribute_mapper

def test_attribute_mapper_to_python():
    assert attribute_mapper.to_python('class') == 'class_'
    assert attribute_mapper.to_python('cls') == 'cls'
    assert attribute_mapper.to_python('data-foo') == 'data_foo'
    assert attribute_mapper.to_python('foo-') == 'foo'

def test_attr():
    pq = PyQuery('<img src="src" data-foo="foo" in="in">')
    assert pq.attr.src == 'src'
    assert pq.attr.data_foo == 'foo'
    assert pq.attr.in_ == 'in'
    del pq.attr.in_
    assert pq == PyQuery('<img src="src" data-foo="foo">')
    pq.attr.in_ = 'out'
    assert pq == PyQuery('<img src="src" data-foo="foo" in="out">')
    assert repr(pq.attr) == '<flexible_element _attr>'
    pq.attr(in_='in')
    assert pq == PyQuery('<img src="src" data-foo="foo" in="in">')
    with pytest.raises(ValueError):
        pq.attr()
    pq.attr.in_ = None
    assert pq == PyQuery('<img src="src" data-foo="foo">')
    pq.attr.src = ''
    assert pq == PyQuery('<img data-foo="foo">')

def test_eq():
    pq = PyQuery('<img src="src" alt="alt"/><a href="foo">bar</a>')
    assert pq == '<img src="src" alt="alt"/><a href="foo">bar</a>'
    assert pq == '<img alt="alt" src="src"/><a href="foo">bar</a>'
    assert pq != '<a href="foo">bar</a><img alt="alt" src="src"/>'
    assert pq != '<img src="src" alt="alt"/><a href="foo">foo</a>'
    assert pq != '<img alt="alt" src="src"/><a href="foo">bar</a>x'
    assert pq != '<img alt="alt" src="src"/><a href="foo">bar</a><br/>'

    pq = PyQuery('<p class="foo">a<img src="src"/>b</p>c<p class="bar">d<img src="other"/>e</p>')
    assert pq == pq
    assert pq == '<p class="foo">a<img src="src"/>b</p>c<p class="bar">d<img src="other"/>e</p>'
    assert pq != '<p class="foo">a<img src="src"/>b</p>c<p class="bar">d<img src="other"/>f</p>'
    assert pq != '<p class="bar">d<img src="other"/>e</p>c<p class="foo">a<img src="src"/>b</p>'
    assert pq != '<p class="foo">a<img src="src"/>b</p>'

    pq = PyQuery('<img src="src" alt="alt"/><img src="bar" data-noalt/>')('img')
    assert [a for a in dir(pq.attr) if not a.startswith('__')] == ['alt', 'data_noalt', 'src']
    assert pq != PyQuery('<img src="src" alt="alt"/><img data-noalt/>')('img')
    assert pq != PyQuery('<img src="src" alt="alt"/>')('img')
    assert pq != PyQuery('<img src="src" alt="alt"/><img src="bar" data-noalt>foo</img>')('img')
    assert pq != object()

def test_map_items():
    pq = PyQuery('<p><span>1</span></p><p><a>2</a></p><p>last</p>')
    result = pq.map_items(lambda item, index, count: None, 'p')
    assert result == []

    pq = PyQuery('<p><span>1</span></p><p><a>2</a><a>3</a></p>')
    result = pq.map_items(lambda item, index, count: list(item('a, span').items()), 'p')
    assert result == ['<span>1</span>', '<a>2</a>', '<a>3</a>']
