# Module:   test_utils
# Date:     ...
# Author:   ...

'''test_utils

...
'''


from circuits import Event
from circuits.core import Value
from circuits.node.utils import dump_event, load_event, dump_value, load_value


class test(Event):
    '''test Event'''


def test_events():
    event = test(1, 2, 3, foo='bar')
    event.success = True
    event.failure = False
    event.test_meta = 1

    id = 1
    s = dump_event(event, id)
    event, id = load_event(s)

    assert hasattr(event, 'args')
    assert hasattr(event, 'kwargs')
    assert hasattr(event, 'success')
    assert hasattr(event, 'failure')
    assert hasattr(event, 'channels')
    assert hasattr(event, 'notify')
    assert hasattr(event, 'test_meta')


def test_values():
    value = Value()
    value.value = 'foo'
    value.errors = False
    value.node_call_id = 1

    x, id, errors = load_value(dump_value(value))

    assert value.value == x
    assert id == 1
    assert not errors
