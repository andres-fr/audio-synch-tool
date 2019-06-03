# CHANGELOG
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Upcoming

### Added:

* Mvn sequence loadable as PyTorch tensors
* Plotter now accepts explicit x axis input

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

* explicit x axis in plotter DONE

* Allow pseudo-shared axes with different formatters DONE

* Add widgets DONE

* Add multi-samplerate label support: right now different "samplerates" aren't really supported: we have to multiply the x axis and this ends up showing the wrong sample number on the x axis. Ideally, all samplerate/shared combinations are possible and accurate. right now the MVN signal is "adapted" to the audio freq. the buttons shift all the signals because they grab the "shared" listeners... this is also messy. need a plan to proceed further!

* mvn processing facilities:
  * serialization DONE
  * Fix timestamp
  * Shift and stretch


### low priority
* replace all np dependencies with torch DONE
