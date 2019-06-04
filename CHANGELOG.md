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

* PLAN: the whole integral GUI thing will take too much time. make 2 variants, one for edit and other for test:
  * Test variant: given a path to a WAV and an MVNX via CLI, loads the plot and allows inspection
  * Edit variant: First make an app that given a path to a WAV and MVNX via CLI, and 4 ints for the anchors, outputs an MVNX with the extra infos `(referred_wav, sample_idx_per_frame)`. Then the GUI loads the plots, allows for inspection and contains 4 int prompts for anchoring, which trigger the edit app.

* mvn processing facilities:
  * serialization DONE
  * Fix timestamp
  * Shift and stretch DONE (through set and get `audio_sample` field)


### low priority
* replace all np dependencies with torch DONE
