
Changelog
=========

0.4.0.dev0 (2020-04-01)
-----------------------

* First release on PyPI.


0.4.0 (2022-04-26)
------------------

* Improved imports
* Improved testing
* Explicitly defined API


0.5.0 (2024-01-12)
------------------

* Improved code quality
* Add Entity.custom_properties
* Simplify node access (experimental: energy_system.node[label])


0.5.1
-----

* Added EnergySystem.check() to check graph for sanity
* Updated build system from setup.py to "build" module
* Modified Node to allow building hierachical graphs
* create_nx_graph(...) now accepts Path objects
* Node access using `energy_system.node[label]` is no longer experimental
* EnergySystem.add(node) will now fail if node.label is already known
