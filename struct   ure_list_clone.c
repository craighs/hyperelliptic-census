{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sage.structure.list_clone import ClonableElement\n        sage: class IntPair(ClonableElement):\n\n",
    "      def __init__(self, parent, x, y):\n\n",
    "          ClonableElement.__init__(self, parent=parent)\n\n",
    "          self._x = x\n\n",
    "          self._y = y\n\n",
    "          self.set_immutable()\n\n",
    "          self.check()\n\n",
    "      def _repr_(self):\n\n",
    "          return \\"(x=%s, y=%s)\\"%(self._x, self._y)\n\n",
    "      def check(self):\n\n",
    "          if self._x >= self._y:\n\n",
    "              raise ValueError(\\"Incorrectly ordered pair\\")\n\n",
    "      def get_x(self): return self._x\n\n",
    "      def get_y(self): return self._y\n\n",
    "      def set_x(self, v): self._require_mutable(); self._x = v\n\n",
    "      def set_y(self, v): self._require_mutable(); self._y = v\n\n    .. NOTE:: we don't need to define ``__copy__`` since it is properly\n       inherited from :class:`Element<sage.structure.element.Element>`.\n\n    We now demonstrate the behavior. Let's create an ``IntPair``::\n\n        sage: myParent = Parent()\n        sage: el = IntPair(myParent, 1, 3); el\n        (x=1, y=3)\n        sage: el.get_x()\n        1\n\n    Modifying it is forbidden::\n\n        sage: el.set_x(4)\n        Traceback (most recent call last):\n        ...\n        ValueError: object is immutable; please change a copy instead.\n\n    However, you can modify a mutable copy::\n\n        sage: with el.clone() as el1:\n\n",
    "      el1.set_x(2)\n        sage: [el, el1]\n        [(x=1, y=3), (x=2, y=3)]\n\n    We check that the original and the modified copy are in a proper immutable\n    state::\n\n        sage: e\"\"l.is_immutable(), el1.is_immutable()\n        (True, True)\n        sage: el1.set_x(4)\n        Traceback (most recent call last):\n        ...\n        ValueError: object is immutable; please change a copy instead.\n\n    A modification which doesn't restore the invariant `x < y` at the end is\n    illegal and raise an exception::\n\n        sage: with el.clone() as elc2:\n\n",
    "      elc2.set_x(5)\n        Traceback (most recent call last):\n        ...\n        ValueError: Incorrectly ordered pair\n    \")},\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sage.structure.list_clone import ClonableElement\n        sage: class IntPair(ClonableElement):\n\n",
    "      def __init__(self, parent, x, y):\n\n",
    "          ClonableElement.__init__(self, parent=parent)\n\n",
    "          self._x = x\n\n",
    "          self._y = y\n\n",
    "          self.set_immutable()\n\n",
    "          self.check()\n\n",
    "      def _repr_(self):\n\n",
    "          return \\"(x=%s, y=%s)\\"%(self._x, self._y)\n\n",
    "      def check(self):\n\n",
    "          if self._x >= self._y:\n\n",
    "              raise ValueError(\\"Incorrectly ordered pair\\")\n\n",
    "      def get_x(self): return self._x\n\n",
    "      def get_y(self): return self._y\n\n",
    "      def set_x(self, v): self._require_mutable(); self._x = v\n\n",
    "      def set_y(self, v): self._require_mutable(); self._y = v\n\n    .. NOTE:: we don't need to define ``__copy__`` since it is properly\n       inherited from :class:`Element<sage.structure.element.Element>`.\n\n    We now demonstrate the behavior. Let's create an ``IntPair``::\n\n        sage: myParent = Parent()\n        sage: el = IntPair(myParent, 1, 3); el\n        (x=1, y=3)\n        sage: el.get_x()\n        1\n\n    Modifying it is forbidden::\n\n        sage: el.set_x(4)\n        Traceback (most recent call last):\n        ...\n        ValueError: object is immutable; please change a copy instead.\n\n    However, you can modify a mutable copy::\n\n        sage: with el.clone() as el1:\n\n",
    "      el1.set_x(2)\n        sage: [el, el1]\n        [(x=1, y=3), (x=2, y=3)]\n\n    We check that the original and the modified copy are in a proper immutable\n    state::\n\n        sage: e\"\"l.is_immutable(), el1.is_immutable()\n        (True, True)\n        sage: el1.set_x(4)\n        Traceback (most recent call last):\n        ...\n        ValueError: object is immutable; please change a copy instead.\n\n    A modification which doesn't restore the invariant `x < y` at the end is\n    illegal and raise an exception::\n\n        sage: with el.clone() as elc2:\n\n",
    "      elc2.set_x(5)\n        Traceback (most recent call last):\n        ...\n        ValueError: Incorrectly ordered pair\n    \"), /*tp_doc*/\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": null,
   "metadata": {},
   "outputs": [],
   "source": [
    " "
   ]
  }
],
"metadata": {
 "kernelspec": {
  "display_name": "SageMath 10.6",
  "language": "sage",
  "name": "sagemath"
 },
 "language_info": {
  "codemirror_mode": {
   "name": "ipython",
   "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
