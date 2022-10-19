from proto import Message, MapField, UINT32

class Dictionary(Message):
    pairs = MapField(UINT32, UINT32, number=1)