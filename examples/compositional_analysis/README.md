This folder contains examples demonstrating the usage of the new compositional analysis method of VerifAI from our RV'23 paper [Compositional Simulation-Based Analysis of AI-Based Autonomous Systems for Markovian Specifications](https://link.springer.com/content/pdf/10.1007/978-3-031-44267-4_10.pdf?pdf=inline%20link).

Currently, we only decompose the `Main` scenario of a given Scenic file into its sub-scenarios.
This gives more control to the programmer over the decompositions.
Specifically, both theoretically and practically, decomposing scenarios that are sequentially composed without any random choices, i.e., no `do choose ...` or `do shuffle ...` statements, does not provide any performance improvements.
Therefore, programmers should write all of their random choices over sub-scenarios in the `Main` scenario for performance improvements.
Similarly, if the programmer wants to compute interface specifications between two sub-scenarios, then they should compose these scenarios in the `Main` scenario as those sub-scenarios will be decomposed.

See the `newtonian` folder for a simple example for the usage of compositional analysis method.

This is still a prototype implementation so please email to [beyazit@berkeley.edu](mailto:beyazit@berkeley.edu) if you encounter any issues of if you have any feedback!
