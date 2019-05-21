# -*- coding:utf-8 -*-


r"""
| Main init file docstring.
| It exemplifies the usage of
  `restructured text
  <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_,
  like:

* 1 2 3 4
* *Italics*
* **Bold**
* Numbered and nested lists:
   #. This is a numbered list
   #. Nested lists have at least three characters indentation
* ``Inline literals``
* Parameter fields: see class and method docstrings.

| Note that lines above 80 characters would break ``flake8`` and
  therefore have to be wrapped. This can be achieved with ``|`` blocks.
| This is a new line.


#######################
Section about sections:
#######################

* Surrounding chars have to be at least as long as the title


No explicit hierarchy, but this recommended: ``#, *, =, -, ^, "``
(the first two with overline).


Subsection:
===========

| To exemplify the usage of :math:`\text{\LaTeX}` and nested quotes, nothing
  better than the words of Isaac Newton himself:

   "If I have seen further it is by standing on the shoulders of Giants."

Or, in other words:

.. math::

   \sum_{k=1}^{\infty} k = -\frac{1}{12}


Emphasis:
=========

.. note:: The sum of all parameters cannot exceed infinity

.. warning::
   If the sum of all parameters exceeds infinity, behaviour is undefined!


Function descriptions:
======================

Sphinx formatting:
------------------

.. function:: add(a, b=None)

   This is a cool function.

   :param a: a number
   :param b: another number
   :returns: ``a+b``. If b is none, returns ``a``
   :type a: int or float
   :type b: int, float or None
   :rtype: integer or float

   .. note:: Neither ``a`` nor ``b`` can be infinity!


Google formatting:
------------------

This function does something.

Args:
   name (str):  The name to use.

Kwargs:
   state (bool): Current state to be in.

Returns:
   int.  The return code::

      0 -- Success!
      1 -- No good.
      2 -- Try again.

Raises:
   AttributeError, KeyError

Usage example:

>>> print public_fn_with_googley_docstring(name='foo', state=None)
0

BTW, this always returns 0.  **NEVER** use with :class:`MyPublicClass`.



#################
Other structures:
#################

Field lists:

:Author:
    Homer J. Simpson
:Email: ``hjs@compuglobalhypermega.net``


Literal blocks, preceded by double colon::

   This is a literal block

   Markups are **not** rendered here.


Doctest blocks can be tested by the doc tool:

>>> [factorial(n) for n in range(6)]
[1, 1, 2, 6, 24, 120]
>>> [factorial(long(n)) for n in range(6)]
[1, 1, 2, 6, 24, 120]


Grid tables must be indented:
   +------------+------------+-----------+
   | Header 1   | Header 2   | Header 3  |
   +============+============+===========+
   | body row 1 | column 2   | column 3  |
   +------------+------------+-----------+
   | body row 2 | Cells may span columns.|
   +------------+------------+-----------+
   | body row 3 | Cells may  | - Cells   |
   +------------+ span rows. | - contain |
   | body row 4 |            | - blocks. |
   +------------+------------+-----------+


Simple table:

=====  =====  ======
   Inputs     Output
------------  ------
  A      B    A or B
=====  =====  ======
False  False  False
True   False  True
False  True   True
True   True   True
=====  =====  ======
"""


name = "dummypackage"
