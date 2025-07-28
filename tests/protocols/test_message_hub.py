from protocols.utils.messaging import Message, MessageHub


def test_publish_invokes_callbacks():
    hub = MessageHub()
    received_a = []
    received_b = []

    def handler_a(msg: Message) -> None:
        received_a.append(msg)

    def handler_b(msg: Message) -> None:
        received_b.append(msg)

    hub.subscribe("task", handler_a)
    hub.subscribe("task", handler_b)

    msg_data_1 = {"foo": 1}
    msg_data_2 = {"bar": 2}

    hub.publish("task", msg_data_1)
    hub.publish("task", msg_data_2)

    assert len(received_a) == 2  # nosec B101
    assert len(received_b) == 2  # nosec B101
    for msg, expected in zip(received_a, [msg_data_1, msg_data_2]):
        assert isinstance(msg, Message)  # nosec B101
        assert msg.topic == "task"  # nosec B101
        assert msg.data == expected  # nosec B101


def test_unsubscribe_stops_callbacks():
    hub = MessageHub()
    received = []

    def handler(msg: Message) -> None:
        received.append(msg)

    hub.subscribe("task", handler)
    hub.publish("task", {"n": 1})

    hub.unsubscribe("task", handler)
    hub.publish("task", {"n": 2})

    assert len(received) == 1  # nosec B101
    assert received[0].data == {"n": 1}  # nosec B101


def test_get_messages_history_and_filtering():
    hub = MessageHub()
    hub.publish("a", {"n": 1})
    hub.publish("b", {"n": 2})
    hub.publish("a", {"n": 3})

    history = hub.get_messages()
    assert [m.topic for m in history] == ["a", "b", "a"]  # nosec B101

    a_msgs = hub.get_messages("a")
    assert len(a_msgs) == 2  # nosec B101
    assert all(m.topic == "a" for m in a_msgs)  # nosec B101
