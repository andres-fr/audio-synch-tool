# CHANGELOG
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## v[1.2.2] ([diff](https://github.com/andres-fr/audio-synch-tool/compare/v1.2.0...v1.2.2))

### Changed:

* Now Mvn class refers to the package's MVNX validation schema by default, so now validation can be done by feeding `-v` instead of `-S <SCHEMA_PATH>`

## [1.2.1]

At this stage the following is implemented:

* Mvn class and schema to load and validate MVNX files
* Plotter base class with functionality to host multiple plots and multiple lines per plot
* Interaction: custom buttons and text prompts
* Two specific subclasses of the plotter: one for editing and one for checking signals. Subclasses extract the acceleration magnitude for both arms from the MVN by default.
* Editing class has functionality to provide 4 anchor points and export synched MVNX

## [0.5.0] - 24-Jun-2019

### Added:

* Dirst version of multiplotter
* Mvn loader dependencies


## [0.1.0]

Started dev



## TODO:

### high priority

### low priority
* Add useful info to plots
* abstract the accel.magnitude extraction from the plotter classes
