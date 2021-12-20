import typing as t


class JsonModel:
    def json(self, attrs: t.Set[str]) -> t.Dict[str, t.Any]:
        data = {}
        for attr in attrs:
            value = getattr(self, attr)
            if value:
                if isinstance(value, JsonModel):
                    data[attr] = value.json()  # type: ignore[call-arg]
                elif isinstance(value, list):
                    data[attr] = [  # type: ignore[assignment]
                        element if not isinstance(value, JsonModel) else element.json()
                        for element in value
                    ]
                else:
                    data[attr] = value
        return data
