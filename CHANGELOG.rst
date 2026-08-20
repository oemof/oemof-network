
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


0.5.1 (2025-11-03)
------------------

* Added EnergySystem.check() to check graph for sanity
* Updated build system from setup.py to "build" module
* Modified Node to allow building hierachical graphs
* create_nx_graph(...) now accepts Path objects
* Node access using `energy_system.node[label]` is no longer experimental
* EnergySystem.add(node) will now fail if node.label is already known

0.5.2 (2026-01-29)
------------------

* Nodes are now considered equal to their string representation
* EnergySystem.add(node) will now fail if a node with the same
  string representation is already known. (It turned out that just having
  different labels sometimes is not good enough.)

0.5.3
-----

* Properties "results", "timeindex", "timeincrement", and "temporal"
  of the class EnergySystem are now deprecated. They are not used (at least
  not at the level of oemof.network).
* Fixed passing references to the EnergySystem when adding Nodes as subnodes.
* The required python version is upped to 3.10. This prevents problems in
  environment creation and moves with the end-of-life-timeline of python 
  versions.
* Added new way to load EnergySystem instances:
  `EnergySystem.from_file(filename)`.
