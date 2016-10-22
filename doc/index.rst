Testing for Sphinx-Rust
========================

.. code-block:: rust

	pub fn hello_world(x: i32) -> i64 {
		return x;
	}

.. rust:crate:: HelloCrate

.. rust:module:: HelloModule

.. rust:struct:: pub struct HelloStruct
	
	a struct yay

	.. rust:member:: hello_member: i32

		a member yay

.. rust:function:: fn hello_world(x: ExternalTest, y: i64) -> Good

	something about this function		
									
:rust:struct:`HelloStruct`


.. py:class:: Foo

	.. py:method:: test()

	.. py:attribute:: test_attribute

		this is a test attribute

:py:class:`Foo`



.. toctree::
  :maxdepth: 1

  External_Test

Indices and tables
==================
* :ref:`genindex`
* :ref:`search`
