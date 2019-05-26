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

* BUGFIX: shared axes share timestamps, but they should depend on the samplerate and x value only.
  * Tried to use a custom formatter that looks into the axis, and add the samplerate attribute to the axis. But since multiple axes share the SAME xaxis, the xaxis->axes pointer points to the same axes, no matter where the signal comes from.
  * Going up the tree extending classes to pass down the signal seems very cumbersome in comparison to the following method:
  * Extend our xlim_changed callback to not only re-downsample but also do the job of the "shared" thing: update x limits for all shared (and individually instantiated) xaxes. The only problem could be side effects, so check if this makes sense


* mvn processing facilities:
  * Fix timestamp
  * Shift and stretch

### low priority
* replace all np dependencies with torch DONE
