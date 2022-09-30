from dataclasses import dataclass
from operator import methodcaller
from typing import Optional, ParamSpec, Tuple, TypeVar, Generic, Callable, Concatenate, overload
from edifice.components import plotting
import edifice as ed
from matplotlib.axes import Axes

T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class StateVar(Generic[T]):
    _prop_name: str
    _parent: ed.Component

    @property
    def value(self) -> T:
        return getattr(self._parent, self._prop_name)

    def set(self, value: T) -> T:
        self._parent.set_state(**{self._prop_name: value})
        return value

    def map(self, f: Callable[[T], T]) -> T:
        value = f(self.value)
        self.set(value)
        return value

    @property
    def as_tuple(self
    ) -> Tuple[T, Callable[[T], T], Callable[[Callable[[T], T]], T]]:
        value: T = self.value
        return (value, self.set, self.map)

@dataclass
class FunctionalComponentFunctions:
    parent_component: ed.Component
    first_call: bool = False
    _use_state_count: int = 0

    @overload
    def use_state(self, default: T, *, name: Optional[str] = None) -> StateVar[T]: ...
    
    @overload
    def use_state(self, *, get: Callable[[], T], name: Optional[str] = None) -> StateVar[T]: ...

    def use_state(self, *args: T, get: Optional[Callable[[], T]] = None, name: Optional[str] = None
    ) -> StateVar[T]:
        def get_default() -> T:
            if len(args) == 0 and get is not None:
                return get()
            if len(args) == 1 and get is None:
                return args[0]
            raise TypeError(
                "Either a single default argument or a getter function must be provided")

        name = f"state_{self._use_state_count}" if name is None else name
        parent = self.parent_component
        var = StateVar(name, parent)
        
        if not hasattr(parent, name):
            if not self.first_call:
                raise KeyError("Use called on an uninitialized state variable")
            setattr(parent, name, get_default())

        self._use_state_count += 1
        return var

Funs = FunctionalComponentFunctions
from frozendict import frozendict

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")
def function_component(render_func: Callable[Concatenate[Funs, P], R]
) -> ed.Component:
    class CustomComponent(ed.Component):
        def __init__(self, *args, **kwargs):
            self._first_render = True
            self.register_props(
                dict(args=args, kwargs=frozendict(kwargs)))
            super().__init__()
        
        def render(self):
            args = self.props.args
            kwargs = self.props.kwargs
            view = render_func(
                Funs(first_call=self._first_render, parent_component=self),
                *args, **kwargs)
            self._first_render = False
            return view

    CustomComponent.__name__ = render_func.__name__
    return CustomComponent


def ed_figure(
    plot_func: Callable[[Axes], None],
    *extras: Callable[[Axes], None] | str,
) -> plotting.Figure:
    def plot(ax: Axes):
        plot_func(ax)
        for func in extras:
            methodcaller(func)(ax) if isinstance(func, str) else func(ax)

    return plotting.Figure(plot)
