import inspect


class InterfaceMeta(type):
    IGNORED_ATTRS = ["__module__", "__qualname__", "__annotations__", "__doc__"]

    def __new__(mcs, name, bases, attrs):
        base_interface = None
        is_interface = False
        for base in bases:
            if base is Interface:
                is_interface = True
            if base in Interface.__subclasses__():
                base_interface = base

        if is_interface:
            mcs._validate_interface_attributes(name, attrs)

        if base_interface:
            mcs._validate_implementation_attributes(name, base_interface, attrs)
            mcs._validate_implementation_methods(name, base_interface, attrs)

        return super().__new__(mcs, name, bases, attrs)

    @staticmethod
    def _validate_interface_attributes(name, attrs):
        for attr_name, attr_value in attrs.items():
            if attr_name not in InterfaceMeta.IGNORED_ATTRS:
                if attr_name in attrs.get("__annotations__", {}):
                    raise AttributeError(
                        f"Attribute '{name}.{attr_name}' cannot have an implementation "
                        f"in interface. Current implementation value is '{attr_value}'."
                    )
                if (callable(attr_value) and
                        inspect.getsourcelines(attr_value)[0][1].strip() not in ("pass", "...")):
                    raise AttributeError(
                        f"Method '{name}.{attr_name}' cannot have any implementation "
                        f"other than 'pass' or '...'"
                    )
                if isinstance(attr_value, property):
                    raise AttributeError(
                        f"Property '{name}.{attr_name}' is not allowed, "
                        f"since properties are not implemented yet."
                    )

    @staticmethod
    def _validate_implementation_attributes(name, base_interface, attrs):
        base_interface_annotations = base_interface.__annotations__
        for attr_name, attr_type in base_interface_annotations.items():
            if attr_name not in attrs:
                raise AttributeError(
                    f"{name} doesn't have the attribute '{attr_name}' "
                    f"of type {base_interface_annotations[attr_name]}, "
                    f"which is provided in its interface {base_interface.__name__}"
                )
            if not isinstance(attrs[attr_name], attr_type):
                raise TypeError(
                    f"Attribute '{attr_name}' of class {name} has wrong type. "
                    f"Type provided by the interface is {attr_type}. "
                    f"Type in the implementation is {type(attrs[attr_name])}."
                )

    @staticmethod
    def _validate_implementation_methods(name, base_interface, attrs):
        for method_name, method in vars(base_interface).items():
            if method_name not in InterfaceMeta.IGNORED_ATTRS:
                if method_name not in attrs:
                    attr_type = "method" if callable(method) else "property"
                    raise AttributeError(
                        f"{name} doesn't have the {attr_type} '{method_name}', "
                        f"which is provided in its interface {base_interface.__name__}"
                    )
                # print(print(inspect.getsourcelines(method)[0][1].strip()))


class InstanceError(Exception):
    pass


class Interface(metaclass=InterfaceMeta):
    def __new__(cls, *args, **kwargs):
        if cls in Interface.__subclasses__() or cls is Interface:
            raise InstanceError("Interface class or its subclasses cannot be instantiated.")
        return super().__new__(cls, *args, **kwargs)


class IClass(Interface):
    some_attr: int

    def new_method(self, value: int = 10, some: str = "some") -> int:
        pass


class ClassImpl(IClass):
    some_attr = 10

    def new_method(self, value: int = 10, some: str = "some") -> int:
        pass
