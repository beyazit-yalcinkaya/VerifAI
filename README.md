This is a fork of [VerifAI](https://github.com/berkeleyLearnVerify/verifAI/). The repository contains two prototype extensions to VerifAI. Once these extensions reach a stable performance, this fork will be merged with the original VerifAI repository. The repository extends VerifAI for the compositional falsification and statistical verification of Scenic scenarios, reducing analysis time by leveraging compositional structure of scenarios. This extension is based on our RV'23 paper [Compositional Simulation-Based Analysis of AI-Based Autonomous Systems for Markovian Specifications](https://link.springer.com/content/pdf/10.1007/978-3-031-44267-4_10.pdf?pdf=inline%20link). See our [examples](examples/compositional_analysis/) for using the compositional analysis method!

<!--The extensions implemented in this repository are listed below.
-->
<!--* The repository contains a statistical verifier, enhancing capabilities of VerifAI beyond falsification. As of right now, the verifier can only be used with static sampling strategies. See our [example](examples/smc/) for using the statistical verifier.
* It also extends VerifAI for the compositional falsification and statistical verification of Scenic scenarios, reducing analysis time by leveraging compositional structure of scenarios. This extension is based on our RV'23 paper [Compositional Simulation-Based Analysis of AI-Based Autonomous Systems for Markovian Specifications](https://link.springer.com/content/pdf/10.1007/978-3-031-44267-4_10.pdf?pdf=inline%20link). See our [example](examples/compositional_analysis/) for using the compositional analysis feature.-->

----

[![Documentation Status](https://readthedocs.org/projects/verifai/badge/?version=latest)](https://verifai.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)


# VerifAI

**VerifAI** is a software toolkit for the formal design and analysis of 
systems that include artificial intelligence (AI) and machine learning (ML)
components.
VerifAI particularly seeks to address challenges with applying formal methods to perception and ML components, including those based on neural networks, and to model and analyze system behavior in the presence of environment uncertainty.
The current version of the toolkit performs intelligent simulation guided by formal models and specifications, enabling a variety of use cases including temporal-logic falsification (bug-finding), model-based systematic fuzz testing, parameter synthesis, counterexample analysis, and data set augmentation. Further details may be found in our [CAV 2019 paper](https://people.eecs.berkeley.edu/~sseshia/pubs/b2hd-verifai-cav19.html).

Please see the [documentation](https://verifai.readthedocs.io/) for installation instructions, tutorials, publications using VerifAI, and more.

VerifAI was designed and implemented by Tommaso Dreossi, Daniel J. Fremont, Shromona Ghosh, Edward Kim, Hadi Ravanbakhsh, Marcell Vazquez-Chanlatte, and Sanjit A. Seshia. 

If you use VerifAI in your work, please cite our [CAV 2019 paper](https://people.eecs.berkeley.edu/~sseshia/pubs/b2hd-verifai-cav19.html) and this website.

If you have any problems using VerifAI, please submit an issue to the GitHub repository or contact Daniel Fremont at [dfremont@ucsc.edu](mailto:dfremont@ucsc.edu) or Edward Kim at [ek65@berkeley.edu](mailto:ek65@berkeley.edu).

### Repository Structure

* _docs_: sources for the [documentation](https://verifai.readthedocs.io/);

* _examples_: examples and additional documentation for particular simulators, including CARLA, Webots, X-Plane, and OpenAI Gym;

* _src/verifai_: the source for the `verifai` package proper;

* _tests_: the VerifAI test suite.
