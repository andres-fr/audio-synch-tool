# CHANGELOG
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Upcoming

### Added:

* Mvn sequence loadable as PyTorch tensors


## [0.5.0] - 24-Jun-2019

### Added:

* Dirst version of multiplotter
* Mvn loader dependencies


## [0.1.0]

Started dev



## TODO:


### high priority

* multi plotter debug: ticks with different samplerates dont work? DONE
* zooming doesnt have resolution when num_plots > 1 DONE

* create multi-multiplotter, which given lists of lists plots multiple lines per axis. DONE

* mvn: split vectors into per-sensor info, and plot in multi-multiplotter DONE


* mvn processing facilities:
  * Fix timestamp
  * Shift and stretch

### low priority
* replace all np dependencies with torch DONE
